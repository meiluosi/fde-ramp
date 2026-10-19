# 产品化路线：从 skill 到 DSH 插件

> 目标：把 `fde-ramp` 从「一个 skill」变成「FDE 速成产品」——可安装、可复用、可度量。
> 原则：**skill 先行验证流程，插件只封装被验证过的东西。**

## 1. 产品定位

**一句话**：FDE 的行业对话就绪度系统——不是又一个行业报告生成器，而是帮你在短时间内具备「能和资深从业者聊 30 分钟」的状态，并给出可验证的自检分数。

**与现有插件的差异**：

| 现有 | 它们做什么 | 我们不做什么 | 我们做什么 |
|---|---|---|---|
| `dsh-industry-research` | 产业链图、政策跟踪、公司卡、可审计报告 | 不重造研究引擎，直接复用 | 把研究产物转成「可被一线纠正的图 + 术语卡 + 对话准备」 |
| `dsh-scout` | 公司/岗位尽调、证据分级 | 不重造证据分级 | 把证据边界接到「我猜的/我确认的」上 |
| `dsh-kb` | 知识沉淀、检索 | 不做知识库 | 把知识库当素材源 |
| 通用 deep research | 出报告 | 不拼报告长度 | 拼「对话就绪度」 |

**核心指标**：不是报告字数，而是 **time-to-conversation-ready** 与 **readiness delta**。

## 2. 工具接口（Host 侧）

插件化后注册以下工具（`ctx.tools`）。每个工具都读写 `ramp/` 下的产物，保持与 skill 版兼容。

| 工具 | 输入 | 输出 | 说明 |
|---|---|---|---|
| `ramp_init` | industry, customer, persona, deadline, workspace? | `ramp/` 骨架 + state.json | 幂等；已存在则不覆盖 |
| `ramp_map` | op=build/update, seedFiles?, webDepth? | value-chain.md + sources.jsonl | 可选调用 `industry_map` |
| `ramp_chain` | op=build/update, segment? | chain.md + chain.mmd | 分段/玩家/规划/关系；规划标自述/转述/推断 |
| `ramp_domains` | op=build/update | domains.md | 业务域划分与接口 |
| `ramp_activities` | op=fill/update, domain? | activities.md | 活动表：做什么/谁做/影响谁/工具/背景 |
| `ramp_glossary` | op=candidates/calibrate/lock, customerDocs? | glossary.md（带状态） | 校准必须引用客户文档原句 |
| `ramp_flow` | op=draft/update, confidence? | flow.md + flow.mmd + verification-list.md | 每个节点强制标 ✅/⚠️/❓ |
| `ramp_verify` | itemId, result, evidence?, person? | 更新 verification-list + state | 记录被推翻/确认 |
| `ramp_drill` | persona, difficulty, rounds | drill-scorecard.md + 可选 drills/*.md | 角色扮演 + 评分 |
| `ramp_metrics` | activities + 客户数字 | process-metrics.md（四个数字/成本/上限） | 算账 |
| `ramp_opportunities` | 六个信号 + 四维打分 | opportunities.md（象限/第一项目） | 找机会 |
| `ramp_case` | 客户数字 + 选择 | business-case.md | 一页纸方案 |
| `ramp_brief` | meeting, audience, goal | brief.md | 一页纸 |
| `ramp_score` | auto/evidence | readiness.md + state | 五维评分与门槛 |
| `ramp_status` | — | 当前阶段/计数/缺口 | 给模型与会话面板用 |

**设计约束**：

- 所有工具必须**可降级**：没有 `ctx.web` 时只读本地；没有 `dsh-industry-research` 时用自己的模板。
- 所有写操作幂等，写前备份（`*.bak` 或版本账本）。
- 工具返回结构化摘要（token 友好），长文落盘，用 `present` 展示。

## 3. 数据模型

```
ramp/
  state.json        # 阶段、五维分、计数、产物清单、gaps
  sources.jsonl     # {id,title,url,publisher,published,accessed,tier,usedFor,note}
  value-chain.md/.mmd
  sources.md        # 人看的来源清单（脚本从 sources.jsonl 生成）
  chain.md/.mmd     # 全链路：分段/玩家/现状/规划/关系
  domains.md        # 业务域
  activities.md     # 环节/活动明细（16 列：含频率/异常/交接/验收/外包）
  glossary.md       # 术语表 + 状态 + 近邻对
  flow.md/.mmd      # 节点信心等级
  verification-list.md
  corrections.md
  brief.md
  readiness.md
  process-metrics.md  # 四个数字 + 成本/改进上限
  opportunities.md    # 六个信号 + 四维打分 + 第一项目
  business-case.md    # 一页纸方案
  drill-scorecard.md  # 对话演练评分卡（当前 skill 版）
  drills/             # 可选：每次演练的 transcript + 分数（插件版）
```

**版本账本**（参考 `dsh-industry-research`）：每次写产物追加 `versions.jsonl`，记录路径、SHA-256、时间、变更类型；读取时校验，坏了 fail loud。

## 4. 客户端 UI（Web）

一个侧栏面板「Ramp」：

- **就绪度仪表盘**：五维雷达 + 门槛状态 + 缺口 Top 3；
- **术语卡**：翻卡模式、状态筛选（needs-customer 优先）、近邻辨析；
- **全链路图**：分段/玩家/关系，点击玩家看现状与规划来源（自述/转述/推断）；
- **业务域与活动表**：域地图 + 可编辑活动表（做什么/谁做/影响谁/工具/背景/频率/异常/交接/验收/外包），❓ 行高亮；
- **算账与机会**：四个数字表 + 成本/改进上限 + 六信号打勾 + 四维打分 + 象限图；第一项目高亮；
- **流程图**：渲染 mermaid，❓ 节点高亮；点击标记「已验证/被推翻」；
- **待验证看板**：按风险×成本排序，拖到「已问/已确认/被推翻」；
- **演练室**：选人设 → 多轮对话 → 自动评分卡；
- **Brief 卡**：一页纸，可导出 PDF/Markdown。

## 5. 包形态

```
dsh-fde-ramp/
  package.json          # name: dsh-fde-ramp, type: module, engines.dsh >=0.2
  cordis.patch.yml      # bundle patch：挂 host 工具 + client 面板
  lib/
    index.js            # Host: 注册 ramp_* 工具、读写 ramp/
    client.js           # Client: 侧栏面板
    schema.js           # state/sources/glossary 的校验
  skills/fde-ramp/
    SKILL.md
    references/
    templates/
  industries/
    coalbed-methane/
  scripts/              # 与 skill 版共用
```

- 安装：`dsh plugin --profile web add dsh-fde-ramp`；
- 兼容：DSH `>=0.2.0-0 <0.3.0`，Node `>=22.19`；peer 依赖 `@deepseek-ai/dsh-tools`、`@deepseek-ai/dsh-skill`、`@deepseek-ai/cordis`、`@deepseek-ai/schemastery`；
- 测试：用 `dsh-test-drive` 插件在一次性 profile 里安装并冒烟，再进主力 profile；
- 发布：npm + 一个插件市场 index（含 icon、双语描述、安装目标）。

## 6. 里程碑

| 里程碑 | 内容 | 验收 |
|---|---|---|
| **M0 skill MVP（✅ 已完成，v0.3.3）** | SKILL.md + references + templates + scripts + 煤层气案例 + 端到端 `ramp/` 示例 | `examples/coalbed-methane-run/` 通过 strict validator 与 readiness；selftest 17/17 |
| **M0.5 真实试跑（用户判断可跳过）** | 原计划用真实客户走一遍；用户判断当前版本已可用，跳过 | —（保留为以后可选） |
| **M1 可复制（✅ 已完成，v0.4.0）** | 第二个行业包：网络文学 / 网文写作；「没有客户资料」的走法已写进 SKILL | 行业包 27 条来源、77 词、25 行活动；`examples/web-novel-run/` 通过 strict + readiness |
| **M1.5 组合现有插件（✅ 组合器完成，待真实导出实测）** | `references/adapters.md` + 4 个导入器 + `m15_compose.py`；接 `dsh-industry-research` / `dsh-scout` / `dsh-kb` | 样例导出 4/4 导入成功；待真实环境安装三插件跑一次对比 |
| **M2 工具化（✅ 读 + 写工具）** | 5 个只读工具 + `ramp_metrics_update` / `ramp_activities_update` 写工具；下一步 M3 面板 | 工具可独立跑；真实 headless 读写调用已通过 |
| **M3 UI（🚧 客户端面板已接入，待重启验证）** | 侧栏「算账面板」+ 全屏 overlay + `/fde-ramp/api/snapshot`；四数字表 + 成本卡片 + 机会象限 + 第一项目 | Web 面板可用，状态与文件同步 |
| **M4 发布** | npm 包 + 市场索引 + 文档站 | 外部用户可一键安装并跑通 |

## 7. 验证与指标

**过程指标**：

- 首次 brief 时间 < 2h；
- 从零到 readiness 门槛 ≤ 7 天；
- 来源覆盖率（有来源的关键节点 / 全部关键节点）≥ 70%；
- 待验证清单关闭率（访谈后尽快）。

**结果指标**：

- 演练评分 delta（基线 → 终局）≥ +1.5；
- 一线访谈中「实质修正」≥ 5 处/次；
- 客户侧盲评：10 个问题的质量 ≥ 4/5；
- time-to-conversation-ready（自报 + 同伴评）；
- 全链路玩家/关系覆盖（≥10 / ≥5）；
- 业务域覆盖（≥3）与活动行数（≥15）；
- 方案模式：重点环节四个数字覆盖率、改进上限合计、第一项目选择理由。

**质量红线**：

- 高影响结论无来源 = 0；
- 编造 URL/文号/数字 = 0（validator + 人工抽检）；
- 未做 第 4 步 就标「已就绪」= 0。

## 8. 推荐推进顺序（当前建议）

按「先验证，再放大」排：

1. **第二个行业包（✅ 已完成）**：网络文学 / 网文写作；行业包 + 完整 `ramp/` 示例均通过严格检查。真实试跑按用户判断跳过。
2. **（可选）真实试跑**：以后有真实客户时再补；第 4 步仍然必须由人做。
3. **组合现有插件**：`dsh-industry-research` / `dsh-scout` / `dsh-kb`，先把 第 1–3 步 的重复劳动降下来；这一步不改 skill 的对外形态，只加适配层。
4. **插件化 M2/M3**：把成熟的工具（`ramp_chain` / `ramp_activities` / `ramp_metrics` / `ramp_opportunities` / `ramp_score`）先包成 Host 工具，再做 UI；不要一上来做完整面板。
5. **发布 M4**：npm + 市场索引 + 文档站；先小范围给 3–5 个 FDE 试用，再公开。

**决策点**：
- 先自用还是对外发布？（决定是否做多租户/权限）
- 第二个行业选哪个？（最好是你手上有真实客户/资料的那个）
- 是否离线/私有化？（客户现场可能无外网）

## 9. 风险与未决问题

| 风险 | 应对 |
|---|---|
| DSH API 处于 0.2.x，插件接口可能变 | skill 先行；工具层薄；CI 兼容性测试 |
| 行业数据可得性（付费/内网） | 公开源 + 客户文档双轨；离线模式 |
| 模型幻觉/口径错误 | 证据分级 + 客户文档校准 + validator |
| 「就绪度」主观 | 五维行为锚点 + 演练评分 + 客户侧盲评 |
| 行业包维护成本 | 先做 1–2 个；模板化；社区贡献 |
| 从业者内容源（公众号/知乎等）版权与质量 | 只摘一句、标作者/日期、区分软文；不整段复制 |

**需要产品决策的问题**：

1. 目标用户是「自己用」还是「卖给/给其他 FDE 用」？（决定 UI 与多租户）
2. 行业包由谁维护？（决定是否做包市场）
3. 是否要离线/私有化（客户现场可能无外网）？（决定检索与模型调用架构）
