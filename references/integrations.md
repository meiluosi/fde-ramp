# 与现有插件 / skill 的组合

> **M1.5 适配层（具体工具名/导出路径/导入脚本）见 [`adapters.md`](adapters.md)。** 下面是原则性说明。

> 原则：**本 skill 负责「速成流程 + 对话就绪」，不重造研究能力。** 能借的借，借不到就降级，绝不因为没装插件而卡住。

## 0. 开工前自检（30 秒）

按顺序检查（看工具列表 / `dsh plugin list` / `~/.dsh/skills`）：

| 依赖 | 怎么判断有没有 | 没有时 |
|---|---|---|
| `dsh-industry-research` | 工具里有 `industry_map` / `industry_track` / `company_scan` | 用本 skill 的 `chain.md` + `web_search`/`web_fetch` |
| `dsh-scout` | 工具里有 `scout_start` / `scout_add_claim` / `scout_report` | 用 `sources.jsonl` 的 tier 手工做证据分级 |
| `dsh-kb` | 设置里/侧栏有知识库入口，或工具里有 `kb_*` | 客户文件路径写进 `sources.jsonl`，按需 `read` |
| `material-audit` skill | 技能列表里有 | 用 `templates/business.md` 手工抽 |
| `gap-rehearsal` skill | 技能列表里有 | 用 `verification-list.md` 自问自答 |
| `chain-authoring` skill | 技能列表里有 | 只交 mermaid + markdown |
| `web_search` / `web_fetch` | 工具列表里有 | 只能靠客户给的材料；明确告知用户「公开源覆盖不足」 |

> 不要假设插件一定存在；不要因为插件不存在就停止。先降级跑通，再提示用户可装什么。

## 1. 与 `dsh-industry-research` 的组合（最强）

**它提供**：`industry_map`（chain.json + chain.svg，节点/边/指标槽，指标必须带 sourceRef）、`industry_track`（政策/新闻跟踪，SHA-256 快照）、`company_scan`（公司卡）、`industry_report`（可审计报告）、两套方法论 skill。

**怎么用**：

- 第 1 步：先调 `industry_map` 建行业链，再把 `chain.json` 里的节点/指标抄进 `chain.md`，保留 `sourceRef`；
- 第 1 步：用 `industry_track` 抓近 12 个月政策/新闻，产出 `sources.jsonl` 的一部分；
- 第 3 步：用 `company_scan` 生成客户公司卡，作为业务流程与活动表的上游输入；
- **不要**把 `industry_report` 直接当交付物——它是报告，不是对话就绪度；可以把它当 第 1 步 的加速器。

**注意**：它的 `industry_map` 指标要求 `sourceRef`，这正好和本 skill 的证据纪律一致；如果它报错缺来源，不要绕过，补来源。

## 2. 与 `dsh-scout` 的组合（客户尽调）

**它提供**：E0–E3 证据分级、公司主体核验、11 维覆盖度、PROCEED/VERIFY/STOP、访谈问题清单、导出/导入。

**怎么用**：

- 客户是陌生理公司：先跑 `scout_start` → `scout_search` → `scout_add_source` → `scout_verify_identity`，把结论并入 `chain.md` 的「客户」节；
- 把它的 `scout_questions` 作为 `verification-list.md` 的输入；
- 它证据等级比本 skill 更细，冲突时以它的 E3 官方核验为准。

**注意**：它评的是「公司/岗位值不值得推进」，不是「行业能不能对话」；不要拿它的报告替代 第 2 步/3/4。

## 3. 与 `dsh-kb` 的组合（素材沉淀）

**它提供**：raw → wiki 自动蒸馏、全文检索、问 AI 带来源、版本回滚。

**怎么用**：

- 客户给的 PDF/制度/研报，先丢进 `dsh-kb`；
- 术语校准阶段用 kb 的全文检索找「客户原句」；
- 访谈记录/修正也可以进 kb，形成团队资产。

**注意**：kb 是沉淀层，不是学习路径；不要用「上传了 50 份资料」代替「50 个词 + 一张图 + 一次访谈」。

## 4. 与你已有的三个 skill 的组合

| skill | 在本流程里的位置 |
|---|---|
| `material-audit` | 客户给了架构/流程/制度文档 → 先抽出结构图与决策缺口，直接作为 第 3 步 的输入 |
| `gap-rehearsal` | 待验证清单里「必须内部拍板」的项（如报价策略、方案取舍）→ 变成一次决策演练 |
| `chain-authoring` | 产品化阶段：把价值链做成可交互的「选边」页面，用于新人培训或客户共创 |

## 5. 与通用研究插件的组合（可选）

| 插件 | 用途 | 注意 |
|---|---|---|
| `@creait/dsh-research-mode` | 需要多轮自适应深研 + 引用报告时 | 产出是报告，仍需 第 4 步 |
| `dsh-socrates` | 问题本身不清楚，需要先澄清再研究 | 适合开工前定题 |
| `@stifer/dsh-harvest` | 多平台（含社交/视频）找线索 | 社交源只能作 D 级，需交叉验证 |
| `dsh-debate` | 对关键判断做正反方压力测试 | 适合写 brief 的「反对意见」节 |
| `dsh-scout` | 公司尽调 | 见上 |

## 6. 推荐组合（煤层气案例）

```text
dsh-industry-research  → industry_map（产业链）/ industry_track（政策）/ company_scan（客户）
dsh-scout              → 客户主体核验 + 访谈问题
dsh-kb                 → 客户 PDF/制度沉淀 + 术语原句检索
material-audit         → 客户给的技术/流程文档抽结构
fde-ramp（本 skill）    → 四步编排 + 术语校准 + 流程图 + 被否定 + 自检
```

## 7. 产品化时的接口预留

插件化后，本 skill 的每个 Block 对应一组工具：

| 工具 | 对应 | 输入 | 输出 |
|---|---|---|---|
| `ramp_init` | 开工 | industry/customer/persona/deadline | `ramp/` 骨架 + `state.json` |
| `ramp_map` | 第 1 步 | 研报/年报/监管目录 | `chain.md` + `sources.jsonl` |
| `ramp_chain` | 第 1 步 | 分段/玩家/关系 | `chain.md` + `chain.mmd` |
| `ramp_domains` | 第 3 步 | 业务域划分 | `business.md` |
| `ramp_activities` | 第 3 步 | 流程拆活动 | `business.md` |
| `ramp_glossary` | 第 2 步 | 候选词 + 客户文档 | `glossary.md`（带状态） |
| `ramp_flow` | 第 3 步 | 地图 + 访谈 | `business.md` + `verification-list.md` |
| `ramp_verify` | 第 3/4 步 | 待验证项 | 更新清单与状态 |
| `ramp_brief` | 收尾 | 对象/目标 | `brief.md` |
| `ramp_score` | 收尾 | 产物 | `readiness.md` |

详见 `plugin/roadmap.md`。
