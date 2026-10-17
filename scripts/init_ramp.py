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
    "plan.md": "plan.md",
    "sources.md": "sources.md",
    "value-chain.md": "value-chain.md",
    "value-chain.mmd": "value-chain.mmd",
    "chain.md": "chain.md",
    "chain.mmd": "chain.mmd",
    "domains.md": "domains.md",
    "activities.md": "activities.md",
    "glossary.md": "glossary.md",
    "flow.md": "flow.md",
    "flow.mmd": "flow.mmd",
    "verification-list.md": "verification-list.md",
    "corrections.md": "corrections.md",
    "open-questions.md": "open-questions.md",
    "brief.md": "brief.md",
    "readiness.md": "readiness.md",
    "drill-scorecard.md": "drill-scorecard.md",
    "calibration-log.md": "calibration-log.md",
}


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

    for src_name, dst_name in FILES.items():
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
    (out / "state.json").write_text(json.dumps(rendered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"ramp workspace created: {out}")
    print("next: fill value-chain.md, then run:")
    print(f"  python3 {Path(__file__).with_name('validate_artifacts.py')} --root {args.out}")
    print(f"  python3 {Path(__file__).with_name('readiness.py')} --root {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
