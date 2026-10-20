# 示例运行：网络文学（compact 8 文件）

这是用 `scripts/init_ramp.py` 生成、用公开资料 + 行业包填完的一次完整运行，验证 skill 不只对煤层气有效，用来展示「填完的 `ramp/` 长什么样」。

## 重要说明

- **不是真实客户项目**：客户名、访谈对象、修正内容都是虚构示例，只用于演示格式；`verification-list.md` 的修正记录逐条标了「虚构示例」。
- **不是模板**：模板在 [`../../templates/`](../../templates/)；这里是填好的结果。
- **不是权威行业报告**：所有数据来自公开源，术语没有客户校准（0 个 verified），规划都标了来源性质。
- 本示例已迁移到 **compact 8 文件**：`decision-brief.md`、`chain.md`、`glossary.md`、`business.md`、`verification-list.md`、`brief.md`、`sources.jsonl`、`state.json`（`sources.md` 为按需生成的可读清单）。

## 怎么看（建议顺序）

1. `decision-brief.md`：第 0 步的决策、拍板人、成功标准、干系人。
2. `chain.md`：行业怎么赚钱、链上有谁、什么关系（含 mermaid）。
3. `business.md`：业务域 + 流程 + 活动表。
4. `glossary.md` + `verification-list.md`：行话、待验证、修正记录、开放问题。
5. `brief.md`：见客户前的一页纸。
6. `sources.md`：所有来源的清单（编号、标题、发布方、日期、链接）。
7. `state.json`：`mode: explore`、provenance、计数；示例不会通过 `--client` 门禁，这是刻意设计。

## 复现

```bash
python3 scripts/init_ramp.py --industry "网络文学" --out ramp
python3 scripts/validate_artifacts.py --root ramp
python3 scripts/readiness.py --root ramp
```
