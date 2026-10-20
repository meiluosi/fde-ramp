#!/usr/bin/env python3
"""Calculate the daily labor/risk cost and improvement ceiling for one process step.

Usage:
  python3 scripts/calc_process.py --minutes 12 --freq 200 \
      --error-rate 0.03 --cost-per-error 50 --hourly-rate 60

Formulas:
  labor/day = minutes / 60 * freq * hourly_rate
  risk/day  = error_rate * freq * cost_per_error
  ceiling   = labor/day + risk/day
  annual    = ceiling * days (default 250)
"""
from __future__ import annotations

import argparse
import json


def main() -> int:
    parser = argparse.ArgumentParser(description="Process step cost calculator")
    parser.add_argument("--minutes", type=float, required=True, help="平均耗时（分钟/次）")
    parser.add_argument("--freq", type=float, required=True, help="日频次（次/天）")
    parser.add_argument("--error-rate", type=float, default=0.0, help="出错率（0–1，如 0.03 表示 3%）")
    parser.add_argument("--cost-per-error", type=float, default=0.0, help="单次代价（元/次）")
    parser.add_argument("--hourly-rate", type=float, required=True, help="人力单价（元/小时）")
    parser.add_argument("--days", type=int, default=250, help="年化工作日（默认 250）")
    parser.add_argument("--realization", type=float, default=1.0, help="可实现比例 0–1（保守估计）")
    parser.add_argument("--build-cost", type=float, default=0.0, help="一次性建设成本（元）")
    parser.add_argument("--run-cost-per-day", type=float, default=0.0, help="每天运行成本（元）")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    if args.minutes < 0 or args.freq < 0 or args.hourly_rate < 0:
        parser.error("minutes / freq / hourly-rate 不能为负")
    if not 0 <= args.error_rate <= 1:
        parser.error("error-rate 用 0–1 表示百分比，例如 0.03")
    if not 0 <= args.realization <= 1:
        parser.error("realization 用 0–1，例如 0.4 表示实现 40%")

    labor = args.minutes / 60.0 * args.freq * args.hourly_rate
    risk = args.error_rate * args.freq * args.cost_per_error
    ceiling = labor + risk
    annual = ceiling * args.days
    realized = annual * args.realization
    run_annual = args.run_cost_per_day * args.days
    net_annual = realized - args.build_cost - run_annual
    payback = (args.build_cost / (realized - run_annual)) if realized > run_annual and args.build_cost > 0 else None

    result = {
        "minutes": args.minutes,
        "freq_per_day": args.freq,
        "error_rate": args.error_rate,
        "cost_per_error": args.cost_per_error,
        "hourly_rate": args.hourly_rate,
        "labor_cost_per_day": round(labor, 2),
        "risk_cost_per_day": round(risk, 2),
        "ceiling_per_day": round(ceiling, 2),
        "ceiling_per_year": round(annual, 2),
        "days_per_year": args.days,
        "realization": args.realization,
        "gross_annual": round(annual, 2),
        "realized_annual": round(realized, 2),
        "build_cost": args.build_cost,
        "run_cost_annual": round(run_annual, 2),
        "net_annual": round(net_annual, 2),
        "payback_years": round(payback, 3) if payback is not None else None,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(f"每天人力成本: {labor:,.2f} 元")
    print(f"每天风险成本: {risk:,.2f} 元")
    print(f"改进上限:     {ceiling:,.2f} 元/天")
    print(f"毛年化上限:   {annual:,.2f} 元/年（{args.days} 个工作日）")
    print(f"可实现收益:   {realized:,.2f} 元/年（可实现比例 {args.realization:.0%}）")
    print(f"净收益/年:    {net_annual:,.2f} 元/年（扣建设 {args.build_cost:,.0f} + 运行 {run_annual:,.0f}）")
    if payback is not None:
        print(f"回收期:       {payback:.2f} 年")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
