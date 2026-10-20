# fde-ramp · 快速入门一个行业

> 给第一次接触某个行业的 FDE / 售前 / 交付 / 顾问用：**在见客户前，把这个行业的基本盘搭起来。**
>
> 产出不是行业报告，而是：一张会被人改的全链路图 + 一组业务域/流程/活动表 + 50 词行话小抄 + 一份待验证清单 + 一次被一线员工改图的记录 + 一个自检分数。

## 这是什么，不是什么

| 是 | 不是 |
|---|---|
| 一套让 AI 帮你查资料、填图、填表、标出「我不确定」的流程 | 一份行业报告的写作模板 |
| 一个「先画错图、再拿去被一线改」的方法 | 读一堆资料就能自动变内行 |
| 空模板 + AI 填好的示例，帮你快速开始 | 标准答案，或可以照抄的行业结论 |

**三个东西别搞混：**

1. **流程说明**：`SKILL.md` 和 `references/`，告诉 AI 和人每一步做什么。
2. **空模板**：`templates/`，AI 生成 `ramp/` 工作区时自动复制，内容要 AI 去填。
3. **填好的示例**：`industries/coalbed-methane/`（煤层气）和 `industries/web-novel/`（网络文学），AI 用公开资料填出来的行业案例，用来看「填完长什么样」，不是答案。

## 怎么用（四步）

| 步骤 | 做什么 | 产出 |
|---|---|---|
| 第 1 步 · 画地图 | 读 3 份行业报告 + 客户年报/官网 + 监管目录；画钱怎么流；再画全链路关系：每段有谁、什么关系、下一步想干什么 | `value-chain.md`、`chain.md`、`sources.jsonl` |
| 第 2 步 · 行话小抄 | AI 先列 60–80 个候选（研报 + 公众号/知乎/B站/播客的从业者科普）→ 用客户文档校准 → 收敛到约 50 词 | `glossary.md`、`calibration-log.md` |
| 第 3 步 · 拆业务 | 先分业务域 → 再画流程 → 再拆活动表（做什么/谁做/影响谁/工具/为什么/多久一次/常见异常/上下游交接/谁验收/是否外包） | `domains.md`、`flow.md`、`activities.md`、`verification-list.md` |
| 第 4 步 · 去被改 | 带链路图、域图、活动表去找一线员工：「我画了张图，肯定有不对的地方，您帮我改改」 | `corrections.md` + 改过的图/表 |

**不设固定时长。** 资料少就快，约不到人就慢；但第 4 步不能省——没有它，前面三步只是练习。

### 可选第 5 步：方案模式（算账 + 找机会）

如果目标不只是「能对话」，而是「给客户提 AI 改造方案」，加做第 5 步：

- 给重点环节标四个数字：**耗时、日频次、出错率、单次代价**；再问「谁做、什么职级」，找 HR/财务要**人力单价**；
- 算两个成本：`每天人力成本 = 耗时÷60×日频次×人力单价`，`每天风险成本 = 出错率×日频次×单次代价`，相加是**改进上限**；
- 用六个信号找 AI 机会（重复人工判断 / 信息散在多系统 / 大量非结构化文档 / 有标准但靠人记 / 流程大量等待 / 有人在偷偷自救）；
- 四个维度打分：业务价值、可行性、数据可得性、政治阻力；数据/政治红灯先解决；
- 第一个项目选**第一象限最靠右**的（最容易落地），不是最靠上的。

详见 [opportunity-analysis.md](references/opportunity-analysis.md)，模板在 `templates/process-metrics.md` / `templates/opportunities.md` / `templates/business-case.md`。

## 谁填？

- **AI 填大头**：查资料、填地图、整理小抄、画流程、拆活动表、标出猜测、写会前 brief。
- **人做三件事**：给客户材料；去现场被一线改；判断哪些能对外说。
- **来源**：AI 找的资料都要在 `sources.jsonl` 留底，并在正文用 `[S01]` 标注；最后生成一份人看得懂的 `sources.md`（谁发的、什么时候、什么等级、链接）。客户什么都没给时，这份清单就是你「有依据」的证明。
- 自检脚本会检查「是不是真的做了」：光把五个维度给自己打高分，不会通过。

## 快速开始

### 作为 DSH skill 安装

```bash
ln -s ~/Documents/GitHub/fde-ramp ~/.dsh/skills/fde-ramp
```

然后在会话里说：

> 帮我用 fde-ramp 快速入门煤层气行业，先画全链路关系。

> 安装后如果技能列表里没出现，重启一下 DSH 会话或应用。

### 独立使用（不装 skill 也能跑）

```bash
cd ~/Documents/GitHub/fde-ramp
python3 scripts/init_ramp.py --industry "煤层气" --customer "某公司" \
    --persona "技术负责人" --deadline 2026-10-25
python3 scripts/render_sources.py --root ramp   # 生成 sources.md（人看的来源清单）
python3 scripts/validate_artifacts.py --root ramp
python3 scripts/readiness.py --root ramp
python3 scripts/selftest.py        # 23 项自测

# 可选：算某个环节的成本/改进上限
python3 scripts/calc_process.py --minutes 12 --freq 200 --error-rate 0.03 --cost-per-error 50 --hourly-rate 60
```

若已作为 skill 安装，脚本在 `~/.dsh/skills/fde-ramp/scripts/` 下，可在任意工作区用绝对路径调用。

## 目录结构

```
fde-ramp/
  SKILL.md                     # 主入口：AI 和人照着做
  QUICKSTART.md                # 一页纸：先做什么
  references/                  # 每一步的详细说明
    method.md                  # 为什么这么设计、每一步怎么做
    readiness-rubric.md        # 五个维度怎么打分
    glossary-protocol.md       # 行话怎么找、怎么校准
    map-and-negate.md          # 怎么画图、怎么请人改
    evidence.md                # 来源、口径、待验证规则
    personas.md                # 一线/技术/商务/管理层等角色
    integrations.md            # 和现有插件/技能配合
    source-hunting.md          # 去哪找报告、客户材料、监管文件
    opportunity-analysis.md    # 四个数字、六个 AI 信号、四维打分、第一项目选择
    adapters.md                # 与 dsh-industry-research / dsh-scout / dsh-kb 的具体接法
  templates/                   # 空模板（AI 填）
  scripts/
    init_ramp.py               # 生成 ramp/ 工作区
    render_sources.py          # 从 sources.jsonl 生成人看的 sources.md
    import_industry_map.py     # 把 dsh-industry-research 的 chain.json 转成 ramp 种子
    import_industry_track.py   # 把 timeline.jsonl 转成政策/动态草稿
    import_company_card.py     # 把 company_scan 的 card.json 转成公司卡草稿
    import_scout_case.py       # 把 dsh-scout 的 case.json 转成 ramp 草稿
    m15_compose.py             # 一键导入三个插件的导出，生成组合报告
    merge_imports.py           # 把 ramp-m15 草稿合并进已有 ramp（含来源重编号）
    validate_artifacts.py      # 检查来源引用、空模板、数量
    readiness.py               # 五个维度 + 证据够不够
    calc_process.py            # 算某环节的人力/风险成本与改进上限
    render_dashboard.py        # 生成 dashboard.html（四数字表 + 机会象限）
    selftest.py                # 23 项自测，CI 入口
  industries/
    coalbed-methane/           # 煤层气：AI 填好的公开源示例（不是模板）
    web-novel/                 # 网络文学：第二个行业包（验证通用性）
  examples/                    # 示例索引 + 两个完整跑通的运行（coalbed-methane-run/、web-novel-run/）
  docs/
    m15-live-test.md           # M1.5 真实导出实测步骤（装插件 → 导出 → compose）
    m15-live-test-result.md    # 2026-10-19 实测结果、路径与踩坑
    m15-scout-export-issue.md  # scout_export workspace-write 问题复核
    m15-plugin-live-test.md    # 插件本地 headless 实测（ramp_status/metrics/opportunities）+ M3 面板
  plugin/
    package.json               # dsh-fde-ramp npm 包骨架
    cordis.patch.yml
    lib/index.js               # 当前只注册 ramp_status（只读）
    README.md
    roadmap.md                 # 工具/界面/发布计划
  REVIEW.md / REVIEW2.md / REVIEW3.md  # 三轮独立验收报告
  CHANGELOG.md
```

## 五个自检维度

| 维度 | 一句话 |
|---|---|
| 结构 | 能不能讲清行业怎么赚钱、链条怎么分、什么会改变结构 |
| 语言 | 50 个行话用不用得准，能不能分辨近邻词 |
| 玩家 | 链上玩家、关系、规划说不说得清 |
| 决策 | 客户分几块业务、谁拍板、活动表能不能被一线逐行纠正 |
| 对话 | 能不能问出好问题、接住反对、不知道时承认并追问 |

目标：五项都到 3 分；最低不低于 2 分；还要有证据（来源、术语、待验证、玩家关系、业务域、活动行、访谈修正）。自检脚本会查这些，光自报分数不算。

## 煤层气示例

`industries/coalbed-methane/` 是一份**用公开资料填好的示例**，用来让你看到「填完大概是什么样」：

- `value-chain.md`：钱怎么流
- `chain.md`：15 家/类玩家 + 20 条关系 + 规划来源标签
- `domains.md`：8 个业务域
- `activities.md`：36 行活动表
- `glossary.md`：78 个候选词（0 个已客户校准）
- `verification-list.md`：15 条待验证
- `example-run/`：每一步的抽样子集

它没有客户文档、没有券商研报全文，**所有术语最高只到「公开说法」**；所有规划都标了「公司自述/媒体转述/推断」。不要把它当权威报告或照抄。

## 第二个行业：网络文学（网文写作）

[`industries/web-novel/`](industries/web-novel/README.md) 是第二个行业包，用来验证 skill 不是只对煤层气有效。假设客户是「某中型网络文学平台（付费 + 免费混合）」；同样没有客户文档，**0 个已校准术语**，所有规划标了 自述/转述/推断。

包含：34 条来源、77 个候选术语（39 public / 36 needs-customer / 2 unsure）、14 家玩家（含赛道/收入结构/用户画像总览）、10 条关系、8 个业务域、25 行活动表（16 列）+ 10 个关键环节展开（带真实例子）、15 条待验证、12 张 mermaid 图。

## 完整跑通的运行（两个行业）

- [`examples/coalbed-methane-run/`](examples/coalbed-methane-run/README.md)：煤层气，31 条来源、78 个术语、36 行活动表；
- [`examples/web-novel-run/`](examples/web-novel-run/README.md)：网络文学，34 条来源、77 个术语、25 行活动表。

两个都是从 `init_ramp.py` 生成、走完四步、通过 `validate_artifacts.py --strict` 和 `readiness.py --check` 的完整 `ramp/` 示例。都含 5 处**模拟访谈**修正（已标注是虚构示例，只演示记录格式）。

## FDE Skill 系列

各 Skill 独立运行，通过手动读取的产物衔接，不互相依赖安装。典型顺序：ramp → problem-framing → route-selection → knowledge-base（场景含文档检索时）→ demo → pilot，comms 贯穿各阶段。

| Skill | 管什么 | 结论词 |
|---|---|---|
| [fde-ramp](https://github.com/meiluosi/fde-ramp) | 见客户前搭起行业基本盘，拿图去被一线改 | 自检分数 |
| [fde-problem-framing](https://github.com/meiluosi/fde-problem-framing) | 把需求变成有证据的业务问题，比较 AI 与非 AI | Proceed / Investigate / Non-AI / Stop-Defer |
| [fde-route-selection](https://github.com/meiluosi/fde-route-selection) | 业务问题定义之后，先过滤合规与部署等硬约束，再选适配路线，最后用客户样本比选模型 | 见该仓库 |
| [fde-knowledge-base](https://github.com/meiluosi/fde-knowledge-base) | 路线含文档检索（RAG）时，判断知识够不够、怎么治、怎么评、质量卡在哪 | Proceed / Investigate / Pivot / Stop-Defer |
| [fde-comms](https://github.com/meiluosi/fde-comms) | 与人的关键沟通：访谈、向上汇报、坏消息 | 无（产出文稿） |
| [fde-demo](https://github.com/meiluosi/fde-demo) | 设计并复盘一次客户 Demo，换验证与信任 | Proceed / Iterate / Pivot / Stop-Defer |
| [fde-pilot](https://github.com/meiluosi/fde-pilot) | 把 Demo 通过的方案做成可检验的试点并判定成效 | Proceed / Iterate / Pivot / Stop-Defer |

跨 Skill 引用时加前缀保留原编号（`ramp:S01`、`framing:V2`、`kb:Q01`、`demo:L3`、`pilot:M2`）；同名结论词含义随阶段不同，引用时写 `framing:Proceed`、`demo:Proceed`。编号、结论词、边界与回写规则的完整约定见 [fde-demo 的 references/series.md](https://github.com/meiluosi/fde-demo/blob/main/references/series.md)。

## 当前状态

- ✅ **v0.9.5（当前）**：M3 侧栏面板（客户端 bundle + Host snapshot API）已接入 desktop profile；13 项单测；写工具批量/备份/diff 可用。
- ⏭ **下一步**：在真实环境安装三个插件，用 `m15_compose.py` 跑一次真实导出；然后把方案模式补进示例；最后插件化（M2/M3），见 `plugin/roadmap.md`。

## 已知限制

- 行业报告多数要付费/登录，skill 只负责「怎么读、读什么」，不提供全文。
- 中国源的可达性不稳定，打不开就标「未找到公开源」，不编。
- 第 4 步必须由人完成；skill 只能准备图、问题、记录模板。
- 自检分数用于找缺口，不是标准化考试，也不适合对外承诺。
- 案例包没有客户文档，所以没有「已校准」的术语——这是刻意设计。

## License

MIT
