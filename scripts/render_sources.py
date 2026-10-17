#!/usr/bin/env python3
"""Generate a human-readable sources.md from sources.jsonl.

Usage:
  python3 scripts/render_sources.py --root ramp
  python3 scripts/render_sources.py --root ramp --output ramp/sources.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render sources.md from sources.jsonl")
    parser.add_argument("--root", default="ramp")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    ledger = root / "sources.jsonl"
    if not ledger.exists():
        print(f"missing {ledger}", file=sys.stderr)
        return 2

    rows: list[dict] = []
    for i, line in enumerate(ledger.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            print(f"sources.jsonl:{i}: invalid JSON ({exc.msg})", file=sys.stderr)
            return 2

    out = Path(args.output).resolve() if args.output else root / "sources.md"
    lines = [
        "# 来源清单",
        "",
        "> 这份清单由 `scripts/render_sources.py` 从 `sources.jsonl` 生成，给人看的；",
        "> 正文里的 `[S01]` 都能在这里查到。没在正文用到的来源也保留，方便追溯。",
        "",
        f"共 {len(rows)} 条。",
        "",
        "| 编号 | 标题 | 发布方 | 日期 | 等级 | 类型 | 用途 | 链接 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        title = str(r.get("title", "")).replace("|", "\\|")
        publisher = str(r.get("publisher", "")).replace("|", "\\|")
        published = str(r.get("published", "")).replace("|", "\\|")
        tier = str(r.get("tier", ""))
        kind = str(r.get("sourceKind", ""))
        used = r.get("usedFor", "")
        if isinstance(used, list):
            used = "、".join(str(x) for x in used)
        used = str(used).replace("|", "\\|")
        url = str(r.get("url", ""))
        lines.append(
            f"| [{r.get('id', '')}] | {title} | {publisher} | {published} | {tier} | {kind} | {used} | {url} |"
        )
    lines += [
        "",
        "## 说明",
        "",
        "- **等级**：A=官方一手，B=行业机构/学术，C=媒体/研报摘要，D=其他。",
        "- **类型**：official（官方）、report（研报/论文）、practitioner（从业者科普）、media（媒体）、other。",
        "- 打不开或找不到的公开源，请写进 `verification-list.md`，不要编造 URL。",
        "",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out} ({len(rows)} sources)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
