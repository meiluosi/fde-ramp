# 复核：`scout_export` 在 workspace-write 下失败，是不是 issue？

**结论：是 `dsh-scout` 插件侧的 bug，不是 DSH 核心的 bug，也不是我们的用法错误。**

有 `/tmp` 绕行方案，所以不是阻断性问题；但对“导出到工作区”这个正常用法来说，是实打实的兼容缺陷。

## 1. 复现

环境：

- DSH 桌面运行时 **0.2.1-rc.2**
- `dsh-scout` **0.9.3**
- 文件策略：`workspace-write`
- 会话工作区：`/Users/meros/Documents/GitHub`

调用：

```text
scout_export({ caseId: "yuewen-m15", targetDir: "/Users/meros/Documents/GitHub/m15-live/scout/yuewen-m15" })
```

结果：

```text
EXPORT FAILED (/Users/meros/Documents/GitHub/m15-live/scout/yuewen-m15):
cannot write ".../export.complete.json": file access denied under workspace-write mode
```

同一调用改到 `/tmp`：

```text
scout_export({ caseId: "yuewen-m15", targetDir: "/tmp/m15-scout-export/yuewen-m15" })
→ exported to /tmp/m15-scout-export/yuewen-m15 (complete: true)
```

默认目录（`dsh-scout/yuewen-m15`）同样失败；说明不是某个自定义路径的问题。

## 2. 代码级原因

`dsh-scout@0.9.3` 的写文件代码（`dist/index.js:310-313`）：

```js
const target = await fs.resolve(`${targetDir}/${fileName}`, { cwd, signal });
...
await fs.writeText(target, content, undefined, signal);
```

注意：**没有传第 5 个参数 `sandboxPolicy`**。

DSH 的 `dsh-fs-sandbox` 在 `writeText` 里会这样取策略（`lib/index.js:154`）：

```js
const policy = sandboxPolicy ?? this.ctx.sandboxPolicy.resolve();
```

不传 `sandboxPolicy` 时，`resolve()` 没有 session，就用**部署回退 root**（进程 cwd），而不是当前会话的 workspace root；`workspace-write` 的可写根是：

```js
writableRoots(policy) = [policy.workspaceRoot, "/tmp", os.tmpdir()]
```

所以：

- 会话工作区 `/Users/meros/Documents/GitHub/...` 不在回退 root 下 → 拒绝；
- `/tmp` 永远在可写根里 → 成功。

对比 DSH 自己的文件写工具 `@deepseek-ai/dsh-tool-fs`（`lib/index.js:605-610`）：

```js
const sandboxPolicy = await sandbox.resolvePolicy("write", args, exec);
...
await ctx.fs.writeText(target, input.content, intent, exec.signal, sandboxPolicy);
```

它把**带 session 的 policy** 传进去了，所以正常文件写工具可以在 workspace 内写。

## 3. 为什么说是插件 bug，不是 DSH bug

- `ctx.fs.writeText` 的第 5 个参数是公开的 per-call policy 入口；DSH 自己的工具按约定传了；
- `dsh-scout` 用 `ctx.get('fs')` 写文件，但没把 tool execution 的 session policy 传进去；
- 在没挂 `dsh-fs-sandbox`（用 `fs-local`）的环境里不会触发，所以插件作者的测试环境很可能没覆盖；
- 修复应落在 `dsh-scout`：在 `persistFiles` 里拿到当前 tool 的 `exec`，解析 policy 并传入；而不是让 DSH 放宽沙箱。

## 4. 建议修复（插件侧）

`persistFiles` 增加 `policy` 参数：

```js
const policy = ctx.get('sandboxPolicy')?.resolve({
  session: exec.agent?.session,
});
await fs.writeText(target, content, undefined, signal, policy);
```

如果 `exec` 不便下传，至少应在 `scout_export` 的 execute 里解析一次，传给 `exportCase` / `persistFiles`。

## 5. 影响面

- 只影响 `scout_export` 的写文件；`scout_start` / `add_source` / `add_claim` / `report` 是内存操作，不受影响；
- `scout_import` 读文件不受影响（读不被围栏）；
- 绕行：导出到 `/tmp`，再复制进 workspace；已写进 `docs/m15-live-test.md` 和 `references/adapters.md`。

## 6. 上游 issue 草稿

- 仓库：https://github.com/MaxHou-infinity/dsh-scout
- 标题：`scout_export` fails under DSH `workspace-write` (fs-sandbox) when target is inside the session workspace
- 正文要点：环境版本、复现步骤、错误文本、代码行、根因、`/tmp` 绕行、建议修复。
- 已发到上游：https://github.com/MaxHou-infinity/dsh-scout/issues/1（2026-10-19，标题/repro/根因/建议修复齐全）。

## 7. 复核结论

之前说“像是插件/宿主权限兼容问题”是对的，但更准确的说法是：

> **dsh-scout 没有把 tool execution 的 sandbox policy 传给 `fs.writeText`，导致挂载 `dsh-fs-sandbox` 时 workspace 写入被拒；DSH 核心行为符合设计。**
