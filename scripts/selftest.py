#!/usr/bin/env python3
"""Self-test for the fde-ramp skill.

Runs the CLI chain in a temporary directory and asserts the gate behaves:
  init -> validate -> readiness (fresh should FAIL)
  complete fixture -> validate --strict PASS, readiness --check PASS
  unknown source ref -> validate FAIL
  invalid state.json -> readiness clean error (exit 2)

Usage: python3 scripts/selftest.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PY = sys.executable
FAILED: list[str] = []


def run(script: str, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PY, str(REPO / "scripts" / script), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd or REPO),
    )


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        FAILED.append(name)
        if detail:
            print(detail[-1500:])


def build_complete(root: Path) -> None:
    sources = [
        {
            "id": f"S{i:02d}",
            "title": f"示例来源 {i}",
            "url": f"https://example.com/{i}",
            "publisher": "示例",
            "published": "2026-01-01",
            "accessed": "2026-10-18",
            "tier": "A" if i <= 4 else "C",
            "usedFor": ["value-chain"],
        }
        for i in range(1, 9)
    ]
    (root / "sources.jsonl").write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in sources) + "\n", encoding="utf-8"
    )

    statuses = ["public"] * 12 + ["needs-customer"] * 6 + ["unsure"] * 2
    rows = ["| # | term | EN | 一句话 | 用法 | 近邻 | 状态 | source |", "|---|---|---|---|---|---|---|---|"]
    for i, status in enumerate(statuses, 1):
        rows.append(f"| {i} | 术语{i} | term{i} | 一句人话 | 行业用法 | 近邻{i} | {status} | S{i % 8 + 1:02d} |")
    (root / "glossary.md").write_text("# 术语\n\n" + "\n".join(rows) + "\n", encoding="utf-8")

    v = ["| # | 我猜的是什么 | 为什么不确定 | 风险 | 成本 | 找谁 | 怎么问 | 状态 |", "|---|---|---|---|---|---|---|---|"]
    for i in range(1, 6):
        v.append(f"| {i} | 我猜是 X{i} | 无公开源 | 高 | 低 | 站长 | 「我画了…您帮我改」 | open |")
    (root / "verification-list.md").write_text("# 待验证\n\n" + "\n".join(v) + "\n", encoding="utf-8")

    f = ["# 流程", "", "| 节点 | 我理解的是 | 信心 | 来源 | 备注 |", "|---|---|---|---|---|"]
    for i in range(1, 6):
        f.append(f"| 节点{i} | 猜测 | ❓ | — | — |")
    f.append("| 节点6 | 有来源 | ✅ | S01 | — |")
    (root / "flow.md").write_text("\n".join(f) + "\n", encoding="utf-8")

    c = ["# 修正记录"]
    for i in range(1, 6):
        c += ["", f"## 修正 {i}", "", f"- 我原以为：A{i}", f"- 实际：B{i}", "- 差异原因：C", "- 影响：D", "- 来源：访谈", ""]
    (root / "corrections.md").write_text("\n".join(c), encoding="utf-8")

    chain = [
        "# 链路", "", "## 1. 分段", "| # | 分段 | 做什么 |", "|---|---|---|", "| 1 | 上游 | 生产 |", "",
        "## 2. 每段玩家", "", "| 玩家 | 角色 | 现状 | 近12月动作 | 未来规划 | 信心 | 来源 |",
        "|---|---|---|---|---|---|---|",
    ]
    for i in range(1, 11):
        chain.append(f"| 玩家{i} | 角色 | 现状 | 动作 | 自述：规划 | ✅ | S01 |")
    chain += ["", "## 3. 玩家关系", "", "| from | 关系类型 | to | 证据 | 信心 | 来源 |", "|---|---|---|---|---|---|"]
    for i in range(1, 6):
        chain.append(f"| 玩家{i} | 供应 | 玩家{i + 1} | 合同 [S01] | ✅ | S01 |")
    (root / "chain.md").write_text("\n".join(chain) + "\n", encoding="utf-8")

    domains = ["# 业务域", "", "| # | 业务域 | 目标 | 负责 | 流程 | 接口 | 痛点 | 信心 | 来源 |",
               "|---|---|---|---|---|---|---|---|---|"]
    for i in range(1, 4):
        domains.append(f"| {i} | 域{i} | 目标 | 部门 | 流程 | 接口 | 痛点 | ✅ | S01 |")
    (root / "domains.md").write_text("\n".join(domains) + "\n", encoding="utf-8")

    activities = ["# 活动", "",
                  "| 业务域 | 流程 | 环节/活动 | 做什么 | 谁做 | 影响谁 | 工具 | 背景 | 输入→输出 | 信心 | 来源 |",
                  "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i in range(1, 16):
        activities.append(f"| 域1 | 流程1 | 活动{i} | 做{i} | 岗位 | 下游 | 系统❓ | 背景 | A→B | ✅ | S01 |")
    (root / "activities.md").write_text("\n".join(activities) + "\n", encoding="utf-8")

    state = json.loads((root / "state.json").read_text(encoding="utf-8"))
    state["blocks"]["negate"] = "done"
    (root / "state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="fde-ramp-selftest-"))
    try:
        fresh = tmp / "fresh"
        r = run("init_ramp.py", "--industry", "测试", "--customer", "客户", "--persona", "技术", "--deadline", "2026-10-25", "--out", str(fresh))
        check("init fresh", r.returncode == 0, r.stdout + r.stderr)

        expected = {"decision-brief.md", "state.json", "sources.jsonl",
                    "chain.md", "glossary.md", "business.md",
                    "verification-list.md", "brief.md"}
        check("init generates required files", expected <= {p.name for p in fresh.iterdir()})

        check("minimal layout has decision-brief", (fresh / "decision-brief.md").exists())
        state = json.loads((fresh / "state.json").read_text(encoding="utf-8"))
        check("minimal state mode/layout", state.get("mode") == "explore" and state.get("layout") == "compact")

        r = run("validate_artifacts.py", "--root", str(fresh))
        check("fresh validate exit 0 (warnings ok)", r.returncode == 0, r.stdout + r.stderr)

        r = run("next_steps.py", "--root", str(fresh))
        check("next_steps prints actions", r.returncode == 0 and "下一步" in r.stdout, r.stdout + r.stderr)

        r = run("calc_process.py", "--minutes", "12", "--freq", "200", "--error-rate", "0.03",
                "--cost-per-error", "50", "--hourly-rate", "60", "--realization", "0.4",
                "--build-cost", "200000", "--run-cost-per-day", "200")
        check("calc net ROI", r.returncode == 0 and "20,000.00" in r.stdout, r.stdout + r.stderr)

        r = run("readiness.py", "--root", str(fresh), "--set", "structure=4", "--set", "language=4",
                "--set", "players=4", "--set", "decision=4", "--set", "dialogue=4", "--check")
        check("fresh readiness fails evidence gate", r.returncode == 1, r.stdout + r.stderr)

        full = tmp / "complete"
        r = run("init_ramp.py", "--industry", "测试", "--out", str(full), "--full")
        build_complete(full)
        r = run("render_sources.py", "--root", str(full))
        check("render sources.md", r.returncode == 0 and "S01" in (full / "sources.md").read_text(encoding="utf-8"), r.stdout + r.stderr)

        r = run("readiness.py", "--root", str(full), "--set", "structure=4", "--set", "language=4",
                "--set", "players=3", "--set", "decision=3", "--set", "dialogue=3", "--check")
        check("complete fixture readiness PASS", r.returncode == 0, r.stdout + r.stderr)

        r = run("validate_artifacts.py", "--root", str(full), "--strict")
        check("complete fixture strict validate PASS", r.returncode == 0, r.stdout + r.stderr)

        r = run("readiness.py", "--root", str(full), "--client", "--check", "--no-write")
        check("client-ready gate rejects explore fixture", r.returncode == 1 and "client" in r.stdout, r.stdout + r.stderr)

        r = run("consistency.py", "--root", str(full), "--strict")
        check("consistency passes complete fixture", r.returncode == 0, r.stdout + r.stderr)

        r = run("check_sources.py", "--root", str(full), "--no-network")
        check("source check offline passes", r.returncode == 0, r.stdout + r.stderr)

        with (full / "value-chain.md").open("a", encoding="utf-8") as fh:
            fh.write("\n合并引用 [S01/S02] 与 [S03、S04]。\n")
        r = run("validate_artifacts.py", "--root", str(full))
        check("merged source refs [S01/S02] parse", r.returncode == 0, r.stdout + r.stderr)

        with (full / "value-chain.md").open("a", encoding="utf-8") as fh:
            fh.write("\n未知引用 [S99]。\n")
        r = run("validate_artifacts.py", "--root", str(full))
        check("unknown source ref fails", r.returncode == 1, r.stdout + r.stderr)

        (full / "state.json").write_text("{bad json", encoding="utf-8")
        r = run("readiness.py", "--root", str(full))
        check("invalid state.json handled cleanly", r.returncode == 2 and "invalid JSON" in (r.stdout + r.stderr), r.stdout + r.stderr)

        r = run("init_ramp.py", "--industry", "x", "--out", str(full))
        check("refuse non-empty dir", r.returncode == 2, r.stdout + r.stderr)
        sys.path.insert(0, str(REPO / "scripts"))
        from validate_artifacts import correction_count, flow_guess_count  # noqa: E402

        sample = "# 修正\n## 修正 1\n\n- 我原以为：\n  A\n- 实际：\n  B\n"
        check("correction value on next line", correction_count(sample) == 1, repr(sample))
        check(
            "prose ❓ not counted as guessed node",
            flow_guess_count("| 节点 | 说明 |\n|---|---|\n| A | 这里提到 ❓ 但这不是信心列 |\n") == 0,
        )

        # ---- M1.5 importers ----
        imp = tmp / "import"
        imp.mkdir()
        chain = {
            "industry": "测试行业",
            "nodes": [
                {"id": "n1", "name": "上游A", "tier": "upstream",
                 "metrics": [{"key": "规模", "value": 12, "unit": "亿元", "sourceRef": "S1"}, {"key": "毛利率"}]},
                {"id": "n2", "name": "中游B", "tier": "midstream",
                 "metrics": [{"key": "产量", "value": 3, "unit": "万吨", "sourceRef": "S2"}]},
            ],
            "edges": [{"from": "n1", "to": "n2", "note": "原料供应"}],
        }
        (imp / "chain.json").write_text(json.dumps(chain, ensure_ascii=False), encoding="utf-8")
        (imp / "sources.json").write_text(
            json.dumps({"next": 3, "items": [
                {"ref": "S1", "origin": "https://example.com/a", "capturedAt": "2026-10-01", "note": "来源A"},
                {"ref": "S2", "origin": "https://example.com/b", "capturedAt": "2026-10-02", "note": "来源B"},
            ]}, ensure_ascii=False), encoding="utf-8")
        r = run("import_industry_map.py", "--chain", str(imp / "chain.json"),
                "--sources", str(imp / "sources.json"), "--out-dir", str(imp))
        check("import industry_map chain", r.returncode == 0 and "上游A" in (imp / "chain-seed.md").read_text(encoding="utf-8"),
              r.stdout + r.stderr)
        check("import industry_map sources -> S01", (imp / "sources-imported.jsonl").read_text(encoding="utf-8").count('"S01"') == 1)

        case = {
            "schemaVersion": "dsh-scout.case.v0", "caseId": "acme", "title": "ACME 尽调", "language": "zh",
            "decisionObjective": "判断是否推进",
            "subject": {"name": "ACME", "identityStatus": "needs_verification", "identitySourceIds": []},
            "role": {"title": "技术负责人", "location": "深圳", "fitQuestion": "值得去吗"},
            "decision": "VERIFY", "decisionReason": "主体未核验",
            "sources": [{"sourceId": "s1", "type": "official_filing", "title": "年报",
                         "url": "https://example.com/report", "capturedAt": "2026-10-01",
                         "evidenceLevel": "E2", "status": "ok"}],
            "claims": [{"claimId": "c1", "text": "营收 1 亿", "status": "reported", "evidenceLevel": "E2",
                        "dimension": "company_and_founder", "impact": "material", "sourceIds": ["s1"],
                        "nextAction": "核对页码", "confidenceNote": "媒体"}],
            "interviewQuestions": ["数据口径是什么？"],
        }
        (imp / "case.json").write_text(json.dumps(case, ensure_ascii=False), encoding="utf-8")
        r = run("import_scout_case.py", "--case", str(imp / "case.json"), "--out-dir", str(imp))
        check("import scout case", r.returncode == 0 and "数据口径" in (imp / "scout-import.md").read_text(encoding="utf-8"),
              r.stdout + r.stderr)

        (imp / "timeline.jsonl").write_text(
            "\n".join(json.dumps(x, ensure_ascii=False) for x in [
                {"date": "2026-09-01", "title": "政策A", "url": "https://example.com/p1",
                 "summary": "摘要", "capturedAt": "2026-10-01", "topics": [], "evidenceCategory": "confirmed-catalyst"},
                {"date": "2026-09-02", "title": "媒体B", "url": "https://example.com/p2",
                 "summary": "摘要", "capturedAt": "2026-10-01", "topics": [], "evidenceCategory": "market-narrative"},
            ]) + "\n", encoding="utf-8",
        )
        r = run("import_industry_track.py", "--timeline", str(imp / "timeline.jsonl"), "--out-dir", str(imp))
        check("import industry_track", r.returncode == 0 and "政策A" in (imp / "timeline-import.md").read_text(encoding="utf-8"),
              r.stdout + r.stderr)

        card = {
            "name": "ACME", "slug": "acme", "asOf": "2026-10-01",
            "sources": [], "outline": [{"path": "/a.md", "headings": ["一、业务"]}],
            "figureCandidates": [], "webSources": [], "gaps": ["缺 2026Q3"],
            "disclaimer": "仅供研究", "metrics": [{"key": "营业收入", "value": 1, "unit": "亿元",
                                                            "asOf": "2025-12-31", "source": "/a.md"}],
        }
        (imp / "card.json").write_text(json.dumps(card, ensure_ascii=False), encoding="utf-8")
        r = run("import_company_card.py", "--card", str(imp / "card.json"), "--out-dir", str(imp))
        check("import company card", r.returncode == 0 and "营业收入" in (imp / "company-card-acme.md").read_text(encoding="utf-8"),
              r.stdout + r.stderr)

        imports = tmp / "imports"
        ir = imports / "industry-research" / "测试行业"
        companies = imports / "industry-research" / "companies" / "acme"
        scouts = imports / "scout" / "acme"
        for d in (ir, companies, scouts):
            d.mkdir(parents=True, exist_ok=True)
        shutil.copy2(imp / "chain.json", ir / "chain.json")
        shutil.copy2(imp / "sources.json", ir / "sources.json")
        shutil.copy2(imp / "timeline.jsonl", ir / "timeline.jsonl")
        shutil.copy2(imp / "card.json", companies / "card.json")
        shutil.copy2(imp / "case.json", scouts / "case.json")
        r = run("m15_compose.py", "--imports", str(imports), "--out-dir", str(tmp / "compose"))
        check("m15 compose", r.returncode == 0 and "失败 0" in (tmp / "compose" / "m15-composition-report.md").read_text(encoding="utf-8"),
              r.stdout + r.stderr)
        check(
            "verification-table ❓ not counted as flow node",
            flow_guess_count(
                "| # | 待验证点 | 当前信心 | 谁会知道 |\n|---|---|---|---|\n| 1 | X | ❓ | 站长 |\n| 2 | Y | ❓ | 商务 |\n"
            )
            == 0,
        )
        from validate_artifacts import activities_count, chain_counts, domains_count  # noqa: E402

        check("chain counts 10 players / 5 relations", chain_counts((full / "chain.md").read_text(encoding="utf-8")) == (10, 5))
        check("domains count", domains_count((full / "domains.md").read_text(encoding="utf-8")) == 3)
        check("activities count", activities_count((full / "activities.md").read_text(encoding="utf-8")) == 15)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if FAILED:
        print(f"{len(FAILED)} test(s) failed: {', '.join(FAILED)}")
        return 1
    print("all self-tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
