#!/usr/bin/env python3
"""Import a dsh-industry-research company card (card.json) into a ramp workspace.

Writes <out-dir>/company-card-<slug>.md. Does not modify existing ramp files.

Usage:
  python3 scripts/import_company_card.py --card /path/companies/acme/card.json --out-dir ramp
"""
from __future__ import annotations

import json
import sys
from argparse import ArgumentParser
from pathlib import Path


def main() -> int:
    parser = ArgumentParser(description="Import dsh-industry-research company card")
    parser.add_argument("--card", required=True)
    parser.add_argument("--out-dir", default="ramp")
    args = parser.parse_args()

    path = Path(args.card)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        card = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: cannot read {path}: {exc}", file=sys.stderr)
        return 2

    slug = card.get("slug") or "company"
    lines = [
        f"# 公司速览卡：{card.get('name', slug)}",
        "",
        f"> 来自 dsh-industry-research `company_scan`；扫描时间：{card.get('asOf', '')}。",
        "> 这是**证据卡**，不是结论；所有数字要回数据文件/行号核对。",
        "",
        "## 1. 基本信息",
        "",
        f"- 名称：{card.get('name', '')}",
        f"- 上市状态：{card.get('status', '未声明')}" + (f"（{card.get('statusAsOf')}）" if card.get("statusAsOf") else ""),
        f"- 代码：{card.get('ticker', '未声明')}",
        "",
        "## 2. 数据文件来源",
        "",
        "| 文件 | 大小 | 行数 | SHA-256（前 12） |",
        "|---|---|---|---|",
    ]
    for s in card.get("sources") or []:
        lines.append(f"| {s.get('path', '')} | {s.get('bytes', '')} | {s.get('lines', '')} | {str(s.get('sha256', ''))[:12]} |")

    lines += ["", "## 3. 结构大纲", ""]
    for o in card.get("outline") or []:
        lines.append(f"### {o.get('path', '')}")
        for h in o.get("headings") or []:
            lines.append(f"- {h if isinstance(h, str) else h.get('text', '')}")
        lines.append("")

    lines += ["", "## 4. 可引用的数字行（figure candidates）", "", "| 文件 | 行 | 原文 |", "|---|---|---|"]
    for f in card.get("figureCandidates") or []:
        text = str(f.get("text", "")).replace("|", "/")
        lines.append(f"| {f.get('path', '')} | {f.get('line', '')} | {text} |")

    lines += ["", "## 5. 公开网页来源", ""]
    for w in card.get("webSources") or []:
        when = w.get("publishedAt") or w.get("asOf")
        lines.append(f"- {w.get('title') or w.get('url')} — {w.get('url', '')}" + (f"（{when}）" if when else ""))
    if not card.get("webSources"):
        lines.append("- 未运行 web 辅助/没有公开网页来源")

    lines += ["", "## 6. 指标（每个值都有来源与日期）", "", "| 指标 | 值 | 单位 | 日期 | 来源 |", "|---|---|---|---|---|"]
    for m in card.get("metrics") or []:
        lines.append(f"| {m.get('key', '')} | {m.get('value', '')} | {m.get('unit', '')} | {m.get('asOf', '')} | {m.get('source', '')} |")
    if not card.get("metrics"):
        lines.append("| — | — | — | — | — |")

    lines += ["", "## 7. 证据缺口", ""]
    for g in card.get("gaps") or []:
        lines.append(f"- {g}")
    if not card.get("gaps"):
        lines.append("- 无显式缺口（不代表信息完整）")

    lines += [
        "",
        "## 8. 合并建议",
        "",
        "1. 把「结构大纲 + 数字行」用于 `chain.md` 的玩家现状/指标，引用时写清文件 + 行号；",
        "2. `gaps` 并进 `verification-list.md`；",
        "3. 上市状态/代码写进玩家表，标扫描时间；",
        "4. 不要直接引用卡片里的「待补」段落当事实。",
        "",
        "## 依据与来源",
        "",
        "- 本文件由脚本从 `card.json` 生成；原始证据以 card.json / 数据文件为准。",
    ]
    out = out_dir / f"company-card-{slug}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
