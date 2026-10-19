# M1.5 真实导出实测（Live Test）

> 2026-10-19 已实测一次，结果与踩坑见 [`m15-live-test-result.md`](m15-live-test-result.md)。

> 目标：在真实 DSH 环境里装三个插件，跑一次 `industry_map` / `industry_track` / `company_scan` / `scout_export`，再用 `m15_compose.py` 生成导入草稿，验证适配层不是纸上谈兵。

## 0. 准备

- DSH 0.2.x（当前桌面 App 即可）
- 三个插件（社区包）：
  - `dsh-industry-research`（0.3.19 测试过）
  - `dsh-scout`（0.9.3 测试过）
  - `@weibaohui/dsh-kb`（0.7.15 测试过；可选，用于材料沉淀）

### 安装方式（二选一）

**A. 桌面 App（推荐）**

1. 设置 → 插件 → Discover（插件市场）；
2. 搜索 `dsh-industry-research`、`dsh-scout`、`@weibaohui/dsh-kb`；
3. 逐个安装，按提示重启会话/应用。

**B. CLI（非 desktop profile）**

```bash
dsh plugin --profile web add dsh-industry-research
dsh plugin --profile web add dsh-scout
dsh plugin --profile web add @weibaohui/dsh-kb
```

> 桌面 App 的 `desktop` profile 一般要在 App 内装；CLI 可能拒绝。

装完后在会话里确认工具存在：`industry_map`、`industry_track`、`company_scan`、`scout_start`。

## 1. 跑一次真实导出

新建一个空工作区（或直接用当前工作区），在会话里粘贴：

```text
帮我做 M1.5 实测，用「网络文学」这个行业：
1) 调 industry_map：industry="网络文学"，renderSvg=true，depth="quick"
2) 调 industry_track：industry="网络文学"，topics=["网络文学 政策","微短剧 备案","AI 生成内容 标识"]，since="2025-01-01"，depth="quick"
3) 调 company_scan：name="阅文集团"，web=true，depth="quick"
4) 用 dsh-scout 对「阅文集团」做一次尽调（目标岗位：内容运营负责人），最后 scout_export 导出
完成后把所有导出文件的绝对路径列给我，不要改我的 ramp/ 目录。
```

如果工具名/参数对不上，让 Agent 按插件 README 调整；关键是拿到导出文件。

### 预期导出

| 插件 | 产物 |
|---|---|
| `industry_map` | `<workspace>/industry-research/网络文学/chain.json`、`sources.json`、`chain.svg` |
| `industry_track` | `<workspace>/industry-research/网络文学/timeline.jsonl` |
| `company_scan` | `<workspace>/industry-research/companies/阅文集团/card.json`、`card.md` |
| `dsh-scout` | `<scoutDir>/<caseId>/case.json`（五文件导出） |

> 实际路径以 Agent 报告为准；不同插件配置的 root 可能不同。

## 2. 整理成 imports/

在仓库根目录：

```bash
mkdir -p imports/industry-research imports/scout

# 把上面拿到的文件按下面结构复制（路径换成实际路径）
cp -R /path/to/industry-research/网络文学 imports/industry-research/
cp -R /path/to/industry-research/companies imports/industry-research/
cp -R /path/to/scout/<caseId> imports/scout/
```

最终结构：

```text
imports/
  industry-research/网络文学/chain.json
  industry-research/网络文学/sources.json
  industry-research/网络文学/timeline.jsonl
  industry-research/companies/阅文集团/card.json
  scout/<caseId>/case.json
```

## 3. 一键导入

```bash
python3 scripts/m15_compose.py --imports imports --out-dir ramp-m15
```

产出：

- `ramp-m15/chain-seed.md` / `.mmd`
- `ramp-m15/sources-imported.jsonl`
- `ramp-m15/timeline-import.md`
- `ramp-m15/company-card-阅文集团.md`
- `ramp-m15/scout-import.md`
- `ramp-m15/m15-composition-report.md`（执行记录 + 合并清单）

## 4. 合并与验证

按报告第 3 节合并到真实 `ramp/`，然后：

```bash
python3 scripts/render_sources.py --root ramp
python3 scripts/validate_artifacts.py --root ramp
python3 scripts/readiness.py --root ramp
```

**不要**把 `ramp-m15/` 当最终工作区；它是导入草稿。

## 5. 记录对比

| 指标 | 不接插件 | 接插件 |
|---|---|---|
| 第 1 步用时（人工估） |  |  |
| 有来源节点/总节点 |  |  |
| 来源条数 / A、B 级占比 |  |  |
| 玩家表覆盖 |  |  |
| 返工次数（补来源/改口径） |  |  |

## 6. 把结果发回来

把这些发给 Lead：

1. 四个导出文件的绝对路径（或打包）；
2. `m15-composition-report.md`；
3. 任何失败/工具名对不上的地方；
4. 上面第 5 节的对比表（能填多少填多少）。

Lead 会用这些做合并和 strict 验证，并把真实导出与样例 fixture 的差异补进适配层。
