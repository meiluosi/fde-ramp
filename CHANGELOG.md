# Changelog

## v0.3.3 · 2026-10-18

- 活动表再加两列：「谁验收/签字」「是否外包/自营」，共 16 列；模板、案例 36 行、示例 ramp、SKILL/README/QUICKSTART/method 同步。
- 示例 ramp 重新通过 strict validator 与 readiness 自检。

## v0.3.2 · 2026-10-18

- 产业链表达：`chain.md` 的「分段总表」改为「产业链总览：每段在干啥」，加「大白话」列；新增两张 mermaid 图（链路一眼看懂、玩家关系图），模板同步。
- 活动表增列：新增「多久一次/什么触发」「常见异常/出错后果」「上下游交接（含记录/验收）」三列；模板、案例 36 行、示例 ramp 同步。
- 来源补充：新增 S30（甲烷排放控制行动方案）、S31（煤层气产业政策全文）；案例包与示例 ramp 来源增至 31 条，并生成 `sources.md`。
- 示例 ramp 刷新（`examples/coalbed-methane-run/`），重新通过 strict validator 与 `readiness --check`。
- 文档同步：SKILL / README / QUICKSTART / method / map-and-negate / case README。

## v0.3.1 · 2026-10-18

- 新增「客户什么都没给」的自学模式：不等待材料，按公开资料画；客户相关判断标「待客户确认」；术语最高「公开说法」；见客户先交底。
- 新增来源清单：`sources.jsonl` 是给脚本的台账，`scripts/render_sources.py` 生成给人看的 `sources.md`（编号/标题/发布方/日期/等级/链接）；`validate_artifacts.py` 会检查来源清单是否漏项。
- 新增完整跑通示例：`examples/coalbed-methane-run/`，从 `init_ramp.py` 生成，走完四步，通过 strict validator 与 `readiness.py --check`；含 5 处明确标注为「模拟访谈」的修正，只用于演示格式。
- 所有模板加「依据与来源」末尾说明；`selftest.py` 17 项；README/QUICKSTART/method/evidence 同步。

## v0.3.0 · 2026-10-18

按用户反馈做“去时间化 + 新手可读 + 说清谁填写”：

- 删除所有固定时长、按天排期的表述；统称为「第 1–4 步」，不设固定时长。
- SKILL.md 大幅改写：短句、少术语、每步先讲“要回答什么”，再讲怎么做；术语第一次出现给解释。
- 新增「AI 填大头，人做三件事」与「AI 接到任务先问 6 件事」，明确模板是空壳、案例包是 AI 填好的示例。
- README / QUICKSTART / method / readiness-rubric / source-hunting / templates/plan / plugin roadmap 同步改写；`template/plan.md` 改为四步清单。
- 案例包与 examples 由 cbm-researcher 同步去时间化、示例文件改名（`day1/2/3-*` → `step1/2/3-*`），并补「这是示例不是模板」说明。
- 行为不变：validator / readiness / selftest 门槛逻辑不改；selftest 仍 16/16。

## v0.2.1 · 2026-10-18

第三轮复核（`REVIEW3.md`：0 BLOCKER / 0 MAJOR / 7 MINOR）后的收尾，主要修案例包旧口径与计数精度。

- `flow_guess_count` 只统计「节点信心表」（表头含信心、首列 #/节点/环节，且排除待验证表），案例 flow.md 从 19 降为 5（主流程 3 + 审批链 2）；selftest 增加反例。
- 案例 README：来源 S01…S29、四步法映射补 `chain.md` / `domains.md` / `activities.md`、文件数口径更新。
- `references/evidence.md` 证据闸门补齐玩家/关系/域/活动四项；引用示例统一零填充 `S01`。
- `references/map-and-negate.md` 新增 §8.6/§8.7：带链路图、域图去被否定的话术与规则。
- 案例 `sources.jsonl` 29 条全部补 `sourceKind`（S27 = practitioner）；activities 去掉厂商示例。
- 模板 `chain/domains/activities` 顶部加「不要改表头关键词」警告；根 README 首屏/目录/路线同步 v0.2.1。
- `selftest.py` 从 15 项增到 16 项（新增「待验证表的 ❓ 不计入节点猜测」回归）。

## v0.2.0 · 2026-10-18

按用户本轮补充的三条方法扩展：

### 1. 全链路关系（第 1 步）
- 新增 `chain.md` + `chain.mmd`：分段 → 每段玩家（≥10）→ 现状/近 12 个月动作/未来规划（标 `自述/转述/推断`）→ 关系表（供应/采购/股权/合资/技术/客户/渠道/竞争/监管，≥5 条，带证据与信心）。
- 明确纪律：规划不是已发生；没有证据的股权/合作标 ❓；关系类型不许混用。
- 新增模板 `templates/chain.md`、`templates/chain.mmd`；`state.artifacts/counts`、init、validator、readiness 同步。

### 2. 从业者内容源（第 2 步）
- `source-hunting.md` 新增「公众号/知乎/B站/播客/论坛」检索方法与可信度规则。
- `glossary-protocol.md` 新增 Miner D：从业者内容只作候选词/用法例句，不得作关键数字唯一来源；区分科普/软文/广告；记录作者/机构/日期。
- `evidence.md` 新增 `sourceKind`（official/report/practitioner/media/other）与从业者来源规则。

### 3. 业务域 → 流程 → 活动（第 3 步）
- 新增 `domains.md`（3–8 个业务域：目标/负责人/流程/接口/痛点/信心）与 `activities.md`（≥15 行：做什么/谁做/影响谁/工具/业务背景/输入输出/信心/来源）。
- 新增模板 `templates/domains.md`、`templates/activities.md`；`map-and-negate.md` 新增「用活动表访谈」话术与规则。
- 验收与证据闸门：≥3 域、≥10 行活动（目标 15）；readiness 新增玩家/关系/域/活动检查。

### 4. 工程与文档
- `init_ramp.py` 生成 19 个文件；validator REQUIRED/计数/警告同步；selftest 扩到 15 项（v0.2.1 增到 16）；CI 不变。
- README / QUICKSTART / method / readiness-rubric / integrations / plugin roadmap 全部同步 v0.2。
- 案例包 v0.2：新增 chain/domains/activities 与 example-run 样例（由 cbm-researcher 产出）。

## v0.1.2 · 2026-10-18

第二轮复核（`REVIEW2.md`：0 BLOCKER / 0 MAJOR / 5 MINOR）后的收尾。

- `flow_guess_count` 只统计「纯 ❓ 标记单元格」，不再把正文里提到 ❓ 的表格行算作猜测节点。
- `correction_count` 支持 markdown 常见的「标签在上一行、值在下一行缩进」写法，避免做完修正却数成 0。
- 来源引用支持合并写法 `[S03/S04]`、`[S13、S14]`、`[S1, S2]`，并对每一项做存在性校验。
- `references/readiness-rubric.md` 补齐证据闸门：≥5 修正、≥8 来源、≥20 术语、≥5 待验证、`negate=done`。
- 案例包 ❓ 口径修正：主流程 3/14≈21%，全包合计 19 个待验证标记（不再声称主流程 ≥25%）。
- `selftest.py` 扩到 12 项（新增合并引用、下一行修正、正文 ❓ 不误计）。
- README 标注：CI 已提供，需 `git init` 并推送到 GitHub 后生效。

## v0.1.1 · 2026-10-18

第二轮：根据独立验收（`REVIEW.md`，PASS WITH FIXES，0 BLOCKER / 6 MAJOR）修复质量闸门与一致性问题。

### 修复
- **五维门槛统一**：文档与脚本统一为「目标五项≥3；门槛 min≥2、avg≥3、结构/语言≥3，且 ≥5 处 第 4 步 修正」。`readiness.py` 增加证据闸门：来源≥8、术语≥20、待验证≥5、修正≥5、`state.blocks.negate=done`，自报满分不再能 PASS。
- **validator 计数修正**：跳过空表行、汇总表、图例与表头；glossary 只数真实术语行；verification 只数「我猜的是什么」非空行；flow ❓ 只数节点信心表；corrections 只数有非空「实际」的章节；`state.json` 解析失败给清晰 ERROR；扫描改为 `rglob("*.md")`。
- **来源 id 统一**：煤层气案例包 `sources.jsonl` 改为 `S01…S24`，正文与 example-run 全部对齐 `[S#]`，可直接复制进 `ramp/` 通过 validator。
- **`verified` 语义收紧**：`verified` 只认客户文档/一线确认；官方标准/年报等公开源最高到 `public`；案例包因此 0 个 `verified`。
- **产物清单对齐**：`state.artifacts`、`SKILL.md`、validator 的 `REQUIRED` 统一包含 `.mmd`、`calibration-log.md`、`drill-scorecard.md`。
- **统一了步骤表述**（v0.3 起全部去掉时间框架）。
- **候选池写清**：先列 60–80（最多 120）候选，收敛到约 50。

### 新增
- `scripts/selftest.py`：9 个自测（fresh FAIL / complete PASS / 未知引用 / 非法 JSON / 非空目录等）。
- `.github/workflows/ci.yml`：push/PR 跑 selftest。
- `references/source-hunting.md`：3 份研报、客户材料、监管目录的检索路径。
- `templates/calibration-log.md`：术语校准日志。

### 案例包勘误
- 「山西 2015 年利用率」改为「全国」（S06 为全国口径）。
- 储量起算标准的埋深单位改为 m，与单井日产 m³/d 分开。
- glossary 状态统计改为 38 public / 34 needs-customer / 6 unsure（合计 78）。
- example-run 的 ❓ 占比改为 5/14≈36%；Day3 标注修正。
- verification-list 排序规则改为「风险分档 + 综合排序」，与表格实际一致。

## v0.1.0 · 2026-10-18

- skill-first MVP：`SKILL.md` + 7 篇 references + 14 个 templates + 3 个脚本。
- 煤层气案例包：24 条来源、78 词候选术语、Top15 待验证清单、20 道检验题、步骤示例产物。
- 独立验收报告 `REVIEW.md`。
