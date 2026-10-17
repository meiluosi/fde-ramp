# fde-ramp · v0.2.0 独立复核报告

- **复核人**：fde-verifier（独立于实现者）
- **复核时间**：2026-10-18 02:19 CST
- **对象**：v0.2.0（用户新增三条方法 A 全链路关系 / B 从业者内容源 / C 业务域→流程→活动）
- **方式**：逐项实跑（init / validator / readiness / selftest / 计数反例 / 案例包抽检 / 来源 curl），不接受「文档说实现了」
- **快照**：仓库仍无 `.git`。关键文件 sha256 前 12 位：`SKILL.md 982f6a670832`、`README.md de5edb7eadd0`、`scripts/validate_artifacts.py 2b688c71c0d8`、`scripts/readiness.py 49db753bcbeb`、`scripts/selftest.py 588cf56471da`、`industries/coalbed-methane/chain.md b47969b7ba94`、`activities.md 365b9263b7ee`、`domains.md 6a4cce706d1e`、`sources.jsonl d902c9342e28`
- **说明**：已按 Lead 02:15 的更新（chain 玩家总表补「山西焦煤」）复核，案例玩家数为 **15**；临时文件在 `/tmp`，只写本文件。真实 `~/.dsh/skills` 安装需写工作区外文件，用 `/tmp/fake-skills3/fde-ramp -> 仓库` 符号链接等价验证。

---

## 一、结论：**PASS WITH FIXES**（可以交付）

| 项目 | 结果 |
|---|---|
| 7 项重点复核 | **7/7 PASS**（逐项实测，见 §二） |
| BLOCKER / MAJOR | **0 / 0** |
| MINOR / NIT | **7 / 4**（均不阻塞交付，见 §四） |
| `scripts/selftest.py` | **15/15 PASS**，exit 0 |
| 关键预期值 | init **19** 文件；空壳 `players/relations/domains/activities = 0`；案例包 **15 / 20 / 8 / 36 / terms 78**；空壳+五维全 4 → **exit 1**；全部命中 |

**判断**：三条新方法不是文档口号，模板、init、validator、readiness 证据闸门、selftest、CI 与主文档都已接通，且计数与预期完全一致。剩余问题集中在**案例包 README 的旧口径、两篇 reference 未同步、flow 计数精度、来源元数据**，均属 v0.2.1 小修。

---

## 二、逐项实测（7 项）

### 1) 模板 / init —— **PASS**

```text
$ python3 scripts/init_ramp.py --industry 复核v0.2 --customer 某客户 --persona 技术负责人 --deadline 2026-10-25 --out /tmp/r3-ramp
exit 0；生成 19 个文件：
activities.md brief.md calibration-log.md chain.md chain.mmd corrections.md domains.md drill-scorecard.md
flow.md flow.mmd glossary.md open-questions.md plan.md readiness.md sources.jsonl state.json
value-chain.md value-chain.mmd verification-list.md
$ grep -rn '{{' /tmp/r3-ramp → 无结果
```

- 19 个文件含 `chain.md/.mmd`、`domains.md`、`activities.md` ✓，无未替换占位符 ✓。
- 产物集合四方一致：init = `SKILL.md` 输出目录 = validator `REQUIRED` = **19**；`state.artifacts` = 18（仅不含 `state.json` 本身，合理）。

### 2) validator 计数 —— **PASS**

```text
空壳：
sources: 0  terms: 0  verification: 0  corrections: 0  guessed nodes: 0
chain players: 0  relations: 0  domains: 0  activities: 0          # 与任务预期逐字一致

案例包（sources + chain + domains + activities + glossary + flow + verification-list）：
sources: 29  terms: 78  verification: 15  corrections: 0  guessed nodes: 19
chain players: 15  relations: 20  domains: 8  activities: 36       # 任务预期（含 Lead 更新）全部命中
glossary statuses: ✅ public 38 / needs-customer 34 / unsure 6 / verified 0
```

**「汇总表干扰」专项测试（全部通过）**

| 测试 | 结果 |
|---|---|
| 删掉 activities.md 的 4 张活动表（只留活动画像/KPI/覆盖表等） | `activities = 0` ✓ |
| 删掉 domains.md 的域总表（只留接口矩阵/待校准表） | `domains = 0` ✓ |
| 删掉 chain.md 玩家表（只留 relations） | `players=0, relations=20` ✓ |
| 删掉 chain.md relations 表（只留玩家表） | `players=15, relations=0` ✓ |
| 在活动表后再追加「域/活动画像」「环节/KPI」「覆盖环节」三张对照表 | `activities` 仍为 **36** ✓ |

> 计数实现为 `_iter_tables` + 表头关键词匹配（`validate_artifacts.py:185-234`），确实不是按正文/汇总段计数；但随之带来「表头一旦改名计数归零」的脆弱性，见 NIT-1。

### 3) readiness 证据闸门 —— **PASS**

```text
空壳 + 五维全 4 + --check：
  Block 4 修正 0 / 来源 0 / 术语 0 / 待验证 0 / 链路玩家 0 / 链路关系 0 / 业务域 0 / 活动行 0
  gate: FAIL                                             # exit 1

完整 fixture（10 玩家/5 关系/3 域/15 活动/5 修正/8 来源/20 术语/5 待验证/negate=done）：
  --set 3,4,3,3,2 --check → gate: PASS                   # exit 0
  validate --strict → OK（counts 已由 readiness 回写）    # exit 0

缺 domains.md（清空） → gate: FAIL（业务域 ≥3: 0）           # exit 1
缺 activities.md（清空）→ gate: FAIL（活动行 ≥10: 0）        # exit 1
```

- 门槛扩展为 8 项证据（`readiness.py:108-117`），与 README:108 / QUICKSTART:57 / rubric:76-82 基本一致。
- `scripts/selftest.py` 覆盖 fresh 证据闸门失败 + complete PASS + 新计数函数，**15/15** ✓。

### 4) 案例包 v0.2 —— **PASS**（有 3 处文档旧口径，见 MINOR）

**统计一致性：36 行 ✅13/⚠️13/❓10 与表完全一致**（脚本按「信心」列重数）：

```text
activity rows= 36 confidence= {'❓': 10, '✅': 13, '⚠️': 13}
```

- `chain.md`：15 家/类玩家、20 条 relations；关系信心分布 **✅10 / ⚠️7 / ❓3**，与案例 README 声明一致；20 条关系每行 6 列（from/类型/to/证据/信心/来源）**无空单元格**。
- **规划标签**：`【公司自述】`12 处、`【媒体转述】`3 处、`【推断】`1 处；表内「未来规划」列与 §3 逐段「规划」条目均带标签，无标签的均为「❓ 未找到/待验证」的空白声明，符合「规划不是已发生」。
- **股权关系**：中海油→中联 100%（2019，标 ⚠️ 时点）、山西燃气/晋能→蓝焰（S15）、新天然气→亚美（S25）均有证据；中国石油→中石油煤层气明确标「❓ 名称推断」。未发现把推断股权写成事实。
- `domains.md`：8 域（3–8 上界）；7✅ + D8 ❓，与 README「7✅/1❓」一致。
- `activities.md`：11 列（业务域/流程/环节/做什么/谁做/影响谁/工具/业务背景/输入输出/信心/来源）齐全；工具列**只写类别、无厂商名**（规则见 `activities.md:5`）；只有「谁做」列出现一处厂商示例（NIT-2）。
- `example-run/day3-domains-activities.md`：域图 + 8 行活动样例 + 现场话术，体例与主包一致。

### 5) 文档一致性 —— **PASS（主文档）/ 有 3 处 reference 与案例 README 未同步（MINOR）**

- 已同步：`SKILL.md`（Block 1/2/3/4 均含新方法）、`README.md`（方法表、原则 5/6、五维、证据门槛、19 文件）、`QUICKSTART.md`（A4 速查含三方法）、`references/method.md`（§1.1 全链路 / §2.1 从业者 / §3 域→流程→活动 + 子代理分工）、`source-hunting.md` §3.1、`glossary-protocol.md` Miner D、`evidence.md` §7.1 + sourceKind、`readiness-rubric.md` 门槛/证据索引、`plugin/roadmap.md`（`ramp_chain`/`ramp_domains`/`ramp_activities`）、`CHANGELOG.md`。
- 未同步（详见 Findings）：`industries/coalbed-methane/README.md` 仍写 `S01…S24`、四步法映射未含新文件；`references/evidence.md:81` 的证据闸门描述缺 v0.2 四项；`references/map-and-negate.md` 无 chain/domains 的现场协议。

### 6) selftest / CI —— **PASS**

```text
$ python3 scripts/selftest.py
PASS init fresh
PASS init generates required files
PASS fresh validate exit 0 (warnings ok)
PASS fresh readiness fails evidence gate
PASS complete fixture readiness PASS
PASS complete fixture strict validate PASS
PASS merged source refs [S01/S02] parse
PASS unknown source ref fails
PASS invalid state.json handled cleanly
PASS refuse non-empty dir
PASS correction value on next line
PASS prose ❓ not counted as guessed node
PASS chain counts 10 players / 5 relations
PASS domains count
PASS activities count
all self-tests passed                                    # exit 0（15/15）
```

- CI YAML 合法：`jobs: ['test']`，3 步（checkout / setup-python 3.12 / `python3 scripts/selftest.py`），对 MVP 合理。注意仓库仍未 `git init`，CI 要等建仓推送后才实际运行。

### 7) DSH 适配 —— **PASS**

- `SKILL.md` frontmatter 仍只有 `name` + `description`，与 `~/.dsh/skills/{material-audit,chain-authoring,gap-rehearsal}` 约定一致；name 与安装目录名匹配。
- 符号链接安装 + 任意 cwd：`ln -s <repo> /tmp/fake-skills3/fde-ramp`，从 `/tmp` 执行 `init_ramp.py` / `validate_artifacts.py` / `selftest.py` 全部正常（`readiness.py` 对 validator 的 import 通过 `Path(__file__).resolve().parent` 解析，symlink 下可用）。

---

## 三、Findings

### MINOR（7，不阻塞交付）

| # | 文件:行 | 问题 | 建议修法 |
|---|---|---|---|
| m1 | `industries/coalbed-methane/README.md:147` | 来源编号仍写「`S01`…`S24`（与 sources.jsonl 一一对应）」，实际已是 **29 条 S01–S29**（A16/B2/C9/D2），会误导复制。 | 改为 `S01`…`S29`；补一句「S25–S29 为 v0.2 新增（年报 PDF/论文/从业者科普/增值税/互动易）」。 |
| m2 | `industries/coalbed-methane/README.md:84-90` | 「用户四步法 → 文件映射」仍是 v0.1 版：① 映射里没有 `chain.md`，③ 没有 `domains.md`/`activities.md`，与 v0.2 方法表不一致。 | 在 ① 加 `chain.md`、③ 改为「`domains.md` → `flow.md` → `activities.md`」并补产出说明。 |
| m3 | `references/evidence.md:81` | readiness 证据闸门只写「≥5 修正 / ≥8 来源 / ≥20 术语 / ≥5 待验证」，缺 v0.2 的「≥10 玩家 / ≥5 关系 / ≥3 域 / ≥10 活动行」（实际检查见 `readiness.py:108-117`）。 | 补齐四项，与 README:108 / QUICKSTART:57 / rubric:76-82 对齐。 |
| m4 | `references/map-and-negate.md`（v0.2 仅新增 §8.5，第 100 行起） | 现场协议只讲「活动表访谈」，没有把 `chain.md`（玩家/关系/规划）与 `domains.md`（域划分）纳入「带去被否定」的对象；`grep chain/domains` 无命中，与 `SKILL.md:174,182` 不一致。 | 补 §8.6/§8.7：带链路图去问「谁和谁是什么关系、规划真假」，带域图去问「这几块是不是一个部门」；或至少注明「另见 SKILL Block 4」。 |
| m5 | `scripts/validate_artifacts.py:147-162` | `flow_guess_count` 已改为只数「纯 ❓ 单元格」，但仍会数**非节点表**：案例 `flow.md` 报 `guessed nodes: 19`，而节点信心表实际只有 **3** 个 ❓（其余来自待验证候选、审批链、数据视角表）。「图上 ≥5 个 ❓」的自动验收仍可能假通过。 | 只统计表头含「信心」且首列为节点的表（或要求 `flow.md` 的节点信心表放在固定标题下）；在 selftest 加「3 个节点 ❓ + 其他表 6 个 ❓ → 应 WARN」。 |
| m6 | `industries/coalbed-methane/sources.jsonl`（29 条全部） | 29 条来源 **0 条**带 `sourceKind`；`S27`（B站科普）是案例包唯一的从业者内容样例，但未标 `sourceKind: practitioner`，方法 B 的「区分官方/研报/从业者/媒体」在案例里没有落地样例（`glossary-protocol.md:17`、`evidence.md:32` 只是「建议填」）。 | 给 S25–S29 至少 S27 加 `sourceKind`；或把 `sourceKind` 从「建议」升为「案例包必填」，validator 加软警告。 |
| m7 | `SKILL.md:162` vs `scripts/readiness.py:116` | SKILL Block 3 验收写「活动表 ≥15 行」，readiness 门槛是「活动行 ≥10」；12 行即可 gate PASS，低于 SKILL 验收（rubric:80 已写「≥10（目标 15）」）。 | SKILL 验收句补「（门槛 ≥10，目标 ≥15）」或把 gate 提到 15；二选一并保持 rubric/README/QUICKSTART 一致。 |

### NIT（4）

| # | 文件:行 | 问题 | 建议修法 |
|---|---|---|---|
| n1 | `scripts/validate_artifacts.py:185-234` | 计数**依赖表头关键词**：实测把 activities 的「业务域」列改名「域」→ `activities_count = 0`（readiness 随即 FAIL）；`chain_counts` 关系表要求英文 `from`，若用户写「从/关系类型/到」则 `relations = 0`。模板固定了表头，但用户自建表容易踩。 | 在 SKILL/模板里写明「不要改这几列表头」；或计数兼容同义词（业务域/域、from/从、环节/活动环节）。 |
| n2 | `industries/coalbed-methane/activities.md:41` | 「谁做」列写「测录井队（如石化油服类）」——工具列已严格只写类别（:5），但「谁做」出现具体厂商示例，与任务「不写具体厂商名」的意图不一致。 | 改为「测录井队（专业服务商）」，把石化油服留在 `players.md`/`chain.md`。 |
| n3 | `industries/coalbed-methane/README.md:146`；根 `README.md:5,93,132` | 案例 README 仍写「任务书里的 10 个文件」（现 13 个数据文件 + 6 个 example-run）；根 README 首屏产出清单未含 chain/domains/activities、目录结构只列 `REVIEW.md`（缺 REVIEW2/REVIEW3）、v0.2.1 待办仍写「Day1–Day4」。 | 统一文件数口径；首屏产出补三件新产物；目录补 REVIEW2/REVIEW3；Day 改为 Block。 |
| n4 | `SKILL.md:41`、`templates/value-chain.md:68`、`references/evidence.md:27` vs 案例包 | 文档示例引用 `[S1]`/id `S1`，案例包统一用零填充 `S01…S29`；validator 是字面匹配（`[S1]` 与 `S01` 不等价），混用会报 unknown。 | 统一为零填充 `S01`（文档示例同步），或 validator 对编号做去零归一（`S1`→`S01`）。 |

---

## 四、来源抽检（v0.2 新增 S25–S29，2026-10-18）

`curl -sSL -m 20` 默认 UA；S29 默认 403，换浏览器 UA 后 200。PDF 未做正文解析（环境无 pdftotext/pypdf），只核对 HTTP/文件类型/元数据标题。

| id | tier | HTTP | 标题/内容匹配 | 备注 |
|---|---|---|---|---|
| S25 | A | **200** | ✅ PDF 1.44 MB，PDF 元数据标题含「新疆鑫泰…」（新天然气 2025 年报） | 标题为 UTF-16 多段，部分乱码；建议人工打开确认正文 |
| S26 | B | **200** | ⚠️ PDF 1.90 MB，2 页预览；标题元数据乱码，未能核对完整标题 | 《中国矿业》2025 年第 34 卷第 1 期；「排采制度」唯一公开技术源，建议保留但标注「预览版」 |
| S27 | D | **200** | ✅ `【智造未来】煤层气提取氦气，这项技术啃下氦气制备硬骨头_哔哩哔哩_bilibili` | 从业者/科普样例；`sources.jsonl` 备注已诚实标「非从业者实录、只作语境」 |
| S28 | C | **200** | ✅ `财政部官宣 多个行业增值税优惠政策即将取消_央广网`；正文命中「煤层气抽采」「废止目录」「2025-11-01」 | 未取财政部原文，备注已声明 |
| S29 | C | **403 → 200** | ✅ 浏览器 UA 下标题 `新天然气：煤层气增值税取消对2026年盈利有一定影响`；正文命中「即征即退取消…影响金额与年度产量、收入密切相关」 | 10jqka 反爬：直接 curl 403，带浏览器 UA 200；建议 note 注明或改用互动易原链 |

**结论**：5 条新来源均可打开（S29 需浏览器 UA），未见编造标题/URL；S26 的「2 页预览 + 标题乱码」与 S29 的反爬是使用注意项，不是内容错误。

---

## 五、v0.2.1 待办（≤8）

1. 修案例 README 旧口径：`S01…S24` → `S01…S29`；四步法映射补 `chain.md` / `domains.md` / `activities.md`；文件数 10 → 13（m1、m2、n3）。
2. 同步 `references/evidence.md:81` 与 `readiness-rubric.md:3` 的证据门槛描述（补玩家/关系/域/活动）（m3）。
3. `references/map-and-negate.md` 补 chain / domains 的现场被否定协议（m4）。
4. `flow_guess_count` 限定「节点信心表」并加 selftest 回归；同时给合并引用/正文 ❓ 各留一条反例（m5）。
5. 案例 `sources.jsonl` 补 `sourceKind`（至少 S27 practitioner），或在文档里把 sourceKind 升为案例包必填（m6）。
6. 统一「活动表 ≥15 验收 / ≥10 门槛」口径（SKILL:162、README、QUICKSTART、rubric、readiness.py:116）（m7）。
7. 计数表头兼容或文档固定表头（业务域/域、from/从、环节/活动）（n1）；案例 activities 去厂商示例（n2）。
8. README 首屏产出/目录/路线更新；引用编号统一零填充 `S01`（n3、n4）。
