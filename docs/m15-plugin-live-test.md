# dsh-fde-ramp 插件本地实测（2026-10-19）

## 1. 安装方式（隔离 profile）

为了避免动主力 `desktop` profile，我用一个隔离的 DSH 家目录做真实加载：

```text
/tmp/dsh-m15-home/
  .credentials.yaml        # 从 ~/.dsh 复制（本地测试用）
  llm-deepseek/
  profiles/m15h/           # 从 shipped headless profile 复制
    package.json           # bundles: dsh-base + dsh-headless + dsh-fde-ramp
    node_modules/dsh-fde-ramp/  # 本仓库 plugin/ 的副本
```

`dsh --profile m15h --dump-config` 能看到：

```text
# == dsh-fde-ramp
- id: dsh-fde-ramp
  name: dsh-fde-ramp
```

## 2. 真实 `ramp_status` 调用

```bash
DSH_HOME=/tmp/dsh-m15-home \
DEEPSEEK_API_KEY=*** \
npx -y @deepseek-ai/dsh@0.2.1-rc.2 --profile m15h \
  "请调用 ramp_status 工具，root 参数用 /Users/meros/Documents/GitHub/m15-live/ramp-m15-full-auto，然后把工具返回的内容原样贴出来。"
```

返回：

```text
ramp: /Users/meros/Documents/GitHub/m15-live/ramp-m15-full-auto
sources: 44  activities: 25
readiness: 3.0 (min 3)
只读检查；完整校验请运行 scripts/validate_artifacts.py --strict 与 scripts/readiness.py --check。
```

## 3. 真实 `ramp_metrics` / `ramp_opportunities` 调用

用一个小 fixture（`/tmp/m15-plugin-test`）填了四个数字和机会表：

```text
ramp_metrics 返回：
rows: 2  computed: 1  incomplete: 1
labor/day: 2400  risk/day: 300
ceiling/day: 2700  ceiling/year: 675000

ramp_opportunities 返回：
count: 3  scored: 3  red: 1
first project: O1
第一项目 = 第一象限（价值/可行性≥4 且无红灯）里可行性最高者；不是价值最高者。
```

与公式核对：

```text
12/60 × 200 × 60 = 2400
3% × 200 × 50 = 300
2400 + 300 = 2700 / 天
2700 × 250 = 675,000 / 年
```

## 3.5 真实写工具调用

用同一个 fixture 调 `ramp_metrics_update`（A01，minutes=15）：

```text
updated A01 (line 5)
labor/day: 3000  risk/day: 300  ceiling/day: 3300
已重算并写回三个成本列。
```

写回后的行：

```text
| A01 | 审核 | 初审 | 运营 | 15 | 200 | 3% | 50 | 60 | 3000.00 | 300.00 | 3300.00 | 观察 | ⚠️ |
```

`ramp_activities_update`（人工复核 / 信心 / ✅）也实际写回了 `activities.md`：

```text
updated 人工复核 / 信心
❓ -> ✅
```

## 4. 没做什么

- **没有改主力 `desktop` profile**；隔离 profile 在 `/tmp`，不持久；
- 没有把 API key 写进仓库；
- 没有发布 npm 包；
- 写工具只支持单行/单格更新，不做批量导入；写之前不会自动备份（git 工作区建议先提交）；
- M3 面板还没做。

## 5. 如果要装进主力 profile

```bash
# 需要 DSH CLI 可用；desktop profile 通常建议在 App 内装
dsh plugin --profile desktop add /Users/meros/Documents/GitHub/fde-ramp/plugin
```

装完重启 DSH，`ramp_status` / `ramp_chain` / `ramp_activities` / `ramp_metrics` / `ramp_opportunities` 就会出现。
