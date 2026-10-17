# fde-ramp · v0.1.1 复核报告

- **复核人**：fde-verifier（独立于修复者）
- **复核时间**：2026-10-18 01:59 CST
- **对象**：v0.1.1（上一轮 `REVIEW.md` 的 6 个 MAJOR + 4 个指定 MINOR + 4 个 NIT 修复）
- **方式**：逐项实跑，不接受「文档说修了」；临时工作区在 `/tmp`，只写本文件
- **快照**：仓库仍无 `.git`。关键文件 sha256 前 12 位：`SKILL.md 2b32463ad780`、`README.md 3a73094d7444`、`scripts/validate_artifacts.py 990a5d8e8959`、`scripts/readiness.py a0faaa14cb8f`、`scripts/selftest.py 570e3a317f9e`、`.github/workflows/ci.yml 90ff057872b5`、`templates/state.json 565c72309c58`
- **限制**：真实 `~/.dsh/skills/fde-ramp` 安装需要写工作区外文件（本会话权限不允许），用 `/tmp/fake-skills2/fde-ramp -> 仓库` 符号链接等价验证；案例包按设计不是 `ramp/` 工作区，只验证其数据/引用可被 validator 消费。

---

## 一、结论：**可以交付**（PASS WITH MINOR）

| 项目 | 结果 |
|---|---|
| 上轮 6 个 MAJOR | **6/6 修复**（逐项实测，见 §二） |
| 指定 MINOR（m2/m4/m6/m9） | **4/4 修复** |
| 指定 NIT（n1–n4） | **4/4 修复** |
| `scripts/selftest.py` | **9/9 全过**，exit 0 |
| 新发现 | **0 BLOCKER / 0 MAJOR / 5 MINOR / 3 NIT**（均不阻塞交付，见 §四） |
| 核心闸门 | 空壳 + 五维全 4 → `--check` exit 1；完整 fixture（3,4,3,3,2 + 证据）→ PASS。**自报满分已不能 PASS。** |

**判断**：v0.1.1 可以交付。上一轮最要命的三件事——门槛两套说法、就绪度可刷分、validator 空壳假通过——都已真正修好，且有 `selftest.py` 与 CI 兜底。剩余问题是度量精度与文档边角（flow 计数、多来源引用、证据门槛文案、修正记录换行格式），建议 v0.1.2 顺手收掉。

---

## 二、逐项复核（上轮 MAJOR / MINOR / NIT）

### M1 五维门槛统一 —— **PASS**

- 文档已统一为两条：**目标**五项≥3；**门槛** min≥2、avg≥3、结构/语言≥3 + Block 4 证据。
  - `SKILL.md:193-194`、`README.md:103`、`references/readiness-rubric.md:3`、`:76`、`templates/readiness.md:19` 一致；
  - `scripts/readiness.py:118-123` 判定与文案一致（`dims_ok` + `evidence_ok`）。
- 实测（完整 fixture：8 来源 / 20 术语 / 5 待验证 / 5 修正 / `negate=done`）：
  - `3,4,3,3,2` → `average 3.00`、`gate: PASS`、**exit 0**（任务要求「有证据的 3,4,3,3,2 应 PASS」✓）；
  - 空壳（`/tmp/r2-fresh`）+ 五维全 4 + `--check` → `gate: FAIL`、**exit 1**（任务要求 ✓）。

### M2 证据闸门 —— **PASS**

- `readiness.py:83-105,119,156` 新增 evidence gate：修正≥5、来源≥8、术语≥20、待验证≥5、`state.blocks.negate=="done"`。
- 实测 5 个场景：

| 场景 | 结果 |
|---|---|
| 空壳 + 五维全 4 + `--check` | FAIL / exit 1 ✓ |
| 完整 fixture + `3,4,3,3,2` + `--check` | PASS / exit 0 ✓ |
| 完整 fixture 但 `blocks.negate=pending` | FAIL / exit 1，输出 `missing: Block 4 not marked done` ✓ |
| 完整 fixture 但只留 7 条来源 | FAIL / exit 1，输出 `来源 ≥8: 7 (need >= 8)` ✓ |
| `selftest.py` 覆盖 | `PASS fresh readiness fails evidence gate`、`PASS complete fixture readiness PASS` ✓ |

### M3 validator 计数 —— **PASS（附 2 条残余，见 N1/N4）**

- 空壳计数（任务要求 0/0/0）：
  `sources: 0  terms: 0  verification: 0  corrections: 0  guessed nodes: 0` ✓（5 条 WARN 合理，exit 0）
- 案例 glossary 入 ramp：`terms: 78`、`glossary statuses: {'public': 38, 'needs-customer': 34, 'unsure': 6, 'verified': 0}` ✅ 完全符合任务要求。
- flow 阈值：源码 `validate_artifacts.py:235` 为 `q < 5`；实测 4 个节点 ❓ → `WARN: only 4 … (target >=5)`；5 个 → 无 WARN；0 个 → WARN ✓。
- 非法 `state.json`：validator 输出 `ERROR: state.json: invalid JSON (Expecting property name enclosed in double quotes)`、exit 1；readiness 输出同款 ERROR、exit 2，**无 traceback** ✓。
- 扫描范围改为 `rglob("*.md")`（`validate_artifacts.py:210`）✓。

### M4 `verified` 语义 —— **PASS**

- `SKILL.md:37`：「没有客户文档或一线确认，状态不许写 `verified`；官方文件/公开源最高只能到 `public`」；
- `templates/glossary.md:4`：「`verified`（**客户文档或一线员工**确认）／`public`（…官方文件最高也只到这一档）／没有客户文档时一个 `verified` 都不该有」；
- `references/glossary-protocol.md:4,10,15`：铁律与状态表一致，明确 verified 只认客户/一线。
- 三处语义一致，无残留 ✓。

### M5 来源 id 统一 —— **PASS（附 1 条多引用形式问题，见 N2）**

- 案例 `sources.jsonl`：24 行，id 为 `S01…S24` ✓（`usedFor` 仍为字符串，validator 现已接受 string/list）。
- 把案例 `sources.jsonl` + 全部 `example-run/*.md` 复制进 `ramp/` 后跑 validator：
  `sources: 24`、**0 条 `unknown source ref`**、`OK`、exit 0 ✓。
- example-run 单引用形式 `[S01]/[S03]/[S12]/[S14]/[S15]` 等全部能在 sources 找到 ✓。
- 残余：`[S03/S04]`、`[S03/S04/S05]`、`[S04/S05]`、`[S12/S11]`、`[S14/S24]` 5 种合并写法不被 `SOURCE_RE = \[S(\d+)\]` 解析（静默跳过；其内部 id 均存在，内容无误）——见 N2。

### M6 产物清单 —— **PASS**

- 脚本比对（init 实跑 / SKILL 输出目录块 / `templates/state.json` artifacts / validator `REQUIRED`）：

| 集合 | 数量 | 与 init 差异 |
|---|---|---|
| init 实际生成 | 15 | — |
| SKILL 输出目录块 | 15 | 无差异 |
| validator `REQUIRED` | 15 | 无差异 |
| `state.artifacts` | 14 | 仅不含 `state.json`（状态文件本身不是产物，合理） |

- `.mmd`（2 个）、`calibration-log.md`、`drill-scorecard.md` 均已进入三者 ✓。
- `drills/` 已从 skill 侧移除：`templates/readiness.md:28` 改为 `drill-scorecard.md`；`plugin/roadmap.md:32,57` 明确写「可选 / 插件版」✓。

### 指定 MINOR / NIT 抽查 —— **全部 PASS**

| 项 | 验证 | 结果 |
|---|---|---|
| m2 全国/山西 | `industries/coalbed-methane/README.md:40` 已改为「2015 年**全国**利用率基准」 | ✓ |
| m4 埋深单位 | `value-chain.md:173`、`verification-list.md:97` 已拆成「埋深 m」与「单井日产起算值 m³/d」 | ✓ |
| m6 glossary 统计 | 文件内统计 38/34/6/78；validator 实算 78/38/34/6 | ✓ |
| m9 state JSON 错误 | 见 M3，清 ERROR 非 traceback | ✓ |
| n1 候选池 | `SKILL.md:116-117`、`README.md:23` 统一「60–80（最多 120）→ 约 50」 | ✓（仅输出目录注释仍写「候选池可到 80」，NIT） |
| n2 Day3 命名 | example-run README 第 12 行改 Day3；`day3-flow-guesses.md` H1 改「Day3 产出」 | ✓ |
| n3 examples 文案 | `README.md:90`「说明页；示例见 industries/…/example-run/」 | ✓ |
| n4 roadmap M0 | `plugin/roadmap.md:101` 改为「用案例数据初始化出 ramp 并跑通；v0.2 补 strict 端到端 ramp」 | ✓ |

---

## 三、实测记录（命令 + 结果）

```text
$ python3 scripts/selftest.py
PASS init fresh
PASS init generates required files
PASS fresh validate exit 0 (warnings ok)
PASS fresh readiness fails evidence gate
PASS complete fixture readiness PASS
PASS complete fixture strict validate PASS
PASS unknown source ref fails
PASS invalid state.json handled cleanly
PASS refuse non-empty dir
all self-tests passed                                   # exit 0（9/9）
```

```text
$ init_ramp.py --industry 复核测试 … --out /tmp/r2-fresh          # exit 0，15 文件，无 {{ 残留
$ validate_artifacts.py --root /tmp/r2-fresh
sources: 0  terms: 0  verification: 0  corrections: 0  guessed nodes: 0
WARN ×5（glossary/verification/flow/corrections 未填）
OK                                                      # exit 0

$ readiness.py --root /tmp/r2-fresh --set 五维全 4 --check
evidence: Block4 修正 0 / 来源 0 / 术语 0 / 待验证 0；negate=False
gate: FAIL                                              # exit 1

$ readiness.py --root /tmp/r2-complete --set 3,4,3,3,2 --check   # 完整 fixture
evidence: 修正 5 / 来源 8 / 术语 20 / 待验证 5；negate=True
gate: PASS                                              # exit 0

$ validate_artifacts.py --root /tmp/r2-complete --strict
sources: 8  terms: 20  verification: 5  corrections: 5  guessed nodes: 5
OK                                                      # exit 0

$ validate_artifacts.py --root /tmp/r2-casegloss        # 案例 glossary
sources: 0  terms: 78  verification: 0  corrections: 0  guessed nodes: 0
glossary statuses: {'public': 38, 'needs-customer': 34, 'unsure': 6, 'verified': 0}

$ validate_artifacts.py --root /tmp/r2-caserefs         # 案例 sources + 全部 example-run
sources: 24 … OK，0 条 unknown source ref               # exit 0

$ validate_artifacts.py --root /tmp/r2-badstate         # 非法 state.json
ERROR: state.json: invalid JSON (Expecting property name ...)   # exit 1，无 traceback
$ readiness.py --root /tmp/r2-badstate
ERROR: state.json: invalid JSON (…)                     # exit 2

$ validate_artifacts.py --root /tmp/r2-flow4            # 4 个 ❓ 节点
WARN: flow: only 4 guessed node rows '❓' (target >=5)   # exit 0（WARN 正确）
```

- **符号链接 + 任意 cwd**：`ln -s <repo> /tmp/fake-skills2/fde-ramp`，`cd /tmp` 后执行 `/tmp/fake-skills2/fde-ramp/scripts/readiness.py` 正常运行（`readiness.py` 对 `validate_artifacts` 的 import 通过 `Path(__file__).resolve().parent` 解析，symlink 场景 OK）✓。
- **CI**：`.github/workflows/ci.yml` YAML 解析通过（`jobs: ['test']`），ubuntu-latest + Python 3.12 跑 `python3 scripts/selftest.py`，对 MVP 合理。注意：仓库尚未 `git init`（`git rev-parse` 报 not a git repository），CI 要等建仓推送后才生效——NIT。

---

## 四、新发现（均为非阻塞）

### MINOR（5）

| # | 文件:行 | 问题 | 建议修法 |
|---|---|---|---|
| N1 | `scripts/validate_artifacts.py:142-159` | `flow_guess_count` 的 docstring 写「node rows」，实现却是**任意表格行只要含 ❓ 就计数**。实测把案例 `flow.md` 放进 ramp：`guessed nodes: 19`，而节点信心表实际只有 **3** 个 ❓ 节点（其余来自「待验证候选」「数据视角」「审批链」等表）。这会让「≥5 个 ❓」验收假通过。 | 只统计「信心」列所在表（表头含 `信心`）且首列为节点名的行；或要求表头为 `节点/信心` 组合；并在 `selftest.py` 加一条「3 个节点 ❓ + 若干其他表 ❓ → 应 WARN」的回归。 |
| N2 | `scripts/validate_artifacts.py:35` | `SOURCE_RE = \[S(\d+)\]` 不解析合并引用。example-run 里有 5 处 `[S03/S04]` 式写法，全部静默跳过校验（当前 id 都存在，未造成错误；但 typo 会漏检）。 | 扩展为 `\[S\d+(?:\s*[/、,]\s*S?\d+)*\]` 并逐 id 校验；或在案例包统一改成 `[S03][S04]` 独立引用。 |
| N3 | `references/readiness-rubric.md:76`；`SKILL.md:194`；`README.md:103` | 文档把证据门槛描述为「≥5 处修正（+ state）」，实际脚本还有**来源≥8 / 术语≥20 / 待验证≥5** 三条（`readiness.py:99-105`）；rubric 还写成「从 `corrections.md` 与 `state.json` 检查」，与实现（还读 sources/glossary/verification）不符。evidence.md §7 与 CHANGELOG 已写全，但主文档没同步。 | rubric:76 与 SKILL/README 的门槛句补全四条证据阈值与「negate=done」；或让脚本只保留文档承诺的检查。 |
| N4 | `scripts/validate_artifacts.py:162-171` | `correction_count` 只认**冒号同一行**的值。实测 markdown 合法的「下一行缩进写值」格式 → `corrections: 0`，会让完成 5 处修正的用户 readiness 假 FAIL（模板 `- 我原以为：` 本身也容易被填到下一行）。 | 正则支持续行（冒号后到下一个 `- ` 列表项/空行之间的内容）；或在 `templates/corrections.md` 标明「值写在同一行」。 |
| N5 | `industries/coalbed-methane/README.md:53` | 声称「本包刻意让 ❓ 占比不低于 25%」，但 `flow.md` 主流程节点信心表是 **3/14 ≈ 21%**（另 5 个 ❓ 在非节点表）；若该指标指流程图节点，则不达标。 | 要么给 flow 主流程补 2 个 ❓ 节点（如 ④ 储量备案、⑬ 外输），要么把话改成「全包口径」。 |

### NIT（3）

| # | 文件:行 | 问题 | 建议修法 |
|---|---|---|---|
| N6 | `README.md:130` | v0.2 待办仍列「CI」，但 CI 已在 v0.1.1 交付（`.github/workflows/ci.yml`）；另 `SKILL.md:71` 输出目录注释仍写「候选池可到 80」，与 Block 2「最多 120」不一致。 | 删掉 v0.2 的 CI；注释改成「60–80（最多 120）」。 |
| N7 | 仓库根 | 尚未 `git init`/提交，CI 文件处于「写了但不会跑」状态；`scripts/__pycache__/*.pyc` 留在工作树（已被 `.gitignore` 忽略，但会混进目录）。 | 建仓 + 首次提交，确认 CI 真正跑通；清理 pycache（或加 `make clean`）。 |
| N8 | `industries/coalbed-methane/sources.jsonl` | 5 条 `published` 为自由文本（S01/S06/S09/S10/S12，如「2013-09-14（网站发布2013-09-22）」），validator 只要求非空；`evidence.md:30` 说「不确定写 unknown」。 | 可保留人类可读说明，但建议拆成 `published`（ISO 或 unknown）+ `note`；或在 evidence.md 明确允许该写法。 |

---

## 五、交付判断

**可以交付。** 上轮指出的质量闸门问题（门槛口径、自报刷分、空壳假通过、来源 id、verified 语义、产物清单）全部修复且实测通过；`selftest.py` 9/9 把关键回归固化，CI 就绪。剩余 5 个 MINOR 属于「度量精度 / 文档边角 / 案例包一致性」，不影响用户按 SKILL 完成 4×8h 或判定「能不能见客户」，建议作为 v0.1.2 的收尾项：

1. 修 N1（flow ❓ 只数节点信心表）+ selftest 回归。
2. 修 N4（修正记录支持续行）或把格式写进模板。
3. 统一 N3 的文档门槛描述（四条证据阈值 + negate）。
4. N2 合并引用、N5 案例 ❓ 比例一并处理。
5. N6–N8 文档/仓库卫生。
