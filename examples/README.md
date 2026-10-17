# examples

这里放**跑出来的示例**，不是模板。模板在 [`../templates/`](../templates/)。

## 1. 完整跑通的运行（两个行业，推荐先看）

[`coalbed-methane-run/`](coalbed-methane-run/README.md)：煤层气，31 条来源、78 个候选术语、36 行活动表、5 处模拟访谈修正。
[`web-novel-run/`](web-novel-run/README.md)：网络文学，34 条来源、77 个候选术语、25 行活动表、5 处模拟访谈修正。

两个都是用 `init_ramp.py` 生成、走完四步、通过 `validate_artifacts.py --strict` 和 `readiness.py --check` 的完整 `ramp/` 工作区。**先看各自的 `README.md`，再按文件清单挑着看。**

## 2. 单步抽样子集

[`../industries/coalbed-methane/example-run/`](../industries/coalbed-methane/example-run/)：只挑一步的产物给你看格式。

- `step1-value-chain.md`：价值链草图（带 ❓）
- `step2-glossary-10.md`：10 张术语卡样例（状态为 `public`/`needs-customer`，无 `verified`）
- `step3-flow-guesses.md`：带 ❓ 的客户流程图
- `step3-verification-top5.md`：5 条「我画了…您帮我改」问法
- `step3-domains-activities.md`：业务域划分 + 活动表样例

这些示例的共同点是：**故意留错、故意标 ❓**。它们演示的是「怎么画出一张值得被人改的图」，不是「煤层气行业的标准答案」。
