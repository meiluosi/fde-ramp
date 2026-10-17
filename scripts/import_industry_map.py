#!/usr/bin/env python3
"""Import a dsh-industry-research chain.json into a ramp workspace seed.

Writes (does not overwrite chain.md):
  <out-dir>/chain-seed.md      human-readable segment/metrics/edges + merge notes
  <out-dir>/chain-seed.mmd     mermaid graph
  <out-dir>/sources-imported.jsonl  converted source registry (when --sources given)

Usage:
  python3 scripts/import_industry_map.py --chain /path/industry-research/煤层气/chain.json \
      --sources /path/industry-research/煤层气/sources.json --out-dir ramp
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TIER_LABEL = {"upstream": "上游", "midstream": "中游", "downstream": "下游"}
TIER_ORDER = ["upstream", "midstream", "downstream"]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def norm_ref(ref: str) -> str:
    m = re.search(r"\d+", str(ref))
    if not m:
        return str(ref)
    return f"S{int(m.group(0)):02d}"


def esc(label: str) -> str:
    return str(label).replace('"', "'").replace("\n", " ").strip() or "未命名"


def convert_sources(registry_path: Path, out_path: Path) -> dict[str, str]:
    """Convert industry-research sources.json -> our sources.jsonl; return old->new refs."""
    data = load_json(registry_path)
    items = data.get("items", []) if isinstance(data, dict) else []
    mapping: dict[str, str] = {}
    rows: list[dict] = []
    seen: set[str] = set()
    for item in items:
        old = str(item.get("ref", ""))
        new = norm_ref(old)
        if not old or new in seen:
            continue
        seen.add(new)
        mapping[old] = new
        origin = str(item.get("origin", ""))
        captured = str(item.get("capturedAt", ""))[:10] or "unknown"
        rows.append(
            {
                "id": new,
                "title": str(item.get("note") or origin or new),
                "url": origin,
                "publisher": "",
                "published": "unknown",
                "accessed": captured,
                "tier": "C",
                "sourceKind": "report" if origin.startswith(("http://", "https://")) else "other",
                "usedFor": ["chain"],
                "note": f"由 dsh-industry-research 导入（原 ref {old}）",
            }
        )
    out_path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    return mapping


def main() -> int:
    parser = argparse.ArgumentParser(description="Import dsh-industry-research chain.json as a ramp seed")
    parser.add_argument("--chain", required=True, help="chain.json path")
    parser.add_argument("--sources", default=None, help="industry-research sources.json path")
    parser.add_argument("--out-dir", default="ramp")
    args = parser.parse_args()

    chain_path = Path(args.chain)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        chain = load_json(chain_path)
    except Exception as exc:
        print(f"ERROR: cannot read {chain_path}: {exc}", file=sys.stderr)
        return 2

    nodes = chain.get("nodes") or []
    edges = chain.get("edges") or []
    if not isinstance(nodes, list) or not isinstance(edges, list):
        print("ERROR: chain.json must have nodes[] and edges[]", file=sys.stderr)
        return 2
    if not nodes:
        print("ERROR: chain.json has no nodes", file=sys.stderr)
        return 2

    ref_map: dict[str, str] = {}
    if args.sources:
        try:
            ref_map = convert_sources(Path(args.sources), out_dir / "sources-imported.jsonl")
        except Exception as exc:
            print(f"ERROR: cannot convert sources: {exc}", file=sys.stderr)
            return 2

    def ref_of(value: str) -> str:
        return ref_map.get(str(value), str(value))

    node_by_id = {str(n.get("id")): n for n in nodes}
    lines: list[str] = [
        f"# {chain.get('industry', '行业')} · 产业链图种子（来自 dsh-industry-research）",
        "",
        "> 这是导入的**种子**，不是最终 `chain.md`。请把它合并进 `chain.md`：保留节点/指标/来源，补上大白话、玩家现状、规划和关系。",
        "",
        f"- 节点：{len(nodes)} 个；边：{len(edges)} 条；来源映射：{len(ref_map)} 条。",
        "",
        "## 1. 分段与节点",
        "",
        "| 层级 | 节点 | 指标（值 / 待补） | 状态 | 来源 |",
        "|---|---|---|---|---|",
    ]
    gaps: list[str] = []
    for tier in TIER_ORDER:
        for node in nodes:
            if node.get("tier") != tier:
                continue
            metrics = node.get("metrics") or []
            metric_bits = []
            for m in metrics:
                key = m.get("key", "")
                if m.get("value") is None:
                    metric_bits.append(f"{key}=待补")
                    gaps.append(f"{node.get('name')} / {key}")
                else:
                    unit = m.get("unit", "")
                    asof = f"（{m.get('asOf')}）" if m.get("asOf") else ""
                    src = ref_of(m.get("sourceRef", ""))
                    metric_bits.append(f"{key}={m.get('value')}{unit}{asof} [{src}]")
            status = node.get("status") or ""
            if status and node.get("statusAsOf"):
                status = f"{status}（{node.get('statusAsOf')}）"
            lines.append(
                f"| {TIER_LABEL.get(tier, tier)} | {node.get('name', node.get('id'))} "
                f"| {'；'.join(metric_bits) if metric_bits else '—'} | {status or '—'} | — |"
            )

    lines += ["", "## 2. 边（谁和谁有关系）", "", "| from | to | 说明 |", "|---|---|---|"]
    for e in edges:
        f = node_by_id.get(str(e.get("from")), {}).get("name", e.get("from"))
        t = node_by_id.get(str(e.get("to")), {}).get("name", e.get("to"))
        lines.append(f"| {f} | {t} | {e.get('note', '')} |")

    lines += ["", "## 3. 指标缺口（待补）", ""]
    lines += [f"- {g}" for g in gaps] or ["- 无"]
    lines += [
        "",
        "## 4. 合并到 chain.md 的建议",
        "",
        "1. 把第 1 节的节点/指标并入 `chain.md` 的“产业链总览”和玩家表；",
        "2. 把第 2 节的边并入 relations 表；每条边补“证据/信心/来源”；",
        "3. 把 `sources-imported.jsonl` 合并进 `sources.jsonl`（注意 id 冲突），或直接引用；",
        "4. 用 `chain-seed.mmd` 替换/合并 `chain.mmd`；",
        "5. 如果 industry-research 生成了 `chain.svg`，复制成 `ramp/chain.svg` 并在 README 里引用。",
        "",
        "## 依据与来源",
        "",
        "- 指标 `sourceRef` 已按 sources 映射改写；未提供 `--sources` 时保留原 ref。",
        "- 本文件由脚本生成，数值与关系以原始 `chain.json` 为准。",
    ]
    (out_dir / "chain-seed.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # mermaid
    mmd = ["flowchart LR"]
    for tier in TIER_ORDER:
        tier_nodes = [n for n in nodes if n.get("tier") == tier]
        if not tier_nodes:
            continue
        mmd.append(f'  subgraph {tier}["{TIER_LABEL.get(tier, tier)}"]')
        for i, n in enumerate(tier_nodes):
            mmd.append(f'    N{i}_{tier}["{esc(n.get("name", n.get("id", "")))}"]')
        mmd.append("  end")
    idx: dict[str, str] = {}
    for tier in TIER_ORDER:
        for i, n in enumerate([x for x in nodes if x.get("tier") == tier]):
            idx[str(n.get("id"))] = f"N{i}_{tier}"
    for e in edges:
        a, b = idx.get(str(e.get("from"))), idx.get(str(e.get("to")))
        if a and b:
            note = esc(e.get("note", ""))
            mmd.append(f"  {a} -->|{note}| {b}" if note else f"  {a} --> {b}")
    (out_dir / "chain-seed.mmd").write_text("\n".join(mmd) + "\n", encoding="utf-8")

    print(f"wrote {out_dir / 'chain-seed.md'}")
    print(f"wrote {out_dir / 'chain-seed.mmd'}")
    if args.sources:
        print(f"wrote {out_dir / 'sources-imported.jsonl'} ({len(ref_map)} refs)")
    print(f"nodes={len(nodes)} edges={len(edges)} gaps={len(gaps)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
