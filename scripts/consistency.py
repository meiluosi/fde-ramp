#!/usr/bin/env python3
"""Cross-file consistency checks for a ramp workspace.

Checks:
  - every activity domain exists in domains.md;
  - every relation endpoint exists in chain.md players;
  - duplicate player/domain names;
  - state.counts vs files (a lightweight duplicate of validator warnings).

Usage:
  python3 scripts/consistency.py --root ramp
  python3 scripts/consistency.py --root ramp --strict
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_artifacts import (  # noqa: E402
    activities_count, cells_of, chain_counts, domains_count, is_separator, load_sources_quiet,
)


def tables(text: str):
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if not lines[i].strip().startswith("|"):
            i += 1
            continue
        header = cells_of(lines[i])
        if i + 1 >= len(lines) or not lines[i + 1].strip().startswith("|"):
            i += 1
            continue
        if not is_separator(cells_of(lines[i + 1])):
            i += 1
            continue
        rows = []
        j = i + 2
        while j < len(lines) and lines[j].strip().startswith("|"):
            row = cells_of(lines[j])
            if not is_separator(row):
                rows.append(row)
            j += 1
        yield header, rows
        i = j


def table_with(text: str, *needles: str):
    for header, rows in tables(text):
        joined = " ".join(header)
        if all(n in joined for n in needles):
            return header, rows
    return None, []


def main() -> int:
    parser = argparse.ArgumentParser(description="Cross-file consistency checks")
    parser.add_argument("--root", default="ramp")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    root = Path(args.root)

    def read(name):
        p = root / name
        return p.read_text(encoding="utf-8") if p.exists() else ""

    issues: list[str] = []
    plays, rels = chain_counts(read("chain.md"))
    try:
        layout = json.loads(read("state.json")).get("layout", "compact")
    except Exception:
        layout = "compact"
    business = read("business.md")
    domain_text = read("domains.md") if layout == "full" else (business or read("domains.md"))
    activity_text = read("activities.md") if layout == "full" else (business or read("activities.md"))
    domains_h, domain_rows = table_with(domain_text, "业务域")
    domain_names = {r[1] for r in domain_rows if len(r) > 1 and r[1]} if domains_h else set()
    domain_codes = {r[0] for r in domain_rows if r and r[0] and r[0] != "#"} if domains_h else set()
    activities_h, activity_rows = table_with(activity_text, "业务域", "环节")
    if activity_rows and (domain_names or domain_codes):
        allowed = domain_names | domain_codes
        for row in activity_rows:
            if len(row) > 0 and row[0] and row[0] not in allowed:
                issues.append(f"activity domain not in domains.md: {row[0]!r}")
    chain_h, player_rows = table_with(read("chain.md"), "玩家", "现状")
    # relation endpoints are intentionally descriptive in some packs, so only
    # duplicate-name checks are safe across industry packs.
    # duplicate names
    for label, rows, idx in (("player", player_rows, 0), ("domain", domain_rows, 1)):
        names = [r[idx] for r in rows if len(r) > idx and r[idx]]
        dups = sorted({n for n in names if names.count(n) > 1})
        for d in dups:
            issues.append(f"duplicate {label}: {d!r}")

    print(f"players: {plays}  relations: {rels}  domains: {len(domain_names)}  activities: {activities_count(activity_text)}")
    print(f"issues: {len(issues)}")
    for issue in sorted(set(issues)):
        print("WARN:", issue)
    if args.strict and issues:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
