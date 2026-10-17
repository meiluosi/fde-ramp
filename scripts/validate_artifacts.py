#!/usr/bin/env python3
"""Validate a ramp/ workspace.

Usage:
  python3 scripts/validate_artifacts.py --root ramp [--strict]

Exit codes: 0 = ok (warnings allowed), 1 = errors.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED = [
    "plan.md",
    "state.json",
    "sources.jsonl",
    "sources.md",
    "value-chain.md",
    "value-chain.mmd",
    "chain.md",
    "chain.mmd",
    "domains.md",
    "activities.md",
    "glossary.md",
    "flow.md",
    "flow.mmd",
    "verification-list.md",
    "corrections.md",
    "open-questions.md",
    "brief.md",
    "readiness.md",
    "drill-scorecard.md",
    "calibration-log.md",
]

SOURCE_RE = re.compile(r"\[S(\d+)\]")
REF_BRACKET = re.compile(r"\[([^\]]*S\d+[^\]]*)\]")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CORRECTION_HEAD = re.compile(r"^##\s*修正\s*(\d+)", re.MULTILINE)
STATUSES = {"verified", "public", "needs-customer", "unsure"}
TIERS = {"A", "B", "C", "D"}


def cells_of(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(set(c) <= {"-", ":", " "} for c in cells if c)


def load_sources(path: Path, errors: list[str]) -> list[dict]:
    rows: list[dict] = []
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return rows
    for i, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"sources.jsonl:{i}: invalid JSON ({exc.msg})")
            continue
        missing = [k for k in ("id", "title", "url", "published", "accessed", "tier") if not obj.get(k)]
        if missing:
            errors.append(f"sources.jsonl:{i}: missing {', '.join(missing)}")
        if obj.get("tier") not in TIERS:
            errors.append(f"sources.jsonl:{i}: tier must be A/B/C/D, got {obj.get('tier')!r}")
        accessed = str(obj.get("accessed", ""))
        if accessed and not DATE_RE.match(accessed):
            errors.append(f"sources.jsonl:{i}: accessed must be YYYY-MM-DD, got {accessed!r}")
        used_for = obj.get("usedFor")
        if used_for is not None and not isinstance(used_for, (str, list)):
            errors.append(f"sources.jsonl:{i}: usedFor must be a string or list")
        rows.append(obj)
    ids = [str(r.get("id", "")) for r in rows]
    dup = {x for x in ids if ids.count(x) > 1}
    if dup:
        errors.append(f"sources.jsonl: duplicate ids {sorted(dup)}")
    return rows


def load_sources_quiet(path: Path) -> list[dict]:
    """Best-effort sources loader for readiness counting (no error reporting)."""
    rows: list[dict] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def glossary_count(text: str) -> tuple[int, dict[str, int]]:
    """Count term rows and status cells in markdown glossary tables.

    A term row carries exactly one status cell and at least 6 columns.
    This deliberately skips the '状态统计' summary table and '易混对' tables.
    """
    terms = 0
    counts = {s: 0 for s in STATUSES}
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = cells_of(line)
        if len(cells) < 6 or is_separator(cells):
            continue
        first = cells[0].lower()
        if not first or first in {"term", "#", "术语"}:
            continue
        hits = [c.lower() for c in cells if c.lower() in STATUSES]
        if len(hits) != 1:
            continue
        terms += 1
        counts[hits[0]] += 1
    return terms, counts


def verification_count(text: str) -> int:
    """Count verification rows whose 'item' cell (second column) is filled."""
    n = 0
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = cells_of(line)
        if len(cells) < 3 or is_separator(cells):
            continue
        if not re.fullmatch(r"(?:V)?\d+", cells[0]):
            continue
        if cells[1]:
            n += 1
    return n


def flow_guess_count(text: str) -> int:
    """Count ❓ rows in node-confidence tables only.

    A node-confidence table's header contains 信心 and starts with #/节点/环节;
    verification-candidate tables (待验证/谁会知道) are excluded on purpose.
    """
    n = 0
    for header, rows in _iter_tables(text):
        if not any("信心" in h for h in header):
            continue
        if any(("待验证点" in h or "谁会知道" in h) for h in header):
            continue
        first = header[0] if header else ""
        if first not in {"#", "节点", "环节"}:
            continue
        for cells in rows:
            if any(re.fullmatch(r"[❓\s]+", c) for c in cells):
                n += 1
    return n


def _has_value_after_label(body: str, label: str) -> bool:
    """True when label: has a value on the same line or in following indented lines."""
    lines = body.splitlines()
    for idx, line in enumerate(lines):
        pos = line.find(label)
        if pos < 0:
            continue
        rest = line[pos + len(label):].strip()
        if rest:
            return True
        for follow in lines[idx + 1:]:
            stripped = follow.strip()
            if not stripped:
                continue
            if stripped.startswith(("-", "#", "|")):
                break
            return True
    return False


def _iter_tables(text: str):
    """Yield (header_cells, data_rows) for each markdown table."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("|") and i + 1 < len(lines) and is_separator(cells_of(lines[i + 1])):
            header = [c.lower() for c in cells_of(line)]
            rows: list[list[str]] = []
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = cells_of(lines[i])
                i += 1
                if is_separator(cells):
                    continue
                rows.append(cells)
            yield header, rows
        else:
            i += 1


def count_rows_by_header(
    text: str, keywords: list[str], min_cols: int, content_idx: int = 0
) -> int:
    """Count non-empty rows in tables whose header contains every keyword."""
    total = 0
    for header, rows in _iter_tables(text):
        if not all(any(k.lower() in h for h in header) for k in keywords):
            continue
        for cells in rows:
            if len(cells) >= min_cols and len(cells) > content_idx and cells[content_idx]:
                total += 1
    return total


def domains_count(text: str) -> int:
    """Count filled business-domain rows: header has 业务域+目标, domain name non-empty."""
    return count_rows_by_header(text, ["业务域", "目标"], min_cols=5, content_idx=1)


def activities_count(text: str) -> int:
    """Count filled activity rows: header has 业务域+环节, step/activity non-empty."""
    return count_rows_by_header(text, ["业务域", "环节"], min_cols=8, content_idx=2)


def chain_counts(text: str) -> tuple[int, int]:
    """Return (players, relations) counted from header-matched tables in chain.md."""
    players = count_rows_by_header(text, ["玩家", "现状"], min_cols=5, content_idx=0)
    relations = count_rows_by_header(text, ["from", "关系类型"], min_cols=5, content_idx=0)
    return players, relations


def correction_count(text: str) -> int:
    """Count '## 修正 N' sections that have non-empty 我原以为/实际 content."""
    n = 0
    parts = re.split(CORRECTION_HEAD, text)
    for i in range(1, len(parts), 2):
        body = parts[i + 1] if i + 1 < len(parts) else ""
        if _has_value_after_label(body, "实际：") or _has_value_after_label(body, "我原以为："):
            n += 1
    return n


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ramp artifacts")
    parser.add_argument("--root", default="ramp")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2

    for name in REQUIRED:
        if not (root / name).exists():
            errors.append(f"missing required file: {name}")

    if errors:
        for e in errors:
            print("ERROR:", e)
        return 1

    try:
        state = json.loads((root / "state.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: state.json: invalid JSON ({exc.msg})")
        return 1

    for dim, score in (state.get("dimensions") or {}).items():
        if not isinstance(score, int) or not 0 <= score <= 4:
            errors.append(f"state.dimensions.{dim}: must be int 0-4, got {score!r}")

    sources = load_sources(root / "sources.jsonl", errors)
    source_ids = {str(r.get("id")) for r in sources}
    sources_md = (root / "sources.md").read_text(encoding="utf-8") if (root / "sources.md").exists() else ""
    missing_in_sources_md = sorted(sid for sid in source_ids if sid and sid not in sources_md)
    if missing_in_sources_md:
        warnings.append(f"sources.md: missing {len(missing_in_sources_md)} source id(s), run scripts/render_sources.py")

    for md in sorted(root.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        if "{{" in text:
            errors.append(f"{md.relative_to(root)}: unreplaced template placeholder '{{{{'")
        # ignore examples inside fenced code blocks and inline code spans
        scan = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        scan = re.sub(r"`[^`]*`", "", scan)
        for inner in REF_BRACKET.findall(scan):
            inner = inner.strip()
            # accept [S3] and merged forms [S03/S04], [S13、S14], [S1, S2]
            if not re.fullmatch(r"S\d+(?:\s*[/、,]\s*S?\d+)*", inner):
                continue
            for num in re.findall(r"\d+", inner):
                if f"S{num}" not in source_ids:
                    errors.append(f"{md.relative_to(root)}: unknown source ref [S{num}]")

    glossary = (root / "glossary.md").read_text(encoding="utf-8")
    terms, status_counts = glossary_count(glossary)
    if terms < 20:
        warnings.append(f"glossary: only {terms} term rows (target >=20, final ~50)")
    if sum(status_counts.values()) == 0:
        warnings.append("glossary: no status cells (verified/public/needs-customer/unsure)")

    verification = (root / "verification-list.md").read_text(encoding="utf-8")
    v_items = verification_count(verification)
    if v_items < 5:
        warnings.append(f"verification-list: only {v_items} filled items (target >=5)")

    flow = (root / "flow.md").read_text(encoding="utf-8")
    q = flow_guess_count(flow)
    if q < 5:
        warnings.append(f"flow: only {q} guessed node rows '❓' (target >=5)")

    corrections = (root / "corrections.md").read_text(encoding="utf-8")
    corr = correction_count(corrections)

    domains = (root / "domains.md").read_text(encoding="utf-8")
    d_count = domains_count(domains)
    activities = (root / "activities.md").read_text(encoding="utf-8")
    a_count = activities_count(activities)
    chain = (root / "chain.md").read_text(encoding="utf-8")
    p_count, r_count = chain_counts(chain)
    if p_count < 10:
        warnings.append(f"chain: only {p_count} filled players (target >=10)")
    if r_count < 5:
        warnings.append(f"chain: only {r_count} filled relations (target >=5)")
    if d_count < 3:
        warnings.append(f"domains: only {d_count} filled business domains (target >=3)")
    if a_count < 15:
        warnings.append(f"activities: only {a_count} filled activity rows (target >=15)")
    if corr < 5:
        warnings.append(f"corrections: only {corr} filled corrections (Block 4 target >=5)")

    if (state.get("blocks") or {}).get("negate") == "done" and corr < 5:
        warnings.append("state.blocks.negate=done but corrections.md has <5 filled corrections")

    counts = state.get("counts") or {}
    if counts.get("sources") != len(sources):
        warnings.append(f"state.counts.sources={counts.get('sources')} but sources.jsonl has {len(sources)}")
    if counts.get("terms") != terms:
        warnings.append(f"state.counts.terms={counts.get('terms')} but glossary has {terms}")
    if counts.get("verification_items") != v_items:
        warnings.append(
            f"state.counts.verification_items={counts.get('verification_items')} but list has {v_items}"
        )
    if counts.get("corrections") != corr:
        warnings.append(f"state.counts.corrections={counts.get('corrections')} but corrections.md has {corr}")
    for key, value in (("players", p_count), ("relations", r_count), ("domains", d_count), ("activities", a_count)):
        if counts.get(key) != value:
            warnings.append(f"state.counts.{key}={counts.get(key)} but files have {value}")

    print(f"root: {root}")
    print(
        f"sources: {len(sources)}  terms: {terms}  verification: {v_items}  corrections: {corr}  guessed nodes: {q}"
    )
    print(f"chain players: {p_count}  relations: {r_count}  domains: {d_count}  activities: {a_count}")
    print(f"glossary statuses: {status_counts}")
    for w in warnings:
        print("WARN:", w)
    for e in errors:
        print("ERROR:", e)

    if errors or (args.strict and warnings):
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
