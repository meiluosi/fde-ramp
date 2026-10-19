#!/usr/bin/env python3
"""Import a dsh-industry-research timeline.jsonl into a ramp workspace.

Writes <out-dir>/timeline-import.md. Does not modify existing ramp files.

Usage:
  python3 scripts/import_industry_track.py --timeline /path/timeline.jsonl --out-dir ramp
"""
from __future__ import annotations

import json
import sys
from argparse import ArgumentParser
from pathlib import Path

CATEGORY_LABEL = {
    "confirmed-catalyst": "已确认催化（官方/一手）",
    "market-narrative": "市场叙事（媒体/研报）",
    "forum-buzz": "论坛/社区讨论",
    "technical-confirmation": "技术验证（可复现）",
    "macro-amplifier": "宏观放大（利率/汇率/政策）",
    "background-noise": "背景噪音",
}
CATEGORY_CONFIDENCE = {
    "confirmed-catalyst": "✅ 候选",
    "technical-confirmation": "✅ 候选",
    "market-narrative": "⚠️",
    "macro-amplifier": "⚠️",
    "forum-buzz": "❓",
    "background-noise": "❓",
}


def main() -> int:
    parser = ArgumentParser(description="Import dsh-industry-research timeline.jsonl")
    parser.add_argument("--timeline", required=True)
    parser.add_argument("--out-dir", default="ramp")
    args = parser.parse_args()

    path = Path(args.timeline)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    entries: list[dict] = []
    bad = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            bad += 1

    lines = [
        "# 政策与动态时间线（来自 dsh-industry-research）",
        "",
        "> 这是导入的**素材**，不是结论。把重要条目并进 `chain.md`（趋势/规划背景）、"
        "`verification-list.md`（待验证）或 `brief.md`（会前背景）。",
        "",
        f"- 条目：{len(entries)} 条" + (f"；损坏跳过：{bad} 条" if bad else ""),
        "",
        "## 1. 时间线",
        "",
        "| 日期 | 分类 | 标题 | 摘要 | 链接 | 建议信心 |",
        "|---|---|---|---|---|---|",
    ]
    for e in sorted(entries, key=lambda x: (x.get("date") or ""), reverse=True):
        cat = e.get("evidenceCategory") or "uncategorized"
        label = CATEGORY_LABEL.get(cat, cat)
        title = str(e.get("title", "")).replace("|", "/")
        summary = str(e.get("summary") or "").replace("|", "/")
        url = str(e.get("url") or "")
        lines.append(f"| {e.get('date') or '日期未知'} | {label} | {title} | {summary} | {url} | {CATEGORY_CONFIDENCE.get(cat, '❓')} |")

    lines += [
        "",
        "## 2. 分类计数",
        "",
    ]
    counts: dict[str, int] = {}
    for e in entries:
        cat = e.get("evidenceCategory") or "uncategorized"
        counts[cat] = counts.get(cat, 0) + 1
    for cat, n in sorted(counts.items(), key=lambda x: -x[1]):
        lines.append(f"- {CATEGORY_LABEL.get(cat, cat)}：{n}")

    lines += [
        "",
        "## 3. 合并建议",
        "",
        "1. `confirmed-catalyst` / `technical-confirmation` 可作事实候选，但仍要回原文核对；",
        "2. `market-narrative` / `macro-amplifier` 只能当背景，写「媒体/研报说」；",
        "3. `forum-buzz` / `background-noise` 只作线索，进 `verification-list.md`；",
        "4. 时间线不替代 `sources.jsonl`：要引用某条时，把 URL 登记为来源并给 `[Sxx]`。",
        "",
        "## 依据与来源",
        "",
        "- 本文件由脚本从 `timeline.jsonl` 生成；原始条目的 URL/快照哈希以插件导出为准。",
    ]
    out = out_dir / "timeline-import.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out} (entries={len(entries)}, bad={bad})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
