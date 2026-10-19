import test from 'node:test'
import assert from 'node:assert/strict'
import { activityStats, chainStats, parseTables } from '../lib/parse.js'

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
