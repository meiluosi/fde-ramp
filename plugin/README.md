# dsh-fde-ramp（M2 骨架）

这是 `fde-ramp` 的 DSH 插件起点。当前注册 **9 个工具**（5 个只读 + 2 个单条写 + 2 个批量写），另有 Web 端侧栏面板。

- `ramp_status({ root? })`：读取 ramp 的 `state.json`、`sources.jsonl`，返回是否初始化、来源数、活动行数、五维自评；
- `ramp_chain({ root? })`：统计 `chain.md` 的玩家表/关系表行数；
- `ramp_activities({ root? })`：统计活动表；优先 `activities.md`，compact 布局回退 `business.md`；
- `ramp_metrics({ root?, days? })`：读 `process-metrics.md`，算每天人力/风险成本、改进上限、年化；
- `ramp_opportunities({ root? })`：读 `opportunities.md`，数信号/四维/红灯，按「第一象限最靠右」给第一项目；
- `ramp_metrics_update({ root?, id?/activity?, minutes?, frequency?, errorRate?, costPerError?, hourlyRate?, who? })`：写回四个数字/人力单价，并重算三个成本列；
- `ramp_activities_update({ root?, activity, column, value })`：按活动名和列名改一个单元格；
- `ramp_metrics_batch({ root?, updates[], dryRun? })`：批量改数字，自动重算；写前备份、支持 diff 预览；
- `ramp_activities_batch({ root?, updates[], dryRun? })`：批量改单元格，写前备份、支持 diff 预览。

侧栏「算账面板」：点击后打开全屏面板，输入 ramp 路径，显示四数字表、成本卡片、机会象限和第一项目。数据走 Host 路由 `/fde-ramp/api/snapshot`。

## 还没做

- `ramp_chain`：读写 `chain.md` / `chain.mmd`，校验玩家/关系；
- `ramp_activities`：活动表行列编辑与 ❓ 高亮；
- `ramp_metrics`：四个数字 + 成本/改进上限计算；
- `ramp_opportunities`：六信号/四维打分/第一项目；
- 面板与 npm 发布。

路线见 [`../plugin/roadmap.md`](../plugin/roadmap.md)。

## 本地开发

在仓库根目录：

```bash
node --check plugin/lib/index.js
node --test plugin/test/parse.test.mjs
```

当前 13 项单测（解析 6 + 编辑 7）全过；客户端 bundle 由 `npm run build:client` 生成；真实 DSH profile 调用记录见 [`../docs/m15-plugin-live-test.md`](../docs/m15-plugin-live-test.md)。

装进 DSH profile：

```bash
# web / tui 等非 Electron 管理的 profile
dsh plugin --profile web add /absolute/path/to/fde-ramp/plugin
```

桌面 App 的 `desktop` profile 由 Electron 独占管理，CLI 会拒绝：

```text
error: profile "desktop" is managed exclusively by the Electron application
```

当前已验证的手工安装方式（2026-10-19）：

1. 备份 `~/.dsh/profiles/desktop/{package.json,cordis.patch.yml,pnpm-lock.yaml}`；
2. 把 `plugin/` 复制到 `~/.dsh/profiles/desktop/node_modules/dsh-fde-ramp/`；
3. 在 profile 的 `package.json` dependencies 加 `"dsh-fde-ramp": "file:/.../plugin"`，并在 `dsh.profile.bundles` 末尾加 `"dsh-fde-ramp"`；
4. 重启/热加载 DSH 后，工具列表里出现 `ramp_status` 等工具。

> 本仓库还没有把该包发布到 npm；先本地路径安装/测试。

## 设计约束

- 只读工具不写文件；后续写工具必须走 DSH 的 fs 沙箱 policy（参考 `dsh-tool-fs` 的 `resolvePolicy`），不要绕开；
- 不重复实现 `dsh-industry-research` / `dsh-scout` 的能力，只做 ramp 工作区的读写与校验；
- 所有数字/结论都必须能回到 ramp 文件与来源。
