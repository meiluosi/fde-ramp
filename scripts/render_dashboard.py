#!/usr/bin/env python3
"""Render a self-contained ramp dashboard: four-number table + opportunity quadrant.

Usage:
  python3 scripts/render_dashboard.py --root ramp
  python3 scripts/render_dashboard.py --root ramp --out ramp/dashboard.html
"""
from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_sep(cs: list[str]) -> bool:
    return bool(cs) and all(re.fullmatch(r":?-{3,}:?", c or "") for c in cs)


def tables(md: str):
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        if not lines[i].strip().startswith("|"):
            i += 1
            continue
        header = cells(lines[i])
        if i + 1 >= len(lines) or not lines[i + 1].strip().startswith("|"):
            i += 1
            continue
        sep = cells(lines[i + 1])
        if not is_sep(sep):
            i += 1
            continue
        rows = []
        j = i + 2
        while j < len(lines) and lines[j].strip().startswith("|"):
            row = cells(lines[j])
            if not is_sep(row):
                rows.append(row)
            j += 1
        yield header, rows
        i = j


def col(header: list[str], *needles: str) -> int:
    for n in needles:
        for i, h in enumerate(header):
            if h == n:
                return i
    for n in needles:
        for i, h in enumerate(header):
            if n in h:
                return i
    return -1


def num(value: str | None) -> float | None:
    if value is None:
        return None
    s = str(value).replace(",", "").strip()
    m = re.search(r"[-+]?\d+(?:\.\d+)?", s)
    return float(m.group(0)) if m else None


def rate(value: str | None) -> float | None:
    n = num(value)
    if n is None:
        return None
    s = str(value)
    if "%" in s:
        return n / 100
    return n / 100 if n > 1 else n


def esc(v) -> str:
    return html.escape("" if v is None else str(v))


def load_metrics(root: Path):
    path = root / "process-metrics.md"
    if not path.exists():
        return []
    for header, rows in tables(path.read_text(encoding="utf-8")):
        if col(header, "耗时") >= 0 and col(header, "日频次") >= 0:
            return [dict(header=header, row=r) for r in rows if any(c for c in r)]
    return []


def load_opportunities(root: Path):
    path = root / "opportunities.md"
    if not path.exists():
        return [], []
    candidates, scores = [], []
    for header, rows in tables(path.read_text(encoding="utf-8")):
        if col(header, "机会ID") >= 0 and col(header, "信号") >= 0:
            candidates = [dict(header=header, row=r) for r in rows if any(c for c in r)]
        if col(header, "业务价值") >= 0 and col(header, "可行性") >= 0:
            scores = [dict(header=header, row=r) for r in rows if any(c for c in r)]
    return candidates, scores


def build_rows(metrics):
    out = []
    for item in metrics:
        h, r = item["header"], item["row"]
        get = lambda *n: r[col(h, *n)] if col(h, *n) >= 0 and col(h, *n) < len(r) else ""
        minutes, freq = num(get("耗时")), num(get("日频次"))
        rate_v, cost, hourly = rate(get("出错率")), num(get("单次代价")), num(get("人力单价"))
        labor = risk = ceiling = None
        if None not in (minutes, freq, hourly):
            labor = minutes / 60 * freq * hourly
            risk = (rate_v or 0) * freq * (cost or 0)
            ceiling = labor + risk
        out.append({
            "id": get("环节ID"), "domain": get("业务域"), "activity": get("环节/活动", "环节"),
            "who": get("谁做"), "minutes": minutes, "freq": freq, "rate": rate_v,
            "cost": cost, "hourly": hourly, "labor": labor, "risk": risk, "ceiling": ceiling,
            "source": get("数据来源"), "confidence": get("信心"),
        })
    return out


def build_opportunities(candidates, scores):
    by_id = {}
    for item in candidates:
        h, r = item["header"], item["row"]
        oid = r[col(h, "机会ID")] if col(h, "机会ID") >= 0 and len(r) > col(h, "机会ID") else ""
        sig = len(set(re.findall(r"[1-6]", r[col(h, "信号")] if col(h, "信号") >= 0 and len(r) > col(h, "信号") else "")))
        ceiling = num(r[col(h, "改进上限")]) if col(h, "改进上限") >= 0 and len(r) > col(h, "改进上限") else None
        by_id.setdefault(oid, {"id": oid}).update({"signals": sig, "ceiling": ceiling})
    for item in scores:
        h, r = item["header"], item["row"]
        oid = r[col(h, "机会")] if col(h, "机会") >= 0 and len(r) > col(h, "机会") else ""
        get = lambda *n: r[col(h, *n)] if col(h, *n) >= 0 and len(r) > col(h, *n) else ""
        data = num(get("数据可得性"))
        politics = num(get("政治阻力"))
        red_text = get("红灯")
        red = (data is not None and data <= 2) or (politics is not None and politics <= 2) or ("红" in str(red_text))
        by_id.setdefault(oid, {"id": oid}).update({
            "value": num(get("业务价值")), "feas": num(get("可行性")),
            "data": data, "politics": politics, "red": red, "ceiling": num(get("改进上限")),
        })
    items = list(by_id.values())
    qualified = [x for x in items if not x.get("red") and (x.get("value") or 0) >= 4 and (x.get("feas") or 0) >= 4]
    qualified.sort(key=lambda x: (-(x.get("feas") or 0), -(x.get("value") or 0)))
    first = qualified[0]["id"] if qualified else ""
    return items, first


def render(root: Path) -> str:
    metrics = build_rows(load_metrics(root))
    candidates, scores = load_opportunities(root)
    ops, first = build_opportunities(candidates, scores)
    totals = {
        "labor": sum(x["labor"] or 0 for x in metrics),
        "risk": sum(x["risk"] or 0 for x in metrics),
        "ceiling": sum(x["ceiling"] or 0 for x in metrics),
    }
    def money(v):
        return "" if v is None else f"{v:,.2f}"

    def plain(v):
        return "" if v is None else f"{v:g}"

    def pct(v):
        return "" if v is None else f"{v * 100:.1f}%"

    def metric_row(x):
        return (
            f"<tr><td>{esc(x['id'])}</td><td>{esc(x['domain'])}</td><td>{esc(x['activity'])}</td><td>{esc(x['who'])}</td>"
            f"<td>{plain(x['minutes'])}</td><td>{plain(x['freq'])}</td><td>{pct(x['rate'])}</td>"
            f"<td>{money(x['cost'])}</td><td>{money(x['hourly'])}</td>"
            f"<td>{money(x['labor'])}</td><td>{money(x['risk'])}</td><td>{money(x['ceiling'])}</td>"
            f"<td>{esc(x['confidence'])}</td></tr>"
        )

    total_rows = "".join(metric_row(x) for x in metrics)
    # quadrant SVG
    width, height, pad = 560, 380, 46
    plot_w, plot_h = width - pad * 2, height - pad * 2
    def sx(v): return pad + (max(0, min(5, v or 0)) / 5) * plot_w
    def sy(v): return height - pad - (max(0, min(5, v or 0)) / 5) * plot_h
    points = []
    for i, op in enumerate(ops):
        x, y = sx(op.get("feas")), sy(op.get("value"))
        color = "#b42318" if op.get("red") else ("#0a7f3f" if op.get("id") == first else "#2563eb")
        r = 8 if op.get("id") == first else 6
        points.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" opacity="0.9"/>'
            f'<text x="{x + 9:.1f}" y="{y + 4:.1f}" font-size="12" fill="#111">{esc(op.get("id"))}</text>'
        )
    quad = (
        f'<svg viewBox="0 0 {width} {height}" class="quadrant" role="img" aria-label="机会象限图">'
        f'<rect x="{pad}" y="{pad}" width="{plot_w}" height="{plot_h}" fill="#fafafa" stroke="#d0d7de"/>'
        f'<line x1="{pad + plot_w/2}" y1="{pad}" x2="{pad + plot_w/2}" y2="{pad + plot_h}" stroke="#d0d7de" stroke-dasharray="4 4"/>'
        f'<line x1="{pad}" y1="{pad + plot_h/2}" x2="{pad + plot_w}" y2="{pad + plot_h/2}" stroke="#d0d7de" stroke-dasharray="4 4"/>'
        f'<text x="{pad + 8}" y="{pad + 18}" font-size="12" fill="#0a7f3f">先做（高可行 + 高价值）</text>'
        f'<text x="{pad + plot_w - 150}" y="{pad + 18}" font-size="12" fill="#6b7280">有价值但难</text>'
        f'<text x="{pad + 8}" y="{pad + plot_h - 8}" font-size="12" fill="#6b7280">先不做</text>'
        f'<text x="{pad + plot_w - 150}" y="{pad + plot_h - 8}" font-size="12" fill="#6b7280">容易但价值低</text>'
        f'<text x="{width/2}" y="{height - 10}" font-size="12" text-anchor="middle" fill="#374151">可行性 →</text>'
        f'<text x="14" y="{height/2}" font-size="12" text-anchor="middle" fill="#374151" transform="rotate(-90 14 {height/2})">业务价值 →</text>'
        + "".join(points) + "</svg>"
    )
    op_rows = "".join(
        f"<tr class=\"{'danger' if o.get('red') else ('first' if o.get('id') == first else '')}\">"
        f"<td>{esc(o.get('id'))}</td><td>{esc(o.get('signals'))}</td><td>{esc(o.get('value'))}</td>"
        f"<td>{esc(o.get('feas'))}</td><td>{esc(o.get('data'))}</td><td>{esc(o.get('politics'))}</td>"
        f"<td>{'红灯' if o.get('red') else '—'}</td><td>{esc(o.get('ceiling'))}</td></tr>"
        for o in ops
    )
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>fde-ramp dashboard</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; background: #f6f8fa; color: #1f2328; }}
main {{ max-width: 1180px; margin: 0 auto; padding: 28px 20px 60px; }}
h1 {{ font-size: 24px; margin: 0 0 6px; }}
.meta {{ color: #57606a; font-size: 13px; margin-bottom: 20px; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 22px; }}
.card {{ background: #fff; border: 1px solid #d8dee4; border-radius: 10px; padding: 14px 16px; }}
.card .k {{ color: #57606a; font-size: 12px; }}
.card .v {{ font-size: 22px; font-weight: 650; margin-top: 4px; }}
section {{ background: #fff; border: 1px solid #d8dee4; border-radius: 12px; padding: 18px 20px; margin-bottom: 20px; overflow-x: auto; }}
h2 {{ font-size: 18px; margin: 0 0 12px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
th, td {{ border-bottom: 1px solid #eaeef2; padding: 8px 9px; text-align: left; vertical-align: top; white-space: nowrap; }}
th {{ background: #f6f8fa; color: #57606a; font-weight: 600; }}
tr.first td {{ background: #ecfdf3; font-weight: 600; }}
tr.danger td {{ background: #fff1f0; }}
.quadrant {{ max-width: 620px; width: 100%; height: auto; display: block; margin: 0 auto; }}
.hint {{ color: #57606a; font-size: 13px; line-height: 1.6; }}
code {{ background: #eff1f3; padding: 1px 5px; border-radius: 4px; }}
</style></head><body><main>
<h1>FDE 行业速成 · 算账与机会面板</h1>
<div class="meta">root: <code>{esc(root)}</code> · 数据来自 <code>process-metrics.md</code> / <code>opportunities.md</code> · 仅供研究，不构成投资建议</div>
<div class="cards">
<div class="card"><div class="k">每天人力成本</div><div class="v">{totals['labor']:,.2f} 元</div></div>
<div class="card"><div class="k">每天风险成本</div><div class="v">{totals['risk']:,.2f} 元</div></div>
<div class="card"><div class="k">改进上限 / 天</div><div class="v">{totals['ceiling']:,.2f} 元</div></div>
<div class="card"><div class="k">改进上限 / 年（250 天）</div><div class="v">{totals['ceiling'] * 250:,.2f} 元</div></div>
</div>
<section><h2>1. 四个数字与成本</h2>
<table><thead><tr><th>ID</th><th>业务域</th><th>环节</th><th>谁做</th><th>耗时(分)</th><th>日频次</th><th>出错率</th><th>单次代价</th><th>人力单价</th><th>人力/天</th><th>风险/天</th><th>改进上限/天</th><th>信心</th></tr></thead>
<tbody>{total_rows or '<tr><td colspan="13">还没有填写 process-metrics.md</td></tr>'}</tbody></table>
<p class="hint">数字不全的行不计入合计；人力单价必须来自 HR/财务或明确标“估算”。</p></section>
<section><h2>2. 机会象限：先右后上</h2>
{quad}
<table><thead><tr><th>机会</th><th>信号数</th><th>业务价值</th><th>可行性</th><th>数据可得性</th><th>政治阻力</th><th>红灯</th><th>改进上限/天</th></tr></thead>
<tbody>{op_rows or '<tr><td colspan="8">还没有填写 opportunities.md</td></tr>'}</tbody></table>
<p class="hint">第一项目建议：<strong>{esc(first) or '暂无（需要价值/可行性≥4 且无红灯）'}</strong>。选第一象限里最靠右的，不是价值最高的。</p></section>
</main></body></html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Render ramp dashboard HTML")
    parser.add_argument("--root", default="ramp")
    parser.add_argument("--out", default="")
    args = parser.parse_args()
    root = Path(args.root)
    out = Path(args.out) if args.out else root / "dashboard.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(root), encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
