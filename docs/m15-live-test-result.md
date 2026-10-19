# M1.5 真实导出实测结果（2026-10-19）

- 环境：DSH 桌面 App（0.2.1-rc.1），workspace `/Users/meros/Documents/GitHub`
- 插件版本：`dsh-industry-research 0.3.23`、`dsh-scout 0.9.3`、`@weibaohui/dsh-kb 0.7.15`
- 测试行业：网络文学；目标公司：阅文集团；岗位：内容运营负责人
- 约束：**没有动 `ramp/` 目录**；所有导出与组合产物都在 `/Users/meros/Documents/GitHub/m15-live/`

## 1. 真实导出

### industry_map

```text
/Users/meros/Documents/GitHub/industry-research/网络文学/chain.json
/Users/meros/Documents/GitHub/industry-research/网络文学/chain.svg
/Users/meros/Documents/GitHub/industry-research/网络文学/sources.json
/Users/meros/Documents/GitHub/industry-research/网络文学/timeline.jsonl
```

结果：9 个节点 / 9 条边 / 10 个指标缺口；2 个瓶颈节点（平台=枢纽型，IP 改编=漏斗型）。

### industry_track

```text
/Users/meros/Documents/GitHub/industry-research/网络文学/timeline.jsonl
```

结果：新增 9 条（《微短剧发展管理办法》、AI 生成内容标识相关、网络文艺政策等）。
注意：`depth=quick` 下部分条目**日期/分类为空**；导入器会把它们标为 `未分类 / ❓`。

### company_scan

```text
/Users/meros/Documents/GitHub/industry-research/companies/阅文集团/card.json
/Users/meros/Documents/GitHub/industry-research/companies/阅文集团/card.md
```

结果：公开网页来源 2 条；因为没有提供 `dataFiles`，业务结构/财务要点/风险点均为待补（符合工具设计）。

### dsh-scout

```text
/tmp/m15-scout-export/yuewen-m15/case.json
/tmp/m15-scout-export/yuewen-m15/sources.json
/tmp/m15-scout-export/yuewen-m15/claims.json
/tmp/m15-scout-export/yuewen-m15/events.jsonl
/tmp/m15-scout-export/yuewen-m15/report.md
/tmp/m15-scout-export/yuewen-m15/export.complete.json
```

已复制到：

```text
/Users/meros/Documents/GitHub/m15-live/imports/scout/yuewen-m15/
```

结果：5 条来源、5 条主张（1 条身份、1 条岗位待核验）、12 条访谈问题；决策仍为 **VERIFY**（主体未核验）。

## 2. 组合结果

```text
/Users/meros/Documents/GitHub/m15-live/ramp-m15/
  chain-seed.md
  chain-seed.mmd
  chain.svg
  sources-imported.jsonl
  timeline-import.md
  company-card-阅文集团.md
  scout-import.md
  m15-composition-report.md
```

`m15_compose.py`：**4/4 成功，失败 0**。  
`chain-seed.md`：9 节点 / 9 边 / 来源映射 5 条（`S1`→`S01` … `S5`→`S05`）。

## 3. 实测发现的坑

### 3.1 `scout_export` 在 workspace-write 下被拒绝

- 写入 workspace 内任意目录都报：`file access denied under workspace-write mode`；
- 写入 `/tmp` 成功；
- 处理：先导出到 `/tmp`，再复制进 workspace。已在 `docs/m15-live-test.md` 和 `references/adapters.md` 记录。
- 影响：真实环境用 scout 导出时，要么把 `targetDir` 指到 `/tmp`，要么等插件/宿主修复 workspace 写权限。

### 3.2 `industry_track` 的 quick 模式条目信息不全

- 日期为空、无 `evidenceCategory`；
- 导入器把无日期/无分类的条目标为 `未分类 / ❓`，不会丢；
- 需要更完整的时间线时用 `standard`/`comprehensive`，或显式传 `evidenceCategory`。

### 3.3 `company_scan` 没有数据文件时只有网页线索

- 不给 `dataFiles`，业务结构/财务/风险全是待补；
- 真实用的时候先把年报摘录/数据表放进 workspace，再传给 `dataFiles`（v1 不解析 PDF）。

## 4. 结论

- 适配层在真实导出上可用：4 个导入器 + 组合器全部跑通；
- 唯一阻塞是 `scout_export` 的 workspace 写权限，有 `/tmp` 绕行方案；
- 下一步：把 `ramp-m15/` 的草稿合并进真实 `ramp/`，再跑 strict validator / readiness；并考虑给上游报 `scout_export` 的权限问题。


## 5. 合并成完整 ramp（2026-10-19 追加）

把 `ramp-m15/` 草稿并入网文行业包，生成完整工作区：

```text
/Users/meros/Documents/GitHub/m15-live/ramp-m15-full/
```

合并内容：网文包 8 域 / 25 活动 / 77 术语 / 14 玩家 / 10 关系；`chain-seed`、`timeline-import`、`company-card-阅文集团`、`scout-import`、`m15-composition-report`；来源合并为 **44 条**（行业包 34 + industry_map 5 + scout 5）。

检查结果：

```text
validate_artifacts.py --strict -> OK
readiness.py --check -> PASS（五维 3.0）
```

注意：`corrections.md` 仍是模拟访谈；阅文主体/岗位/财报口径仍待验证。完整 ramp 的 README 里写了同一套诚实声明。
