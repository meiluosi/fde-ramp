#!/usr/bin/env python3
"""Initialize a ramp workspace from templates.

Usage:
  python3 scripts/init_ramp.py --industry "煤层气" --customer "某公司" \
      --persona "技术负责人" --deadline 2026-10-25 [--out ramp] [--force]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEMPLATES = REPO / "templates"

# template file -> destination file
FILES = {
    "decision-brief.md": "decision-brief.md",
    "chain.md": "chain.md",
    "glossary.md": "glossary.md",
    "business.md": "business.md",
    "verification-list.md": "verification-list.md",
    "brief.md": "brief.md",
    "process-metrics.md": "process-metrics.md",
    "opportunities.md": "opportunities.md",
}

MINIMAL = {
    "decision-brief.md", "chain.md", "glossary.md", "business.md",
    "verification-list.md", "brief.md",
}

ANALYSIS = {"process-metrics.md", "opportunities.md"}


def render(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a ramp/ workspace")
    parser.add_argument("--industry", required=True)
    parser.add_argument("--customer", default="待确认")
    parser.add_argument("--persona", default="待确认")
    parser.add_argument("--deadline", default="待确认")
    parser.add_argument("--out", default="ramp")
    parser.add_argument("--force", action="store_true", help="overwrite non-empty output dir")
    parser.add_argument("--mode", choices=["explore", "client-ready"], default="explore", help="readiness mode")
    parser.add_argument("--analysis", action="store_true", help="also generate process-metrics.md / opportunities.md")
    args = parser.parse_args()

    out = Path(args.out).resolve()
    if out.exists() and any(out.iterdir()) and not args.force:
        print(f"refusing to overwrite non-empty dir: {out} (use --force)", file=sys.stderr)
        return 2
    out.mkdir(parents=True, exist_ok=True)

    values = {
        "INDUSTRY": args.industry,
        "CUSTOMER": args.customer,
        "PERSONA": args.persona,
        "DEADLINE": args.deadline,
        "DATE": dt.date.today().isoformat(),
    }

    keep = MINIMAL | (ANALYSIS if args.analysis else set())
    selected = {k: v for k, v in FILES.items() if Path(k).name in keep}
    for src_name, dst_name in selected.items():
        src = TEMPLATES / src_name
        if not src.exists():
            print(f"missing template: {src}", file=sys.stderr)
            return 3
        (out / dst_name).write_text(render(src.read_text(encoding="utf-8"), values), encoding="utf-8")

    # sources ledger starts empty
    (out / "sources.jsonl").write_text("", encoding="utf-8")

    state = json.loads((TEMPLATES / "state.json").read_text(encoding="utf-8"))
    rendered = json.loads(render(json.dumps(state, ensure_ascii=False), values))
    # artifacts are relative to the ramp root, regardless of --out name
    rendered["artifacts"] = {
        key: str(value).rsplit("/", 1)[-1] for key, value in (rendered.get("artifacts") or {}).items()
    }
    rendered["mode"] = args.mode
    rendered["layout"] = "compact"
    if True:
        rendered["artifacts"] = {
            "decision_brief": "decision-brief.md",
            "chain": "chain.md",
            "glossary": "glossary.md",
            "business": "business.md",
            "verification_list": "verification-list.md",
            "brief": "brief.md",
            "sources": "sources.jsonl",
            "sources_md": "sources.md",
        }
        if args.analysis:
            rendered["artifacts"].update({
                "process_metrics": "process-metrics.md",
                "opportunities": "opportunities.md",
            })
    (out / "state.json").write_text(json.dumps(rendered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"ramp workspace created: {out}")
    print(f"layout: compact  mode: {args.mode}  files: {len(selected) + 2}")
    print("next: fill decision-brief.md, then chain.md / business.md / verification-list.md")
    print(f"  python3 {Path(__file__).with_name('next_steps.py')} --root {args.out}")
    print(f"  python3 {Path(__file__).with_name('validate_artifacts.py')} --root {args.out}")
    print(f"  python3 {Path(__file__).with_name('readiness.py')} --root {args.out}")
    print("对外前把 state.mode 改成 client-ready 并跑 readiness --client --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
