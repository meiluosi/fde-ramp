#!/usr/bin/env python3
"""Import a dsh-scout case export into a ramp workspace.

Reads case.json (or a directory containing the five-file export) and writes
<out-dir>/scout-import.md. It does not modify existing ramp files.

Usage:
  python3 scripts/import_scout_case.py --case /path/scout/acme/case.json --out-dir ramp
  python3 scripts/import_scout_case.py --case /path/scout/acme --out-dir ramp
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_case(path: Path) -> dict:
    if path.is_dir():
        path = path / "case.json"
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Import a dsh-scout case export")
    parser.add_argument("--case", required=True, help="case.json or export directory")
    parser.add_argument("--out-dir", default="ramp")
    args = parser.parse_args()

    case_path = Path(args.case)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        case = load_case(case_path)
    except Exception as exc:
        print(f"ERROR: cannot read {case_path}: {exc}", file=sys.stderr)
        return 2

    subject = case.get("subject") or {}
    role = case.get("role") or {}
    lines = [
        f"# {case.get('title', '尽调案例')} · 从 dsh-scout 导入",
        "",
        "> 这是导入的**证据草稿**，不是最终结论。把它合并进 `chain.md`（公司现状/关系）、"
        "`verification-list.md`（未核实项）和 `brief.md`（访谈问题）。",
        "",
        "## 1. 基本信息",
        "",
        f"- 公司：{subject.get('name', '')}",
        f"- 岗位/对象：{role.get('title', '')}" + (f"（{role.get('location')}）" if role.get("location") else ""),
        f"- 决策：**{case.get('decision', '')}** — {case.get('decisionReason', '')}",
        f"- 主体核验：{subject.get('identityStatus', '')}",
        f"- 案例 id：{case.get('caseId', '')}",
        "",
        "## 2. 来源（scout 的 E0–E3 证据等级）",
        "",
        "| 来源 | 类型 | 证据等级 | 标题 | 链接 | 备注 |",
        "|---|---|---|---|---|---|",
    ]
    for s in case.get("sources") or []:
        lines.append(
            f"| {s.get('sourceId', '')} | {s.get('type', '')} | {s.get('evidenceLevel', '')} "
            f"| {str(s.get('title', '')).replace('|', '/')} | {s.get('url') or ''} | {s.get('note', '')} |"
        )

    lines += ["", "## 3. 结论/主张", "", "| 主张 | 状态 | 证据等级 | 维度 | 影响 | 来源 | 下一步 |", "|---|---|---|---|---|---|---|"]
    for c in case.get("claims") or []:
        lines.append(
            f"| {str(c.get('text', '')).replace('|', '/')} | {c.get('status', '')} | {c.get('evidenceLevel', '')} "
            f"| {c.get('dimension', '')} | {c.get('impact', '')} | {', '.join(c.get('sourceIds') or [])} "
            f"| {c.get('nextAction', '')} |"
        )

    questions = case.get("interviewQuestions") or []
    lines += ["", "## 4. 访谈问题（合并进 brief.md）", ""]
    lines += [f"{i}. {q}" for i, q in enumerate(questions, 1)] or ["- 无"]

    lines += [
        "",
        "## 5. 合并建议",
        "",
        "1. **证据等级映射**：E3/E2 → 我们的 ✅候选；E1 → ⚠️；E0/unknown → ❓。不要把 scout 的 `verified` 直接当我们的 `verified`（我们的 `verified` 只认客户/一线确认）。",
        "2. `unknown` / `needs_verification` 的主张 → 加进 `verification-list.md`；",
        "3. `interviewQuestions` → 合并进 `brief.md` 或 `open-questions.md`；",
        "4. 公司主体核验结果 → 写进 `chain.md` 的玩家现状，标来源与日期。",
        "",
        "## 依据与来源",
        "",
        "- 本文件由脚本从 `case.json` 生成；原始证据等级以 scout 导出为准。",
    ]
    out = out_dir / "scout-import.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out} (sources={len(case.get('sources') or [])} claims={len(case.get('claims') or [])})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
