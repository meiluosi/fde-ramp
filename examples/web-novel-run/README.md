# 示例运行：从空模板走完四步（网络文学）

这是用 `scripts/init_ramp.py` 生成、再用公开资料 + 行业包 `industries/web-novel/` 填完的一次完整 `ramp/` 运行，用来展示「填完的工作区长什么样」，并验证 `fde-ramp` 的四步流程**不只对煤层气有效**。

## 重要说明

- **不是真实客户项目**：客户名、访谈对象、修正内容都是虚构示例，只用于演示格式；`corrections.md` 的 5 处修正已逐条标「虚构示例，只演示记录格式」。
- **不是模板**：模板在 [`../../templates/`](../../templates/)；这里是填好的结果。
- **不是权威行业报告**：所有数据来自公开源（34 条，见 `sources.md`），术语没有客户校准（**0 个已验证**），规划都标了 自述/转述/推断。
- **内容来源**：价值链/链路/业务域/活动表/术语/流程/待验证/20 问均从行业包 [`../../industries/web-novel/`](../../industries/web-novel/) 复制，仅做**轻量适配**（标题加「示例运行」、去掉指向行业包内 `players.md` 的悬空引用）；`.mmd` 由各文件第一个 mermaid block 提取。

## 怎么看（建议顺序）

1. `plan.md`：四步清单和完成情况（第 4 步标了"模拟访谈"）。
2. `value-chain.md` + `chain.md`：行业怎么赚钱、链上有谁、什么关系。
3. `domains.md` → `flow.md` → `activities.md`：业务域 → 流程 → 16 列活动表（25 行）+ 关键环节展开 10 个（含 2026 中报/季报的真实例子）。
4. `glossary.md` + `verification-list.md`：77 个候选术语 + Top 15 待验证。
5. `corrections.md`：第 4 步怎么记（注意：全部是虚构示例）。
6. `brief.md` + `readiness.md` + `drill-scorecard.md`：见客户前的一页纸、自检、对话演练。
7. `sources.md`：34 条来源（编号、标题、发布方、日期、等级、链接）。

## 怎么复现

```bash
cd ~/Documents/GitHub/fde-ramp

# 1) 生成空工作区
rm -rf /tmp/web-novel-demo
python3 scripts/init_ramp.py --industry "网络文学" \
    --customer "某中型网文平台（示例）" \
    --persona "内容/运营负责人（示例）" \
    --deadline "见客户前" --out /tmp/web-novel-demo

# 2) 复制行业包 9 个文件（sources.jsonl + 8 份 md），提取 mermaid block 到 .mmd
#    然后补 plan/corrections/brief/readiness/drill-scorecard/calibration-log/README
#    本目录就是做完这一步的结果

# 3) 渲染来源清单 + 打分 + 严格校验
python3 scripts/render_sources.py --root /tmp/web-novel-demo
python3 scripts/readiness.py --root /tmp/web-novel-demo \
    --set structure=3 --set language=3 --set players=3 \
    --set decision=3 --set dialogue=3
python3 scripts/validate_artifacts.py --root /tmp/web-novel-demo --strict
python3 scripts/readiness.py --root /tmp/web-novel-demo --check
```

## 文件清单

| 文件 | 回答什么问题 |
|---|---|
| `plan.md` | 四步做到哪了 |
| `value-chain.md` / `value-chain.mmd` | 行业怎么赚钱、卡在哪 |
| `chain.md` / `chain.mmd` | 每段有谁、什么关系、下一步想干什么 |
| `domains.md` | 平台分几块业务（8 个域） |
| `flow.md` / `flow.mmd` | 每块业务怎么走、哪里不确定（12 个 ❓ 节点） |
| `activities.md` | 一行一个环节（16 列 × 25 行）+ 关键环节展开 10 个（签约/审核/推荐/付费免费/广告/打赏/版权/出海/结算/作者运营，带真实例子与 [Sxx]） |
| `glossary.md` | 77 个候选术语 + 12 组易混对（0 个已验证） |
| `verification-list.md` | Top 15 待验证项 + 「我画了…您帮我改」问法 |
| `corrections.md` | 被一线改了什么（**模拟访谈，5 处**） |
| `open-questions.md` | 20 道资深从业者会怎么考你 |
| `brief.md` | 见谁、问什么、怕什么 |
| `readiness.md` | 五个维度还差什么 |
| `drill-scorecard.md` | 一次模拟对话演练的评分 |
| `calibration-log.md` | 术语校准日志（本示例无客户文档，0 条） |
| `sources.jsonl` / `sources.md` | 34 条来源与人类可读清单 |
| `state.json` | 自检脚本用的状态（blocks 全 done、五维 3 分、计数） |

## 验证结果（生成时实测）

```
validate_artifacts.py --strict   → OK（exit 0）
readiness.py --check             → gate: PASS（exit 0）
sources: 34  terms: 77  verification: 15  corrections: 5  guessed nodes: 12
chain players: 14  relations: 10  domains: 8  activities: 25
glossary statuses: public 39 / needs-customer 36 / unsure 2 / 已验证 0
```

> 与煤层气示例（31 条来源、78 术语、36 行活动表、14 列活动表）相比，本示例的差异是：活动表为 16 列、来源更新到 2026-10、行业结构由「订阅+版权」转向「广告最大」。**流程与门槛完全一致，说明 skill 不依赖单一行业。**

## 已知局限（真实项目必须补）

1. 客户内部的收入四块占比、签约合同条款、审核组织、版权台账——全部未知（见 `verification-list.md`）。
2. 5 处修正是虚构的，真实修正必须由人现场访谈得到；`corrections.md` 里标了"模拟"。
3. 术语 0 个已验证；`readiness.md` 的 3 分是示例自评，不代表真实项目可交付。
