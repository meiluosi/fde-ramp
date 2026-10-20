#!/usr/bin/env python3
"""Score and update FDE conversation readiness.

Usage:
  python3 scripts/readiness.py --root ramp
  python3 scripts/readiness.py --root ramp --set structure=3 --set language=2
  python3 scripts/readiness.py --root ramp --check   # exit 1 if not ready

Target: all five dimensions >= 3.
Gate:   min(dim) >= 2, avg >= 3, structure >= 3, language >= 3,
        AND evidence: >=5 filled corrections (Block 4), >=8 sources,
        >=20 glossary term rows, >=5 verification items.
Self-reported scores alone can never pass.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_artifacts import (  # noqa: E402
    activities_count,
    chain_counts,
    correction_count,
    domains_count,
    glossary_count,
    load_sources_quiet,
    verification_count,
)

DIMS = ["structure", "language", "players", "decision", "dialogue"]
LABELS = {
    "structure": "结构 Structure",
    "language": "语言 Language",
    "players": "玩家 Players",
    "decision": "决策 Decision",
    "dialogue": "对话 Dialogue",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Readiness score")
    parser.add_argument("--root", default="ramp")
    parser.add_argument("--set", action="append", default=[], metavar="DIM=SCORE")
    parser.add_argument("--check", action="store_true", help="exit 1 when not ready")
    parser.add_argument("--no-write", action="store_true", help="do not update state.json")
    parser.add_argument("--client", action="store_true", help="require client-ready evidence (real interviews, verified terms, provenance)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    state_path = root / "state.json"
    if not state_path.exists():
        print(f"missing {state_path}", file=sys.stderr)
        return 2
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: state.json: invalid JSON ({exc.msg})", file=sys.stderr)
        return 2
    dims = state.setdefault("dimensions", {})

    for item in args.set:
        if "=" not in item:
            print(f"bad --set {item!r}, expected DIM=SCORE", file=sys.stderr)
            return 2
        key, raw = item.split("=", 1)
        key = key.strip().lower()
        if key not in DIMS:
            print(f"unknown dimension {key!r}; choose from {DIMS}", file=sys.stderr)
            return 2
        try:
            value = int(raw)
        except ValueError:
            print(f"score must be an integer: {raw!r}", file=sys.stderr)
            return 2
        if not 0 <= value <= 4:
            print(f"score must be 0-4: {value}", file=sys.stderr)
            return 2
        dims[key] = value

    scores = {d: int(dims.get(d, 0)) for d in DIMS}
    avg = sum(scores.values()) / len(DIMS)
    lowest = min(scores.values())

    # ---- evidence gate ----
    sources = load_sources_quiet(root / "sources.jsonl")
    glossary_text = (root / "glossary.md").read_text(encoding="utf-8") if (root / "glossary.md").exists() else ""
    verification_text = (
        (root / "verification-list.md").read_text(encoding="utf-8")
        if (root / "verification-list.md").exists()
        else ""
    )
    corrections_text = (
        (root / "verification-list.md").read_text(encoding="utf-8") if (root / "verification-list.md").exists() else ""
    )
    chain_text = (root / "chain.md").read_text(encoding="utf-8") if (root / "chain.md").exists() else ""
    business_text = (root / "business.md").read_text(encoding="utf-8") if (root / "business.md").exists() else ""
    domains_text = business_text
    activities_text = business_text
    terms, status_counts = glossary_count(glossary_text)
    v_items = verification_count(verification_text)
    corrections = correction_count(corrections_text)
    players, relations = chain_counts(chain_text)
    d_count = domains_count(domains_text)
    a_count = activities_count(activities_text)
    negate_done = (state.get("blocks") or {}).get("negate") == "done"

    # ---- client-ready checks (opt-in) ----
    mode = state.get("mode", "explore")
    decision_text = (root / "decision-brief.md").read_text(encoding="utf-8") if (root / "decision-brief.md").exists() else ""
    verified_terms = status_counts.get("verified", 0)
    tiers = {}
    for row in sources:
        tier = str(row.get("tier", "")).upper()
        tiers[tier] = tiers.get(tier, 0) + 1
    ab = tiers.get("A", 0) + tiers.get("B", 0)
    ab_share = ab / len(sources) if sources else 0
    simulated = any(marker in corrections_text for marker in ("模拟", "虚构"))
    provenance = state.get("provenance") or {}
    client_checks = [
        ("state.mode == 'client-ready'", mode == "client-ready"),
        ("decision-brief 已填", "决策" in decision_text and "拍板人" in decision_text and "{{" not in decision_text),
        ("修正记录非模拟/虚构", not simulated),
        ("verified 术语 ≥3", verified_terms >= 3),
        ("A/B 级来源 ≥5 且占比 ≥50%", ab >= 5 and ab_share >= 0.5),
        ("provenance.evidence == 'customer'", provenance.get("evidence") == "customer"),
        ("provenance.reviewedBy 非空", bool(str(provenance.get("reviewedBy", "")).strip())),
    ]
    client_ok = all(ok for _, ok in client_checks)

    checks = [
        ("修正记录 ≥5", corrections, 5),
        ("来源 ≥8", len(sources), 8),
        ("术语 ≥20", terms, 20),
        ("待验证 ≥5", v_items, 5),
        ("链路玩家 ≥10", players, 10),
        ("链路关系 ≥5", relations, 5),
        ("业务域 ≥3", d_count, 3),
        ("活动行 ≥10", a_count, 10),
    ]
    evidence_ok = all(value >= need for _, value, need in checks) and negate_done

    print(f"{'dimension':<20} score")
    for d in DIMS:
        print(f"{LABELS[d]:<20} {scores[d]}")
    print(f"{'average':<20} {avg:.2f}")
    print(f"{'lowest':<20} {lowest}")
    print()
    print("evidence:")
    for label, value, need in checks:
        print(f"  {label}: {value}" + ("" if value >= need else f"  (need >= {need})"))
    print(f"  state.blocks.negate == 'done': {negate_done}")
    if args.client:
        print("client-ready:")
        for label, ok in client_checks:
            print(f"  {'✅' if ok else '❌'} {label}")

    dims_ok = lowest >= 2 and avg >= 3 and scores["structure"] >= 3 and scores["language"] >= 3
    gate = dims_ok and evidence_ok and (client_ok if args.client else True)

    print()
    print("target: all five dimensions >= 3")
    print("gate:   min>=2, avg>=3, structure>=3, language>=3, AND evidence checks above")
    if gate:
        print("gate: PASS")
    else:
        print("gate: FAIL")
        if not dims_ok:
            weak = [LABELS[d] for d in DIMS if scores[d] < 2]
            if weak:
                print("  blocking dimension (<2): " + ", ".join(weak))
            else:
                print("  next: raise the lowest dimension / structure / language and re-check")
        if not negate_done:
            print("  missing: Block 4 not marked done (state.blocks.negate != 'done')")
        if corrections < 5:
            print(f"  missing: only {corrections} filled corrections in verification-list.md (need >=5)")
        for label, value, need in checks:
            if value < need:
                print(f"  missing: {label} is {value} (need >={need})")
        if args.client:
            for label, ok in client_checks:
                if not ok:
                    print(f"  client missing: {label}")

    counts = state.setdefault("counts", {})
    counts.update(
        {
            "sources": len(sources),
            "terms": terms,
            "verification_items": v_items,
            "corrections": corrections,
            "players": players,
            "relations": relations,
            "domains": d_count,
            "activities": a_count,
        }
    )
    if not args.no_write:
        state["dimensions"] = scores
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"updated {state_path}")

    if args.check and not gate:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
