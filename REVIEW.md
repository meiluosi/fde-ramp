# fde-ramp · 独立验收报告（v0.1 MVP）

- **验收人**：fde-verifier（独立于作者）
- **验收时间**：2026-10-18 01:53 CST
- **范围**：`SKILL.md`、`references/*`（8，含审查期间新增的 `source-hunting.md`）、`templates/*`（14）、`scripts/*`（3）、`README.md`、`plugin/roadmap.md`、`examples/README.md`、`industries/coalbed-methane/*`（8 + example-run 5）
- **方式**：通读 + 实跑脚本 + 13 个边界用例 + 24 条来源逐条 `curl` 抽检 + 交叉 grep 一致性
- **快照**：仓库无 `.git`，按文件快照验收。关键文件 sha256 前 12 位：`SKILL.md be3b0829423e`、`README.md 3e6819341c15`、`references/source-hunting.md 9b8634e14654`、`scripts/init_ramp.py 5a853487f13a`、`scripts/validate_artifacts.py a65ec4d6be54`、`scripts/readiness.py 41d11bb67a61`、`industries/coalbed-methane/glossary.md 42219dc0172f`、`industries/coalbed-methane/README.md f8fc7482dd55`。验收期间 Lead 持续编辑（01:51–01:53 新增 `references/source-hunting.md` 并更新 `SKILL.md`/`README.md`），本报告已按 01:53 快照复核；行号以该快照为准，若文件再变请以内容为准。
- **说明**：本报告只写 `REVIEW.md`，未改动任何其他文件；临时工作区都在 `/tmp`。真实安装到 `~/.dsh/skills/fde-ramp` 需要在工作区外写文件（本会话权限不允许），故用 `/tmp/fake-skills/fde-ramp -> 仓库` 的符号链接等价验证。

---

## 一、结论：**PASS WITH FIXES**

BLOCKER **0** ／ MAJOR **6** ／ MINOR **9** ／ NIT **4**。

**可以接受为 v0.1 skill-first MVP 交付。** 四条方法论（建图→术语校准→标猜测→被否定）与五维就绪度都已逐条落地，脚本可跑、符号链接安装可用，案例包 24 条来源全部 HTTP 200 且抽查数字与标题基本对得上，还主动声明了「无券商研报 / 无客户文档 / 无 verified」的缺口——这是加分项，不是缺陷。

但**质量闸门目前不可信**：validator 的计数会被空壳模板满足，readiness 可被 `--set` 直接刷成 PASS，且五维门槛的文档说法与脚本行为不一致。这三件事直接关系到「用户凭什么相信『我准备好了』」，必须在 v0.2 前修。另有 1 处全国/山西口径标签错误、`verified` 语义残留、example-run 引用 id 与 sources id 不统一等一致性问题。

---

## 二、摘要（5 条）

1. **方法论覆盖：完整。** 4×8h 四块在 `SKILL.md` 都有独立的动作/产物/验收/常见错误，且中间两块的关键约束（① 术语必须客户文档校准、官方源最高只到 `public`；② 流程图必须有具体 ❓ 且必须能「一句话被纠正」）写在 principles 与 glossary-protocol/map-and-negate，不是口号。Block 4 有开场话术、七条现场规则、`corrections.md` 记录模板和「不辩护」纪律。
2. **可执行性：能跑，但验收可被绕过。** `init_ramp.py` → `validate_artifacts.py` → `readiness.py` 在空目录一次通过、无 `{{}}` 残留、symlink + 任意 cwd 正常；但空壳 ramp 会被 validator 数出 `verification=5 / corrections=3 / guessed nodes=3`，readiness 在完全没有产物时也能 `gate: PASS`。
3. **案例包：数据底子好，少数口径/统计错。** 24/24 URL 可打开，标题与内容基本匹配；抽查的 181.3 亿 m³、8.644 亿 m³/a、1709 口井、55.59 亿元、12.25 亿 m³、7000 万 m³、260/180/300 亿 m³ 等均能在原文找到。错在标签与统计：把**全国** 2015 利用率 86.4%/35.3% 标成「山西」；术语状态统计写 39/33/6，实际 38/34/6。
4. **一致性：6 条 MAJOR 里 4 条是「文档 vs 脚本/模板」互相打架。** 五维门槛、`verified` 定义、来源 id 约定、产物清单/时间盒四组对不上；其中门槛与 id 两处有实测证据。
5. **产品味：合格，偏「对话就绪」不是「报告」。** 有开场白、被否定姿势、问法原话、对话演练评分卡与「不要用于」边界；风险是参考资料偏长（案例包 1400+ 行），建议 v0.2 补一页纸「Day-1 速查」与端到端 ramp 示例，别让文档把用户淹掉。

---

## 三、Findings

### MAJOR（6）

| # | 严重度 | 文件:行 | 问题 | 建议修法 |
|---|---|---|---|---|
| M1 | MAJOR | `SKILL.md:191`；`README.md:99`；`templates/readiness.md:19`；`references/readiness-rubric.md:3` vs `references/readiness-rubric.md:76`；`scripts/readiness.py:66,73` | **五维门槛两套说法。** 文档说「门槛：五项都 ≥3，且无一项 <2」；rubric 的「总分与门槛」和脚本实际是 `min≥2 且 avg≥3 且 结构/语言≥3`。实测 `3,4,3,3,2`（avg 3.00，对话 2）→ 脚本 `gate: PASS`，按 SKILL/README 应 FAIL。 | 二选一：① 统一文案为「目标五维≥3；门槛 min≥2 + avg≥3 + 结构/语言≥3」；② 或把脚本收紧为 `min>=3`。推荐①，并在 readiness 输出里同时打印「目标/门槛」两行，避免歧义。 |
| M2 | MAJOR | `scripts/readiness.py:44-66`（只读 state.json）；对照 `SKILL.md:231`、`references/method.md:94,96`、`templates/plan.md:36` | **就绪度可被自报分数刷过，且无 Block 4 闸门。** 空壳 ramp（sources 0、glossary 空、corrections 只有模板标题）执行 `--set structure=4 language=4 players=4 decision=4 dialogue=4` 即 `gate: PASS`。这与「没有 Block 4 的速成不算速成」「见不到一线最多 2 分」「评分必须挂证据」直接冲突。 | 在 `readiness.py` 增加证据闸门：`corrections>=5` 且 `state.blocks.negate=="done"` 才允许 gate PASS；否则输出 `gate: FAIL (no Block 4 evidence)` 或自动 cap≤2。加 `--evidence` 必填（指向 readiness.md 行号）或新增 `--auto` 从产物推导分数上限。 |
| M3 | MAJOR | `scripts/validate_artifacts.py:65-94`（glossary_count）；`:148-151`（verification）；`:153-156`（flow ❓ 阈值）；`:158-159`（corrections） | **validator 的「通过/计数」可被空壳与散文满足。** 实测：空壳模板 → `verification: 5`（来自 5 行空表）、`corrections: 3`（来自 3 个空标题）、`guessed nodes: 3`（来自 `> 信心标记` 和表头里的 ❓ 字符）；把案例包 glossary（78 词）放进 ramp → 数出 `terms: 81`、状态 `public39/needs-customer35/unsure7`（真实 38/34/6），因为把「状态统计」汇总表也当成术语行。 | ① 只统计「术语/猜点」非空的核心字段行；② ❓ 只数节点信心表的单元格（如 `^\|.*\|.*❓.*\|` 且首列为节点名），阈值改 ≥5（与 SKILL Block 3 验收一致）；③ corrections 计数要求 `## 修正 N` 下有非空「我原以为/实际」；④ 跳过「状态统计」「易混对」等辅助表。 |
| M4 | MAJOR | `templates/glossary.md:4`；对照 `references/glossary-protocol.md:4,15`；`SKILL.md:37` | **`verified` 语义残留。** 模板写「`verified`（客户/**官方文档**确认）」，但协议铁律是「公开源再权威也只能到 `public`；`verified` 只认客户/一线」，案例包也声明「一个 verified 都没有」。SKILL:37「没有客户文档/官方文件佐证 → 必须是 needs-customer」也留了「官方文件≈可确认」的歧义。 | 模板改为「`verified`（**客户文档或一线员工**确认）」；SKILL:37 补一句「官方文件最高只能到 `public`，见 glossary-protocol §1」；在 glossary 模板首行加一行四状态定义，避免复制时回退。 |
| M5 | MAJOR | `industries/coalbed-methane/example-run/README.md:19`、`day1-value-chain.md:18-19,31-33`、`day3-flow-guesses.md:29-42` 对照 `sources.jsonl` 的 id（`CBM-Sxx`）与 `industries/coalbed-methane/README.md:125` | **example-run 的引用 id 与 sources id 对不上。** example-run 声称「`[S15]` 指向 `../sources.jsonl`」，但 sources 的 id 是 `CBM-S15`；README 只说「机械映射为 `[S01]`…」却没说要同时改 sources id。实测把案例 sources.jsonl + `day1-value-chain.md` 放进 ramp → validator 报 6 条 `unknown source ref [S01]/[S15]/[S03]/[S14]`。 | 统一 id：推荐 `sources.jsonl` 用 `S01…S24`，另加 `"alias":"CBM-S01"` 字段或正文注释；或反向把 example-run 改成 `[CBM-S15]` 并让 validator 支持 `CBM-S` 前缀。同步更新案例 README §8 的映射说明。 |
| M6 | MAJOR | `scripts/validate_artifacts.py:17-29`（REQUIRED）、`:128`（只扫根目录 `*.md`）、`state.json:29-40`（artifacts）对照 `scripts/init_ramp.py:21-35`、`SKILL.md:64-79`、`templates/readiness.md:28` | **产物清单四处不一致。** init 会生成 `calibration-log.md`/`drill-scorecard.md` 且 SKILL 输出目录未列；SKILL/`state.artifacts` 列了 `flow.mmd`/`value-chain.mmd` 但 validator REQUIRED 不要求；`templates/readiness.md:28` 与 rubric:71 又引用 `drills/`（init 从不创建）；validator 只扫根目录 md，`drills/*.md` 永远不会被检查。 | 以 init 实际产物为唯一真源：补 `flow.mmd`/`value-chain.mmd`/`calibration-log.md`/`drill-scorecard.md` 到 SKILL 输出目录与 `state.artifacts`；要么创建 `drills/` 并把评分卡放进去，要么把 rubric/readiness 模板里的 `drills/` 改成 `drill-scorecard.md`；validator 用 `rglob("*.md")`。 |

### MINOR（9）

| # | 严重度 | 文件:行 | 问题 | 建议修法 |
|---|---|---|---|---|
| m1 | MINOR | `README.md:16`、`SKILL.md:66`、`templates/plan.md:9` | 全篇说「32 小时冲刺」，但 `plan.md` 表是 4×8h + 收尾 2h = **34h**（SKILL 自己的收尾也写 1–2h）。用户按表勾选会发现对不上。 | 统一为「32h 四块 + 1–2h 收尾」，或在 SKILL/README 把时间盒写成「32–34h」。 |
| m2 | MINOR | `industries/coalbed-methane/README.md:40` | 「**山西** 2015 年利用率基准：煤层气 86.4%、煤矿瓦斯 35.3%」——`CBM-S06`（十三五规划「十二五」成就）是**全国**口径，不是山西。 | 改为「全国 2015 年利用率」；若要给山西，需另找山西来源或标「待验证」。 |
| m3 | MINOR | `industries/coalbed-methane/regulators.md:34` vs `sources.jsonl` 的 `CBM-S12.note` | regulators 把「DZ/T 0216（报批稿，**代** DZ/T 0216-2010）」写成事实；sources 备注却写「替代关系需核实」。 | 二选一：核实现行版后写死版本号，或统一写「报批稿；与 DZ/T 0216-2010 的替代关系待核实」。 |
| m4 | MINOR | `industries/coalbed-methane/value-chain.md:173`、`verification-list.md:97` | 「储量起算标准按**埋深**分档（<500、500—1000、1000—2000 **m³/d**）」——埋深单位应是 m，日产量单位才是 m³/d，量纲混写，容易被一线判定为外行。 | 按 DZ/T 0216 原文拆成「埋深档（m）」与「单井日产起算值（m³/d）」两列，并标「报批稿，待核现行版」。 |
| m5 | MINOR | `industries/coalbed-methane/verification-list.md:4` vs `:13-27` | 声称「优先级 = 风险×影响面÷验证成本」并「按此排序」，实际 #13（分 9.0）排在 #9–#12（6.0/4.5）之后；列表实际是按「风险」降序、组内再按分数，未严格按公式。 | 要么按「分」重排，要么把规则改成「先按风险分档，组内再按 风险×影响面÷成本」。 |
| m6 | MINOR | `industries/coalbed-methane/glossary.md:183-185` | 状态统计写 `public 39 / needs-customer 33 / unsure 6`，实际解析为 **38 / 34 / 6**（合计 78 正确）。 | 用脚本重算后回填；建议把该表加进 `validate_artifacts.py --strict` 校验。 |
| m7 | MINOR | `industries/coalbed-methane/example-run/day3-flow-guesses.md:64` | 「❓ 占比 6/14 ≈ 43%」——14 个节点里带 ❓ 的是 ①⑤⑨⑫⑭ 共 5 个（⑨ 写了两个 ❓），应为 5/14≈36%。 | 重数并改写；顺带把「满 ❓」与「25% 下限」的说法对齐（flow.md 实际 5/14≈36%）。 |
| m8 | MINOR | `references/evidence.md:72-78`；`references/evidence.md:22` vs `sources.jsonl` 全 24 行；`references/source-hunting.md:57-60` | 文档说 validator 会检查「没有 `TODO` / `<...>` 占位符」「`[S#]` 都能找到」「state 计数一致」；脚本实际只查 `{{`，且 sources 只校验 id/title/url/tier，不校验 `usedFor/accessed/published`。另外文档给的 `usedFor` 是数组，24 条真实数据全是字符串。新增的 `source-hunting.md` 要求「sources ≥10、A/B ≥5」，validator 同样没有实现。 | 补 validator 检查（占位符、usedFor 类型、accessed 日期、published 为 ISO 或 `unknown`、sources 数量与 A/B 比例），或把 evidence.md 改成「当前只检查以下 N 项」。`usedFor` 统一为数组。 |
| m9 | MINOR | `scripts/validate_artifacts.py:120` | `state.json` 非法 JSON 时直接抛 Python traceback（`json.decoder.JSONDecodeError`），而不是清晰的 `ERROR: state.json: invalid JSON`；同文件对 `sources.jsonl` 是友好处理的。 | 用 try/except 包一层，输出 `ERROR: state.json: invalid JSON (…)` 并 `return 1`。 |

### NIT（4）

| # | 严重度 | 文件:行 | 问题 | 建议修法 |
|---|---|---|---|---|
| n1 | NIT | `SKILL.md:114` vs `references/glossary-protocol.md:87`、`README.md:116` | 候选池规模三处不一致：SKILL 写 80–120 词，协议/README 写 60–80，案例包 78。 | 统一为「先列 60–80（最多 120）候选，收敛到 ~50」。 |
| n2 | NIT | `industries/coalbed-methane/example-run/README.md:12` vs `day3-flow-guesses.md:1` | 文件名是 `day3-*`，README 把它排在「Day2 下午」，文件 H1 也写「Day2 下午产出」。 | 改名 `day2-flow-guesses.md` 或把节奏表改成 Day3。 |
| n3 | NIT | `README.md:86` | 「examples/ 预留」已过时（`examples/README.md` 已存在并指向 example-run）。 | 改为「examples/ 说明页；示例见 …」。 |
| n4 | NIT | `plugin/roadmap.md:100` vs `industries/coalbed-methane/README.md:124` | roadmap M0 验收写「用煤层气跑通 Day1–Day3；validator 通过」，案例包 README 却明确「不会通过 validator」。 | 明确 M0 验收对象是「用案例数据初始化出的 ramp 工作区」，并随 v0.2 补一个真实通过 validator 的端到端 ramp。 |

---

## 四、实测记录（命令 + 结果）

环境：macOS / `python3` 3.13（`/opt/miniconda3`）；所有工作区在 `/tmp`；会话日期 2026-10-18。

### 1) 初始化 → 校验 → 评分（主链路）

```bash
python3 scripts/init_ramp.py --industry "测试行业" --customer "测试客户" \
  --persona "技术负责人" --deadline 2026-10-25 --out /tmp/fde-review-ramp
# exit 0；生成 15 个文件（含 flow.mmd、value-chain.mmd、calibration-log.md、drill-scorecard.md）
# grep -rn '{{' /tmp/fde-review-ramp → 无结果（无未替换占位符）
# state.json: artifacts 已从 "ramp/xxx" 重写为 basename；started=2026-10-18

python3 scripts/validate_artifacts.py --root /tmp/fde-review-ramp
# exit 0，输出 OK
# root: /private/tmp/fde-review-ramp
# sources: 0  terms: 3  verification: 5  corrections: 3  guessed nodes: 3
# glossary statuses: {'verified': 0, 'needs-customer': 0, 'public': 0, 'unsure': 0}
# WARN ×5：glossary 仅 3 词、无状态列、state 计数与文件不一致（3/5/3）
# ↑ 注意：空壳就能凑出 verification=5、corrections=3、guessed nodes=3（见 M3）

python3 scripts/readiness.py --root /tmp/fde-review-ramp          # 全 0，FAIL，exit 0
python3 scripts/readiness.py --root /tmp/fde-review-ramp --check  # exit 1
# readiness 默认会写回 state.json（无 --no-write 时），属预期但有副作用，建议文档提示
```

### 2) 边界用例

| 用例 | 命令要点 | 结果 |
|---|---|---|
| 未知来源 `[S99]` | `value-chain.md` 追加 `某个数字 [S99]。` | `ERROR: value-chain.md: unknown source ref [S99]`，**exit 1** ✓ |
| 代码块里的 `[S99]` | 放进 ` ``` ` 围栏 | 被忽略，OK ✓ |
| `[CBM-S99]` | 正文写 CBM 前缀（案例包实际用的格式） | **不报错、exit 0** ✗（正则只认 `\[S(\d+)\]`，见 M5/m8） |
| flow 完全没有 ❓ | 删掉 flow.md 所有 `❓` | `WARN: flow: only 0 guessed nodes '❓' (target >=5)`，仍 exit 0（只有 `--strict` 才 1） |
| flow 只有 3 个真 ❓ | 追加 3 行节点 ❓ 表 | 计数变 6（3 散文 + 3 节点），**无 WARN** ✗（SKILL 要求 ≥5，阈值却是 <3） |
| glossary 为空 | glossary.md 写成无表格 | `WARN: only 0 numbered terms`；`--strict` 下 **exit 1** ✓ |
| 空壳 + 自报满分 | 空 ramp 执行 `--set` 五维=4 | `gate: PASS`，**exit 0** ✗（见 M2） |
| 文档门槛用例 | `--set structure=3 language=4 players=3 decision=3 dialogue=2` | `avg 3.00 / gate: PASS` ✗（文档要求五项≥3，见 M1） |
| 非法 state.json | `echo '{bad json' > state.json` | Python traceback（`JSONDecodeError`），无清晰 ERROR ✗（见 m9） |
| 案例 glossary 入 ramp | 复制 78 词 glossary 后跑 validator | `terms: 81`；statuses `public 39 / needs-customer 35 / unsure 7`（真实 78/38/34/6）✗（见 M3、m6） |
| example-run 引用入 ramp | 案例 sources.jsonl + `day1-value-chain.md` | 6 条 `ERROR: unknown source ref [S01]/[S15]/[S03]/[S14]` ✗（见 M5） |
| 非空目录初始化 | `--out /tmp/b9`（已有文件） | `refusing to overwrite non-empty dir … (use --force)`，**exit 2** ✓ |
| 非法分数 | `--set structure=5` | `score must be 0-4: 5`，**exit 2** ✓ |
| 符号链接 + 任意 cwd | `ln -s <repo> /tmp/fake-skills/fde-ramp`，`cd /tmp` 后执行 `/tmp/fake-skills/fde-ramp/scripts/init_ramp.py …` | exit 0，模板从真实仓库解析，`--out` 相对 cwd 正常 ✓（脚本 `REPO = Path(__file__).resolve().parent.parent` 对 symlink 正确） |

### 3) DSH 适配

- `SKILL.md` frontmatter 只有 `name: fde-ramp` + `description`，与 `~/.dsh/skills/material-audit|chain-authoring|gap-rehearsal` 的约定完全一致；`name` 与安装目录名 `fde-ramp` 匹配 ✓。
- 三条触发语（「一周内搞懂这个行业」「明天要见客户」「帮我准备行业 brief」）都在 description 里，符合技能发现习惯 ✓。
- `~/.dsh/skills/` 当前只有 material-audit / chain-authoring / gap-rehearsal 三个，`fde-ramp` 尚未安装；真实安装需在会话工作区外写文件，本会话不可执行，故只做了 symlink 等价验证。

---

## 五、案例包来源抽检（`curl -sSL -m 15`，2026-10-18）

**结果：24/24 全部 HTTP 200，且标题/内容与 `sources.jsonl` 的描述基本一致。** 抽查的数字大多能在原文定位（下表「核验」列）。`curl -L` 跟随了重定向；GBK 页面已转码读取。

| id | HTTP | 标题匹配 | 核验要点 |
|---|---|---|---|
| CBM-S01 | 200 | ✅ 国务院办公厅…意见 | 国办发 93 号、价格/补贴/矿权框架可见 |
| CBM-S02 | 200 | ✅ 国家能源局发布煤层气产业政策 | 是「发布消息」而非全文（备注已声明） |
| CBM-S03 | 200 | ✅ 关于“十三五”…补贴标准的通知 | 0.2→**0.3 元/立方米** 原文可查 |
| CBM-S04 | 200 | ✅ 清洁能源发展专项资金管理办法（奇台县政府转载） | 财建〔2025〕35 号通知本体 |
| CBM-S05 | 200 | ✅ 量补转效补（中国能源报） | **0.3—0.6 元/m³ 浮动**、2016—2019 补贴 62.4 亿、产量 44→59 亿，均命中 |
| CBM-S06 | 200 | ✅ 十三五规划（山东发改委转载） | 2015 全国 44/38 亿、利用率 **86.4%**；瓦斯 136/48、**35.3%**；均为**全国**口径（→ m2） |
| CBM-S07 | 200 | ✅ 政协第 0452 号答复 | 瓦斯发电装机超 **260 万千瓦**、页岩气/致密气补贴提及 |
| CBM-S08 | 200 | ✅ 政协第 00666 号答复摘要 | 「三气」共探共采、深层煤层气入科技重大专项 |
| CBM-S09 | 200 | ✅ 发改委令第 33 号 管网公平开放 | **2025-11-01 施行** 原文命中 |
| CBM-S10 | 200 | ✅ 基础设施规划建设与运营管理办法（第 35 号令） | **2026-01-01 施行** 原文命中 |
| CBM-S11 | 200 | ✅ 煤矿瓦斯抽采达标暂行规定（应急管理部） | 安监总煤装〔2011〕163 号通知本体 |
| CBM-S12 | 200 | ⚠️ PDF（26 页），标题不可机读 | 无法核对正文；备注已注明「报批稿」，建议保留「待核现行版」 |
| CBM-S13 | 200 | ✅ 故县区块探矿权挂牌出让公告 | 面积 **291.6799 km²**、预探、**5 年**、起始价 **204.4 万元**、收益率 **0.3%**、净资产≥5 亿，全部命中 |
| CBM-S14 | 200 | ✅ 柿庄南东区环评批复（栏目页标题泛化，正文命中） | **8.644×10⁸ m³/a**、1709 口井、集气站 6 座、管线 1754.61 km、**总投资 55.5949 亿元**、2022-03-23 批复，全部命中 |
| CBM-S15 | 200 | ✅ 蓝焰控股 2025 年报（新浪转载） | 全国 **181.3 亿**、山西 **147 亿**（81%）、销量 **12.25 亿**、毛利率 **31.35%**、0.97 万亿探明、近 5000 亿新增，全部命中 |
| CBM-S16 | 200 | ✅ 新天然气 2025 营收 39.24 亿（证券时报） | 归母净利 **8.07 亿**、全口径产量 **24.13 亿**、潘庄 **63 km² 连续四年稳产 10 亿**、马必 **9.51 亿（+9.31%）**，命中 |
| CBM-S17 | 200 | ✅ 杰瑞 2025 年报摘要（上海证券报） | 电驱压裂国内领先；压缩机组用于煤层气集输/发电，命中 |
| CBM-S18 | 200 | ✅ 石化油服 2025 年报全文（新浪转载） | 营收 **807.12 亿**（80,712,178 千元）、归母净利 **6.59 亿**（658,841 千元）、进尺 **1115 万米**，命中（备注里的国际准则 6.96 亿亦对） |
| CBM-S19 | 200 | ✅ “十五五”煤层气开发基础牢（中国能源报） | 2030 **260 亿 / 瓦斯 65 亿**、鄂东 **180 亿（深层 160 亿+）**、山西 **300 亿/产值千亿**，命中 |
| CBM-S20 | 200 | ✅ 山西前 4 个月产量超 50 亿（新华社/光明网） | **52.3 亿、+10%、占全国 81.5%**，命中 |
| CBM-S21 | 200 | ✅ 大吉煤岩气田单井突破 7000 万（新华网） | 7000 万 m³、4.5 万 m³/d、**连续稳产 29 个月**、2019 先导、2022-05 开钻、2022-12 压裂试气、2023-01 投产，全部命中 |
| CBM-S22 | 200 | ✅ 2025 分省产量（华经产业研究院） | 山西 **147**、陕西 **12**、贵州 **10.6** 亿 m³，命中；页面自身「东部/中部」矛盾在备注中已诚实标注 |
| CBM-S23 | 200 | ✅ 首家全国性煤层气公司再易主（中国能源报） | 1996 成立、2019 中海油 **53.35 亿**收购 100%，命中 |
| CBM-S24 | 200 | ✅ 甲烷排放控制行动方案（碳排放交易网转载，D 级） | **2025 年煤矿瓦斯年利用量 60 亿 m³**，命中 |

**抽检结论**：没有发现编造 URL/编造标题；关键数字与标题匹配良好；S12（PDF 标题）与 S14（栏目页标题）需人工打开确认，但正文/备注不矛盾。案例包「不编造、打不开就说打不开」的纪律执行得比常见草稿好。

---

## 六、逐条对照用户 4×8h 方法论

| 用户要求 | 落地位置 | 评价 |
|---|---|---|
| ① 读 3 份研报（券商深度优先）+ 客户年报/官网 + 监管文件目录，画价值链，知道钱从哪来到哪去 | `SKILL.md:87-105`（找法见 `references/source-hunting.md`）、`references/method.md:15-25`、`templates/value-chain.md`、案例 `value-chain.md`/`regulators.md` | ✅ 覆盖（含「2 份近 12 个月 + 1 份 3 年以上」）。案例包无券商研报，但已诚实声明并给出缺口处理——不算走样 |
| ② 约 50 词术语卡；AI 先列候选、**必须用客户实际文档逐个校准** | `SKILL.md:108-125`、`references/glossary-protocol.md` 全文、`templates/glossary.md`、`templates/calibration-log.md` | ✅ 覆盖且强调到位（候选三 miner、校准顺序、8 项终审、误用示例、状态机）。唯一残留是 M4 的 `verified` 模板措辞 |
| ③ 画流程图并**明确标出猜测**，形成待验证清单 | `SKILL.md:129-145`、`references/map-and-negate.md`、`templates/flow.md`、`templates/verification-list.md`、案例 `flow.md` | ✅ 覆盖（✅/⚠️/❓、每条 ❓ 必须写「我猜是 X」、风险×成本排序、Top15）。排序公式与实现有 m5 小偏差 |
| ④ 拿图去被一线否定：「我画了张图…您帮我改改」，记录被改的地方 | `SKILL.md:149-169`、`references/map-and-negate.md:43-110`、`templates/corrections.md`、`templates/drill-scorecard.md`、`references/personas.md` | ✅ 方法/话术/七条规则/记录格式/30 分钟清单都在。但**没有脚本/校验支撑**（validator 只数空标题，见 M3），且 readiness 不要求 Block 4（M2）；案例包 example-run 只到 Day3 上午，无 Block 4 记录样例 |
| 五维就绪度（结构/语言/玩家/决策/对话） | `SKILL.md:181-191`、`references/readiness-rubric.md`、`templates/readiness.md`、`scripts/readiness.py` | ✅ 五维定义与 0–4 锚点完整、证据要求明确；门槛文案与脚本不一致（M1） |

**未走样判定**：四块没有「被报告化」——SKILL 明确「目标不是写出一份行业报告」、列出「不要用于」、每块都有验收与常见错误，Block 4 的「没有 Block 4 的速成不算速成」写进了最短可行版。**唯一实质缺口是 Block 4 只有文档没有闸门**（M2 + validator 弱校验）。

---

## 七、产品判断（报告味 vs 对话就绪）

**优点（明显偏「对话就绪」）**

- 开场话术是可直接念的原话，不是「建议与客户沟通」；`verification-list.md` 15 条每条都有「我画了…您帮我改」的问法。
- 有「不要这样问」的反例、被纠正时「不辩护」的规则、访谈后 30 分钟清单、对话演练评分卡与三类人设——这些是现场动作，不是报告章节。
- 明确非目标与止损线（见不到一线 → 最多 2 分；Block 4 约不到 → 只交公开源版本）。
- 案例包 README §12 给「交付时怎么讲」的话术，`flow.md` §8 给「用这张图去被否定的正确姿势」。

**风险与建议**

- 参考材料偏长：案例包 1,400+ 行、`SKILL.md` 246 行，新人第一次用容易「先读文档再动手」，恰好是 SKILL 自己反对的失败模式。建议 v0.2 加一张 A4「第一小时做什么」速查卡（直接引用 3 条命令 + Block 1 的 6 个动作）。
- 缺少端到端可跑的 `ramp/` 示例：example-run 是文档样例，不是「init 出来的工作区」。用户想验证「跑通」时没有参照物（也是 n4/M6 的根因）。
- 「就绪度」目前是自评且无证据闸门，作为对外承诺有风险；README 已加「不是标准化考试」的免责，但脚本仍会打印 PASS，建议加一句「自评 PASS ≠ 可对外承诺」或按 M2 收紧。

---

## 八、v0.2 待办（8 条）

1. **统一五维门槛**：文案统一为「目标五维≥3；门槛 min≥2 + avg≥3 + 结构/语言≥3」，readiness 输出同时打印目标与门槛（M1）。
2. **给 readiness 加证据闸门**：`corrections≥5` + `blocks.negate=done` 才允许 PASS；否则 FAIL 或 cap≤2；可选 `--evidence` 指向 readiness.md 行号（M2）。
3. **修 validator 计数与阈值**：跳过空行/汇总表；只数节点信心表 ❓ 且设 ≥5；corrections 要求非空「我原以为/实际」；state.json 解析失败给清晰 ERROR（M3、m9）。
4. **统一来源 id**：sources.jsonl 改 `S01…S24`（保留 CBM alias）或 example-run 改 `[CBM-Sxx]`，validator 支持前缀；把 `--strict` 接进 CI（M5、m8）。
5. **修 `verified` 语义**：模板改为「客户文档或一线员工确认」；SKILL §3 明确「官方文件最高 public」（M4）。
6. **补端到端 ramp 示例**：`init_ramp` → 填案例数据 → `validate_artifacts --strict` → `readiness` 一次跑通，放进 `examples/`；同步 roadmap M0 验收口径（M6、n4）。
7. **案例包勘误**：全国/山西标签、DZ/T 替代关系、储量起算量纲、glossary 状态统计 39/33→38/34、example-run 6/14→5/14、verification-list 排序（m2–m7）。
8. **统一产物清单与时间盒**：calibration-log/drill-scorecard/drills/ 与 `state.artifacts`、validator REQUIRED 对齐；32h vs 34h 写清（M6、m1）。
