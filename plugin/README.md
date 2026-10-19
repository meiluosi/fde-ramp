# dsh-fde-ramp（M2 骨架）

这是 `fde-ramp` 的 DSH 插件起点。当前只注册一个只读工具：

- `ramp_status({ root? })`：读取 ramp 的 `state.json`、`sources.jsonl`，返回是否初始化、来源数、活动行数、五维自评。

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
```

装进 DSH profile（CLI）：

```bash
dsh plugin --profile web add /absolute/path/to/fde-ramp/plugin
```

> 本仓库还没有把该包发布到 npm；先本地路径安装/测试。

## 设计约束

- 只读工具不写文件；后续写工具必须走 DSH 的 fs 沙箱 policy（参考 `dsh-tool-fs` 的 `resolvePolicy`），不要绕开；
- 不重复实现 `dsh-industry-research` / `dsh-scout` 的能力，只做 ramp 工作区的读写与校验；
- 所有数字/结论都必须能回到 ramp 文件与来源。
