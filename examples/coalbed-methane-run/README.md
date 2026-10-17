# 示例运行：从空模板走完四步（煤层气）

这是用 `scripts/init_ramp.py` 生成、再用公开资料 + 模拟访谈填完的一次完整运行，用来展示「填完的 `ramp/` 长什么样」。

## 重要说明

- **不是真实客户项目**：客户名、访谈对象、修正内容都是虚构示例，只用于演示格式。
- **不是模板**：模板在 [`../../templates/`](../../templates/)；这里是填好的结果。
- **不是权威行业报告**：所有数据来自公开源，术语没有客户校准，规划都标了来源性质。

## 怎么看

1. 先看 `plan.md`：四步清单和完成情况。
2. 再看 `value-chain.md` + `chain.md`：行业怎么赚钱、链上有谁、什么关系。
3. 然后 `domains.md` → `flow.md` → `activities.md`：客户业务怎么拆。
4. `glossary.md` + `verification-list.md`：行话和待验证。
5. `corrections.md`：第 4 步怎么记（注意：模拟访谈）。
6. `brief.md` + `readiness.md`：见客户前的一页纸和自检。
7. `sources.md`：所有来源的清单（编号、标题、发布方、日期、链接）。

## 怎么复现

```bash
cd ~/Documents/GitHub/fde-ramp
rm -rf /tmp/ramp-demo
python3 scripts/init_ramp.py --industry "煤层气" --customer "某公司" --persona "技术负责人" --deadline "见客户前" --out /tmp/ramp-demo
# 然后按四步填；填完：
python3 scripts/render_sources.py --root /tmp/ramp-demo
python3 scripts/validate_artifacts.py --root /tmp/ramp-demo --strict
python3 scripts/readiness.py --root /tmp/ramp-demo
```

## 文件清单

| 文件 | 回答什么问题 |
|---|---|
| `plan.md` | 四步做到哪了 |
| `value-chain.md` | 行业怎么赚钱、卡在哪 |
| `chain.md` | 每段有谁、什么关系、下一步想干什么 |
| `domains.md` | 客户分几块业务 |
| `flow.md` | 每块业务怎么走、哪里不确定 |
| `activities.md` | 一行一个环节：做什么/谁做/影响谁/什么工具/为什么 |
| `glossary.md` | 50 个行话小抄（候选池） |
| `verification-list.md` | 哪些必须问、怎么问 |
| `corrections.md` | 被一线改了什么（示例为模拟） |
| `open-questions.md` | 资深从业者会怎么考你 |
| `brief.md` | 见谁、问什么、怕什么 |
| `readiness.md` | 五个维度还差什么 |
| `sources.md` | 来源清单 |
| `state.json` | 自检脚本用的状态 |

## 验证结果（生成时）

- `validate_artifacts.py --strict`：通过
- `readiness.py --check`：通过（示例分数）
- 来源 31 条、术语 78 行、活动表 36 行（16 列）、玩家 15 家/类、关系 20 条、业务域 8 个
