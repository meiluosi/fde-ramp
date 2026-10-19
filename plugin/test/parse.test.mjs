import test from 'node:test'
import assert from 'node:assert/strict'
import { activityStats, chainStats, metricsStats, opportunityStats, parseTables } from '../lib/parse.js'

const chain = `# 链路

## 玩家

| 玩家 | 角色 | 现状 | 来源 |
|---|---|---|---|
| 玩家A | 平台 | 自述 | S01 |
| 玩家B | 渠道 | 推断 | S02 |
|  |  | 空行 |  |

## 关系

| from | 关系类型 | to | 证据 |
|---|---|---|---|
| 玩家A | 供应 | 玩家B | 合同 |
| 玩家B | 渠道 | 玩家A | 推断 |
`

const activities = `# 活动

| 业务域 | 流程 | 环节/活动 | 做什么 | 信心 |
|---|---|---|---|---|
| 域1 | 流程1 | 活动1 | 做1 | ✅ |
| 域1 | 流程1 | 活动2 | 做2 | ❓ |
`

test('parseTables extracts header and rows', () => {
  const tables = parseTables(chain)
  assert.equal(tables.length, 2)
  assert.deepEqual(tables[0].header.slice(0, 2), ['玩家', '角色'])
  assert.equal(tables[0].rows.length, 3)
})

test('chainStats counts non-empty players and relations', () => {
  assert.deepEqual(chainStats(chain), { players: 2, relations: 2 })
})

test('activityStats counts rows/columns/uncertain', () => {
  assert.deepEqual(activityStats(activities), { rows: 2, columns: 5, uncertain: 1 })
})

test('empty/missing tables return zeros', () => {
  assert.deepEqual(chainStats(''), { players: 0, relations: 0 })
  assert.deepEqual(activityStats(''), { rows: 0, columns: 0, uncertain: 0 })
})

const metrics = `# 数字表

| 环节ID | 业务域 | 环节/活动 | 谁做 | 耗时（分钟/次） | 日频次（次/天） | 出错率（%） | 单次代价（元） | 人力单价（元/小时） | 每天人力成本 | 每天风险成本 | 改进上限 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A01 | 域1 | 活动1 | 运营 | 12 | 200 | 3% | 50 | 60 |  |  |  |
| A02 | 域1 | 活动2 | 运营 |  | 100 | 1% | 10 | 50 |  |  |  |
`

test('metricsStats computes labor/risk/ceiling', () => {
  const stats = metricsStats(metrics)
  assert.equal(stats.rows, 2)
  assert.equal(stats.computed, 1)
  assert.equal(stats.incomplete, 1)
  assert.equal(stats.laborPerDay, 2400)
  assert.equal(stats.riskPerDay, 300)
  assert.equal(stats.ceilingPerDay, 2700)
  assert.equal(stats.ceilingPerYear, 675000)
})

const opportunities = `# 机会

| 机会ID | 对应环节 | 机会描述 | 命中信号（1–6） | 预估改进上限（元/天） | 备注 |
|---|---|---|---|---|---|
| O1 | A01 | 自动审核 | 1,2,5 | 2700 |  |
| O2 | A02 | 自动结算 | 1,3 | 5000 |  |
| O3 | A03 | 自动推荐 | 2,4 | 3000 |  |

| 机会 | 业务价值（1–5） | 可行性（1–5） | 数据可得性（1–5） | 政治阻力（5=阻力小） | 红灯 | 结论 |
|---|---|---|---|---|---|---|
| O1 | 4 | 5 | 4 | 4 | 无 | 先做 |
| O2 | 5 | 3 | 4 | 4 | 无 | 难 |
| O3 | 5 | 4 | 1 | 4 | 数据红 | 先不做 |
`

test('opportunityStats picks rightmost first-quadrant project', () => {
  const stats = opportunityStats(opportunities)
  assert.equal(stats.count, 3)
  assert.equal(stats.scored, 3)
  assert.equal(stats.red, 1)
  assert.equal(stats.firstProject, 'O1')
})
