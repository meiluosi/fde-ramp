import test from 'node:test'
import assert from 'node:assert/strict'
import { updateActivities, updateMetrics } from '../lib/edit.js'

const metrics = `# 数字表

| 环节ID | 业务域 | 环节/活动 | 谁做 | 耗时（分钟/次） | 日频次（次/天） | 出错率（%） | 单次代价（元） | 人力单价（元/小时） | 每天人力成本 | 每天风险成本 | 改进上限 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A01 | 审核 | 初审 | 运营 | 12 | 200 | 3% | 50 | 60 |  |  |  |
| A02 | 审核 | 复审 | 编辑 | 10 | 100 | 1% | 10 | 50 |  |  |  |
`

test('updateMetrics writes four numbers and recomputes', () => {
  const result = updateMetrics(metrics, { id: 'A01', minutes: 15 })
  assert.equal(result.id, 'A01')
  assert.equal(result.computed.labor, 3000)
  assert.equal(result.computed.risk, 300)
  assert.equal(result.computed.ceiling, 3300)
  assert.match(result.markdown, /\| A01 \| 审核 \| 初审 \| 运营 \| 15 \| 200 \| 3% \| 50 \| 60 \| 3000\.00 \| 300\.00 \| 3300\.00 \|/)
})

test('updateMetrics can change error rate/cost/rate', () => {
  const result = updateMetrics(metrics, { activity: '复审', errorRate: 2, costPerError: 20, hourlyRate: 60 })
  assert.ok(Math.abs(result.computed.labor - 1000) < 1e-9)
  assert.equal(result.computed.risk, 40)
  assert.equal(result.computed.ceiling, 1040)
  assert.match(result.markdown, /2%/)
})

test('updateMetrics rejects unknown row/column', () => {
  assert.throws(() => updateMetrics(metrics, { id: 'NOPE', minutes: 1 }), /没有找到环节/)
})

const activities = `# 活动

| 业务域 | 流程 | 环节/活动 | 做什么 | 谁做 | 信心 |
|---|---|---|---|---|---|
| 审核 | 初审 | 机器审核 | 过机审 | 运营 | ✅ |
| 审核 | 初审 | 人工复核 | 抽检 | 编辑 | ❓ |
`

test('updateActivities changes one cell', () => {
  const result = updateActivities(activities, { activity: '人工复核', column: '信心', value: '✅' })
  assert.equal(result.oldValue, '❓')
  assert.match(result.markdown, /\| 审核 \| 初审 \| 人工复核 \| 抽检 \| 编辑 \| ✅ \|/)
  assert.match(result.markdown, /机器审核 \| 过机审/)
})

test('updateActivities rejects unknown row/column', () => {
  assert.throws(() => updateActivities(activities, { activity: '无', column: '信心', value: 'x' }), /没有找到活动/)
  assert.throws(() => updateActivities(activities, { activity: '人工复核', column: '不存在', value: 'x' }), /没有找到列/)
})
