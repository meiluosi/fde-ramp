#!/usr/bin/env python3
"""Merge m15_compose drafts into an existing ramp workspace.

Copies imported drafts, appends their sources to sources.jsonl with fresh ids,
and adds a marked section to chain.md. It never overwrites chain.md/activities.md.

Usage:
  python3 scripts/merge_imports.py --ramp ramp --imports ramp-m15
  python3 scripts/merge_imports.py --ramp ramp --imports ramp-m15 --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

IMPORT_MD = [
    "chain-seed.md",
    "timeline-import.md",
    "scout-import.md",
    "m15-composition-report.md",
]
IMPORT_ASSETS = ["chain-seed.mmd", "chain.svg"]
MARKER = "## 插件导入（自动合并）"


def next_source_ids(existing: set[str], n: int) -> list[str]:
    nums = [int(m.group(1)) for i in existing if (m := re.fullmatch(r"S(\d+)", i))]
    cur = max(nums, default=0) + 1
    out = []
    for _ in range(n):
        while f"S{cur:02d}" in existing:
            cur += 1
        sid = f"S{cur:02d}"
        existing.add(sid)
        out.append(sid)
        cur += 1
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge m15_compose drafts into a ramp")
    parser.add_argument("--ramp", required=True)
    parser.add_argument("--imports", required=True, help="composed drafts dir (ramp-m15)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    ramp = Path(args.ramp)
    imports = Path(args.imports)
    if not (ramp / "sources.jsonl").exists() or not (ramp / "chain.md").exists():
        print(f"ERROR: {ramp} does not look like a ramp (missing sources.jsonl/chain.md)", file=sys.stderr)
        return 2
    if not imports.is_dir():
        print(f"ERROR: imports dir not found: {imports}", file=sys.stderr)
        return 2

    copied: list[str] = []
    for name in IMPORT_MD + IMPORT_ASSETS:
        src = imports / name
        if src.exists():
            copied.append(name)
    for p in sorted(imports.glob("company-card-*.md")):
        copied.append(p.name)

    source_rows: list[dict] = []
    sp = imports / "sources-imported.jsonl"
    if sp.exists():
        for line in sp.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                source_rows.append(json.loads(line))

    if args.dry_run:
        print(f"would copy: {', '.join(copied) or '(none)'}")
        print(f"would append {len(source_rows)} sources")
        print(f"would add section to {ramp / 'chain.md'}")
        return 0

    for name in copied:
        src = imports / name
        shutil.copy2(src, ramp / name)

    # merge sources
    sources_path = ramp / "sources.jsonl"
    existing_lines = [l for l in sources_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    existing = {json.loads(l)["id"] for l in existing_lines}
    new_ids = next_source_ids(existing, len(source_rows))
    mapping = []
    for row, nid in zip(source_rows, new_ids):
        old = row.get("id", "")
        row = {**row, "id": nid, "note": (row.get("note") or "") + f"（自动合并：原 {old}）"}
        existing_lines.append(json.dumps(row, ensure_ascii=False))
        mapping.append((old, nid))
    sources_path.write_text("\n".join(existing_lines) + "\n", encoding="utf-8")

    # append chain section
    chain = ramp / "chain.md"
    text = chain.read_text(encoding="utf-8")
    if MARKER not in text:
        block = [f"\n\n---\n\n{MARKER}\n", "> 由 `scripts/merge_imports.py` 生成；导入内容是证据草稿，不是客户确认。\n"]
        block.append(f"- 导入文件：{', '.join(f'`{n}`' for n in copied) or '无'}")
        block.append(f"- 新增来源：{len(source_rows)} 条（{', '.join(f'{a}→{b}' for a,b in mapping) or '无'}）")
        block.append("- 待验证项：见 `scout-import.md` 的 `unknown`/`needs_verification` 主张，以及 `timeline-import.md` 的 ❓ 条目")
        chain.write_text(text + "\n".join(block) + "\n", encoding="utf-8")

    report = ramp / "imports-merge-report.md"
    report.write_text(
        "# 插件导入自动合并报告\n\n"
        f"- ramp：`{ramp}`\n- 导入目录：`{imports}`\n\n"
        "## 1. 复制的文件\n\n"
        + ("\n".join(f"- `{n}`" for n in copied) or "- 无")
        + "\n\n## 2. 来源合并\n\n"
        + (f"- {len(source_rows)} 条：" + "、".join(f"{a}→{b}" for a, b in mapping) if mapping else "- 无")
        + "\n\n## 3. 下一步\n\n"
        "- 跑 `render_sources.py --root <ramp>` 刷新 `sources.md`；\n"
        "- 跑 `validate_artifacts.py --root <ramp> --strict`；\n"
        "- 跑 `readiness.py --root <ramp> --check`；\n"
        "- 按 `m15-composition-report.md` 第 3 节人工合并节点/玩家/待验证项。\n",
        encoding="utf-8",
    )
    print(f"copied {len(copied)} files; appended {len(source_rows)} sources; wrote {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
