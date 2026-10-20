#!/usr/bin/env python3
"""Check source URLs and freshness in a ramp workspace.

Usage:
  python3 scripts/check_sources.py --root ramp
  python3 scripts/check_sources.py --root ramp --no-network
  python3 scripts/check_sources.py --root ramp --strict
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import urllib.request
from pathlib import Path


def check_url(url: str, timeout: float) -> tuple[int | None, str]:
    if not url.startswith(("http://", "https://")):
        return None, "not-http"
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "fde-ramp-source-check/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, "ok"
    except Exception as exc:
        # some servers reject HEAD; retry GET once
        try:
            req = urllib.request.Request(url, method="GET", headers={"User-Agent": "fde-ramp-source-check/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, "ok(get)"
        except Exception:
            return None, str(exc)[:120]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check source URLs/freshness")
    parser.add_argument("--root", default="ramp")
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--stale-days", type=int, default=180)
    parser.add_argument("--no-network", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    root = Path(args.root)
    path = root / "sources.jsonl"
    if not path.exists():
        print(f"missing {path}", file=sys.stderr)
        return 2
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"bad json line: {line[:80]}", file=sys.stderr)
                return 2

    today = dt.date.today()
    dead, stale = [], []
    for row in rows:
        sid = row.get("id", "?")
        url = str(row.get("url", ""))
        accessed = str(row.get("accessed", ""))
        try:
            age = (today - dt.date.fromisoformat(accessed)).days
        except ValueError:
            age = None
        if age is not None and age > args.stale_days:
            stale.append((sid, age))
        if args.no_network or not url.startswith(("http://", "https://")):
            continue
        status, note = check_url(url, args.timeout)
        if status is None or status >= 400:
            dead.append((sid, status, note, url))

    print(f"sources: {len(rows)}  stale>{args.stale_days}d: {len(stale)}  dead: {len(dead)}")
    for sid, age in stale[:20]:
        print(f"STALE {sid}: last accessed {age} days ago")
    for sid, status, note, url in dead[:20]:
        print(f"DEAD  {sid}: {status or '-'} {note} {url}")
    if len(stale) > 20:
        print(f"... {len(stale)-20} more stale")
    if len(dead) > 20:
        print(f"... {len(dead)-20} more dead")

    if args.strict and (dead or stale):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
