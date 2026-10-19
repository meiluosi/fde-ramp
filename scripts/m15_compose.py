#!/usr/bin/env python3
"""One-shot M1.5 composition: turn plugin exports into ramp import drafts.

Expected input layout (all optional, but at least one):
  <imports>/
    industry-research/<industry>/chain.json
    industry-research/<industry>/sources.json
    industry-research/<industry>/timeline.jsonl
    industry-research/companies/<name>/card.json
    scout/<case>/case.json

Usage:
  python3 scripts/m15_compose.py --imports /path/to/imports --out-dir ramp

It runs the matching importers and writes <out-dir>/m15-composition-report.md.
It never overwrites chain.md, sources.jsonl, players.md, etc.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def run_script(name: str, *args: str) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        capture_output=True,
        text=True,
    )
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Compose plugin exports into ramp import drafts")
    parser.add_argument("--imports", required=True, help="directory containing plugin exports")
    parser.add_argument("--out-dir", default="ramp")
    args = parser.parse_args()

    imports = Path(args.imports)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if not imports.is_dir():
        print(f"ERROR: imports dir not found: {imports}", file=sys.stderr)
        return 2

    results: list[tuple[str, int, str]] = []
    outputs: list[str] = []

    # 1) industry-research: chain/sources/timeline/cards
    ir_dirs = sorted(p for p in (imports / "industry-research").glob("*") if (p / "chain.json").exists()) if (imports / "industry-research").is_dir() else []
    for d in ir_dirs:
        cmd = ["--chain", str(d / "chain.json"), "--out-dir", str(out_dir)]
        if (d / "sources.json").exists():
            cmd += ["--sources", str(d / "sources.json")]
        code, log = run_script("import_industry_map.py", *cmd)
        results.append((f"industry_map: {d.name}", code, log))
        outputs += [str(out_dir / "chain-seed.md"), str(out_dir / "chain-seed.mmd")]
        if (d / "sources.json").exists():
            outputs.append(str(out_dir / "sources-imported.jsonl"))
        if (d / "timeline.jsonl").exists():
            code, log = run_script("import_industry_track.py", "--timeline", str(d / "timeline.jsonl"), "--out-dir", str(out_dir))
            results.append((f"industry_track: {d.name}", code, log))
            outputs.append(str(out_dir / "timeline-import.md"))

    card_dirs = sorted((imports / "industry-research" / "companies").glob("*/card.json")) if (imports / "industry-research" / "companies").is_dir() else []
    for card in card_dirs:
        code, log = run_script("import_company_card.py", "--card", str(card), "--out-dir", str(out_dir))
        results.append((f"company_scan: {card.parent.name}", code, log))
        outputs.append(str(out_dir / f"company-card-{card.parent.name}.md"))

    # 2) scout cases
    scout_dirs = sorted((imports / "scout").glob("*/case.json")) if (imports / "scout").is_dir() else []
    scout_source_rows: list[dict] = []
    tier_map = {"E3": "A", "E2": "B", "E1": "C", "E0": "D"}
    for case in scout_dirs:
        code, log = run_script("import_scout_case.py", "--case", str(case), "--out-dir", str(out_dir))
        results.append((f"scout: {case.parent.name}", code, log))
        outputs.append(str(out_dir / "scout-import.md"))
        try:
            data = json.loads(case.read_text(encoding="utf-8"))
            srcs = data.get("sources") or []
            separate = case.parent / "sources.json"
            if not srcs and separate.exists():
                decoded = json.loads(separate.read_text(encoding="utf-8"))
                srcs = decoded.get("sources") if isinstance(decoded, dict) else decoded
            for s in srcs or []:
                scout_source_rows.append({
                    "id": s.get("sourceId", ""),
                    "title": s.get("title") or s.get("url", ""),
                    "url": s.get("url") or "",
                    "publisher": "",
                    "published": "unknown",
                    "accessed": (s.get("capturedAt") or "")[:10] or "unknown",
                    "tier": tier_map.get(s.get("evidenceLevel"), "C"),
                    "sourceKind": "media",
                    "usedFor": ["brief", "verification"],
                    "note": f"dsh-scout {s.get('sourceId')} / {s.get('evidenceLevel')} / {s.get('type')}",
                })
        except Exception:
            pass
    if scout_source_rows:
        (out_dir / "sources-scout.jsonl").write_text(
            "\n".join(json.dumps(r, ensure_ascii=False) for r in scout_source_rows) + "\n", encoding="utf-8"
        )
        outputs.append(str(out_dir / "sources-scout.jsonl"))

    if not results:
        print(f"ERROR: no plugin exports found under {imports}", file=sys.stderr)
        return 2

    ok = sum(1 for _, code, _ in results if code == 0)
    lines = [
        "# M1.5 组合导入报告",
        "",
        f"- 导入目录：`{imports}`",
        f"- 输出目录：`{out_dir}`",
        f"- 任务：{len(results)} 个，成功 {ok} 个，失败 {len(results) - ok} 个。",
        "",
        "## 1. 执行记录",
        "",
        "| 来源 | 结果 | 输出 |",
        "|---|---|---|",
    ]
    for label, code, _ in results:
        lines.append(f"| {label} | {'✅ 成功' if code == 0 else '❌ 失败'} | 见下 |")
    lines += ["", "## 2. 生成的文件", ""]
    for p in sorted(set(outputs)):
        lines.append(f"- `{p}`")
    lines += [
        "",
        "## 3. 下一步（必须人工合并）",
        "",
        "- [ ] 把 `chain-seed.md` 的节点/指标/边并入 `chain.md`（保留来源，补大白话/规划/关系）；",
        "- [ ] 把 `sources-imported.jsonl` 合并进 `sources.jsonl`，检查 id 冲突；",
        "- [ ] 把 `timeline-import.md` 里 `confirmed-catalyst` 的条目补进 chain/brief，`forum-buzz` 进 verification；",
        "- [ ] 把 `company-card-*.md` 的玩家现状/指标并入玩家表；`gaps` 进 verification；",
        "- [ ] 把 `scout-import.md` 的未核实主张进 verification，访谈问题进 brief；",
        "- [ ] `chain-seed.mmd` 与 `chain.svg` 合并进 ramp 图；",
        "- [ ] 跑 `render_sources.py` / `validate_artifacts.py` / `readiness.py`。",
        "",
        "## 4. 失败详情",
        "",
    ]
    failed = [(label, log) for label, code, log in results if code != 0]
    if not failed:
        lines.append("- 无")
    else:
        for label, log in failed:
            lines.append(f"### {label}")
            lines.append("```text")
            lines.append(log)
            lines.append("```")

    report = out_dir / "m15-composition-report.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report} ({ok}/{len(results)} ok)")
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
