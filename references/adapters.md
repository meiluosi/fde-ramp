# 和现有插件组合（M1.5 适配层）

> 真实环境的安装 + 导出实测步骤见 [`docs/m15-live-test.md`](../docs/m15-live-test.md)。

> 目标：不重造研究能力，把已有插件的「产业链图、公司卡、证据分级、知识库」接进 `fde-ramp` 的产物里。
> 原则：**插件是可选加速器，不是依赖**；没装就用手上的资料和模板，照常跑。

## 0. 先确认装没装

在会话里让 Agent 看工具列表，或看设置 → 插件：

| 插件 | 关键工具/入口 | 测试过的版本 |
|---|---|---|
| `dsh-industry-research` | `industry_map` / `industry_track` / `company_scan` / `industry_report` | 0.3.19 |
| `dsh-scout` | `scout_start` / `scout_export` / `scout_questions` 等 12 个 | 0.9.3 |
| `@weibaohui/dsh-kb` | 侧栏「知识库」/ 搜索 / raw 上传 / `@` 引用 | 0.7.15 |

安装示例（CLI profile；桌面 App 的 `desktop` profile 需在 App 内装）：

```bash
dsh plugin --profile web add dsh-industry-research
dsh plugin --profile web add dsh-scout
dsh plugin --profile web add @weibaohui/dsh-kb
```

> 社区插件，装之前在一次性 profile 里试；不要直接进主力 profile。

## 1. `dsh-industry-research`：产业链图 + 公司卡 + 政策跟踪

### 工具

| 工具 | 关键参数 | 产物 |
|---|---|---|
| `industry_map` | `industry`, `seed`, `seedFiles`, `web`, `chain`, `renderSvg`, `depth` | `<workspace>/industry-research/<行业>/chain.json`、`chain.svg`、`sources.json` |
| `industry_track` | `industry`, `topics`, `since`, `depth`, `evidenceCategory` | `timeline.jsonl`（政策/新闻，带快照哈希） |
| `company_scan` | `name`/`companies`, `dataFiles`, `web`, `status`, `statusAsOf`, `ticker`, `metrics` | `companies/<name>/card.json` + `card.md` |
| `industry_report` | `industry`, `sections`, `companies`, `draft` | `reports/<ts>/report.md` + `manifest.json` |

`chain.json` 的结构（关键）：

```json
{"industry":"...", "nodes":[{"id":"n1","name":"...","tier":"upstream","metrics":[{"key":"规模","value":12,"unit":"亿元","asOf":"2026-01-01","sourceRef":"S1"}]}], "edges":[{"from":"n1","to":"n2","note":"原料供应"}]}
```

### 怎么接进 `fde-ramp`

1. 让 Agent 先跑 `industry_map`（建议 `renderSvg: true`），再跑 `industry_track`/`company_scan`；
2. 用导入器把 `chain.json` 和 `sources.json` 转成 ramp 种子：

```bash
python3 scripts/import_industry_map.py \
  --chain  <workspace>/industry-research/<行业>/chain.json \
  --sources <workspace>/industry-research/<行业>/sources.json \
  --out-dir ramp
```

会生成：

- `ramp/chain-seed.md`：分段/节点/指标/边 + 合并建议；
- `ramp/chain-seed.mmd`：mermaid 图；
- `ramp/sources-imported.jsonl`：来源台账（ref 统一成 `S01` 格式）。

3. 手动合并进 `chain.md` / `sources.jsonl`（导入器不覆盖你的正文）；`chain.svg` 复制成 `ramp/chain.svg`；
4. `company_scan` 的 `card.md` 用来看客户/玩家的现状与财务口径，引用时保留 `source` 与 `asOf`。

**注意**：`industry-research` 的 `sourceRef` 是它自己的 `S1/S2`；导入器会做 `S1 → S01` 映射；如果合并到已有 `sources.jsonl`，先检查 id 冲突。

## 2. `dsh-scout`：公司主体核验 + 证据分级 + 访谈问题

### 用法

1. `scout_start(caseId, companyName, roleTitle, location)` 建案例；
2. `scout_add_source` / `scout_search` / `scout_ingest` 登记来源；
3. `scout_add_claim` / `scout_verify_claim` / `scout_verify_identity` 管结论；
4. `scout_export` 导出五文件：`case.json`、`sources.json`、`claims.json`、`events.jsonl`、`report.md`；
5. 用导入器转成 ramp 草稿：

```bash
python3 scripts/import_scout_case.py \
  --case <scoutDir>/<caseId>/case.json \
  --out-dir ramp
```

生成 `ramp/scout-import.md`：公司/岗位/决策、来源表（E0–E3）、主张表、访谈问题、合并建议。

### 证据等级怎么映射

| scout | 我们 |
|---|---|
| E3 官方一手 / E2 权威第三方 | ✅ 候选（仍要标来源） |
| E1 用户提供 | ⚠️ |
| E0 / `unknown` / `needs_verification` | ❓，进 `verification-list.md` |

**不要**把 scout 的 `verified` 直接当本 skill 的 `verified`：本 skill 的 `verified` 只认**客户文档/一线确认**。

## 3. `@weibaohui/dsh-kb`：客户材料沉淀

- 把客户给的 PDF/制度/招标文件/访谈记录放进 kb 的 `raw/`；
- 让 Agent 用 `@raw/...` 或 kb 搜索找原句，用于术语校准与活动表回填；
- 在 `sources.jsonl` 里登记为来源（`url` 可写工作区路径，`sourceKind: other`）；
- 没有脚本导入（kb 是固定知识库，不是文件格式）；这一步靠 Agent 检索 + 人工贴原句。

## 3.5 一键导入：m15_compose.py

如果三个插件都跑完、把导出文件收在一个目录里：

```text
imports/
  industry-research/<行业>/
    chain.json
    sources.json
    timeline.jsonl
  industry-research/companies/<公司>/card.json
  scout/<case>/case.json
```

一条命令生成所有导入草稿：

```bash
python3 scripts/m15_compose.py --imports imports --out-dir ramp
```

会生成：

- `chain-seed.md` / `chain-seed.mmd`
- `sources-imported.jsonl`
- `timeline-import.md`
- `company-card-<slug>.md`
- `scout-import.md`
- `m15-composition-report.md`（执行记录 + 下一步清单）

它**只生成草稿，不覆盖** `chain.md` / `sources.jsonl` / `players.md`。合并步骤见报告第 3 节。

## 4. 推荐的组合顺序

```text
第 1 步：industry_map（产业链种子）+ industry_track（政策）
        → import_industry_map.py → chain-seed.md / sources-imported.jsonl
        → 合并进 chain.md / sources.jsonl
第 1 步：company_scan（客户/玩家公司卡）→ 玩家表
第 2 步：dsh-kb（客户材料）→ 术语校准原句
第 3–4 步：scout（公司主体/证据）+ import_scout_case.py → 访谈问题/待验证
第 5 步（方案模式）：用活动表 + 客户数字算账，不依赖插件
```

## 5. 怎么判断组合有没有用

同一行业跑两遍，记录：

| 指标 | 不接插件 | 接插件 |
|---|---|---|
| 第 1 步用时（人工估） |  |  |
| 有来源节点/总节点 |  |  |
| 来源条数（A/B 级占比） |  |  |
| 玩家表覆盖 |  |  |
| 返工次数（补来源/改口径） |  |  |

如果接插件后来源覆盖率没提升、反而多花时间，就退回纯模板流程。

## 6. 兼容与风险

- 三个插件都是社区包，DSH 还在 0.2.x；升级后先看工具是否还在；
- 桌面 App 的 `desktop` profile 不能从 CLI 装，必须在 App 内装；
- `industry-research` 的 `chain.json` 有严格校验：有数值必须带 `sourceRef`，缺口要显式留空；
- 导入器只读导出文件，不调用插件运行时；所以**先让插件跑完、导出**，再导入；
- 不要为了「接插件」而把客户机密数据传到外部服务。
