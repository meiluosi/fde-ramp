#!/usr/bin/env python3
"""Print the next 3 most useful actions for a ramp workspace.

Usage:
  python3 scripts/next_steps.py --root ramp
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_artifacts import (  # noqa: E402
    activities_count, chain_counts, correction_count, domains_count, glossary_count,
    load_sources_quiet, verification_count,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Next best actions for a ramp")
    parser.add_argument("--root", default="ramp")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    state_path = root / "state.json"
    if not state_path.exists():
        print(f"没有 ramp: {root}")
        print("下一步：python3 scripts/init_ramp.py --industry \"行业\" --out " + str(root))
        return 2
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"state.json 无效：{exc}")
        return 2

    def read(name):
        p = root / name
        return p.read_text(encoding="utf-8") if p.exists() else ""

    mode = state.get("mode", "explore")
    layout = state.get("layout", "compact")
    sources = load_sources_quiet(root / "sources.jsonl")
    terms, statuses = glossary_count(read("glossary.md"))
    v_items = verification_count(read("verification-list.md"))
    business = read("business.md")
    correction_text = read("corrections.md") or read("verification-list.md")
    corrections = correction_count(correction_text)
    players, relations = chain_counts(read("chain.md"))
    if layout == "full":
        domains = domains_count(read("domains.md"))
        activities = activities_count(read("activities.md"))
    else:
        domains = domains_count(business)
        activities = activities_count(business)
    decision = read("decision-brief.md")

    actions: list[str] = []
    if not decision or "{{" in decision or "决策" not in decision:
        actions.append("填 `decision-brief.md`：要做什么决策、谁拍板、什么证据会改变判断。")
    if corrections < 5:
        actions.append(f"第 4 步：还差 {5 - corrections} 处真实修正；带图去问一线「您帮我改改」。")
    if len(sources) < 8:
        actions.append(f"补来源：现在 {len(sources)} 条，至少 8 条；先补 A/B 级。")
    if terms < 20:
        actions.append(f"补术语：现在 {terms} 个候选，至少 20 个；先收客户天天说的词。")
    if v_items < 5:
        actions.append(f"补待验证清单：现在 {v_items} 条，至少 5 条「我画了…您帮我改」的问题。")
    if players < 10:
        actions.append(f"补玩家：现在 {players} 家，至少 10 家；覆盖上下游。")
    if relations < 5:
        actions.append(f"补关系：现在 {relations} 条，至少 5 条；写清供应/股权/渠道/监管。")
    if domains < 3:
        actions.append(f"补业务域：现在 {domains} 个，至少 3 个；按客户组织切，不按行业报告切。")
    if activities < 10:
        actions.append(f"补活动行：现在 {activities} 行，至少 10 行；一行一个环节。")

    if mode == "client-ready":
        prov = state.get("provenance") or {}
        if any(m in correction_text for m in ("模拟", "虚构")):
            actions.append("client-ready 红灯：corrections.md 还有模拟/虚构标记；换成真实访谈。")
        if statuses.get("verified", 0) < 3:
            actions.append(f"client-ready：verified 术语只有 {statuses.get('verified', 0)} 个，至少 3 个。")
        if prov.get("evidence") != "customer":
            actions.append("client-ready：state.provenance.evidence 应为 'customer'。")
        if not str(prov.get("reviewedBy", "")).strip():
            actions.append("client-ready：state.provenance.reviewedBy 不能为空。")

    if not actions:
        print(f"✅ {root} 的探索模式检查项已经齐了。")
        print("下一步：做一次真实访谈修正，或运行 readiness --check 看五维分数。")
        if mode != "client-ready":
            print("要对外使用，把 state.mode 改成 client-ready，再跑 readiness --client --check。")
        return 0

    print(f"ramp: {root}  layout: {layout}  mode: {mode}")
    print("下一步最该做的 3 件事：")
    for i, action in enumerate(actions[:3], 1):
        print(f"  {i}. {action}")
    if len(actions) > 3:
        print(f"  还有 {len(actions) - 3} 项，跑 readiness 看完整清单。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
