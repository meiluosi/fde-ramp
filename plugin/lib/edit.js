/**
 * Table editing helpers for the M2 write tools.
 *
 * Pure string-in/string-out so the behavior can be tested without a DSH
 * runtime. The tool layer owns file resolution and sandbox policy.
 */
import { cells } from './parse.js'

function findTable(markdown, predicate) {
  const lines = String(markdown).split('\n')
  for (let i = 0; i < lines.length; i++) {
    if (!lines[i].trim().startsWith('|')) continue
    const header = cells(lines[i])
    if (!predicate(header)) continue
    const sep = (lines[i + 1] || '').trim()
    if (!sep.startsWith('|')) continue
    const rows = []
    let j = i + 2
    for (; j < lines.length; j++) {
      if (!lines[j].trim().startsWith('|')) break
      rows.push({ line: j, cells: cells(lines[j]) })
    }
    return { lines, headerLine: i, header, rows, next: j }
  }
  return undefined
}

function setCell(line, cellIndex, value) {
  const row = cells(line)
  row[cellIndex] = String(value)
  return '| ' + row.join(' | ') + ' |'
}

function columnIndex(header, ...needles) {
  for (const needle of needles) {
    const exact = header.findIndex(h => h === needle)
    if (exact >= 0) return exact
  }
  return header.findIndex(h => needles.some(n => h.includes(n)))
}

function rowByActivity(table, activity) {
  const i = columnIndex(table.header, '环节/活动', '环节')
  if (i < 0) return undefined
  return table.rows.find(row => (row.cells[i] || '').includes(activity))
}

function rowById(table, id) {
  const i = columnIndex(table.header, '环节ID', '环节 ID')
  return table.rows.find(row => (row.cells[i] || '') === id)
}

function parseNumber(value) {
  const text = String(value ?? '').replace(/,/g, '').trim()
  const match = text.match(/[-+]?\d+(?:\.\d+)?/)
  return match === null ? undefined : Number(match[0])
}

function parseRate(value) {
  const text = String(value ?? '').trim()
  const n = parseNumber(text)
  if (n === undefined) return undefined
  if (text.includes('%')) return n / 100
  return n > 1 ? n / 100 : n
}

function recompute(row, header) {
  const iMinutes = columnIndex(header, '耗时')
  const iFreq = columnIndex(header, '日频次')
  const iRate = columnIndex(header, '出错率')
  const iCost = columnIndex(header, '单次代价')
  const iHourly = columnIndex(header, '人力单价')
  const minutes = parseNumber(row[iMinutes])
  const freq = parseNumber(row[iFreq])
  const rate = iRate >= 0 ? parseRate(row[iRate]) : 0
  const cost = iCost >= 0 ? parseNumber(row[iCost]) : 0
  const hourly = parseNumber(row[iHourly])
  if (minutes === undefined || freq === undefined || hourly === undefined) return undefined
  const labor = minutes / 60 * freq * hourly
  const risk = (rate ?? 0) * freq * (cost ?? 0)
  return { labor, risk, ceiling: labor + risk }
}

/** Edit one activity-table cell. */
export function updateActivities(markdown, { activity, column, value }) {
  const table = findTable(markdown, header => header.some(h => h.includes('业务域')) && header.some(h => h.includes('流程')) && header.some(h => h.includes('环节')))
  if (!table) throw new Error('activities.md 里没有找到活动表')
  const row = rowByActivity(table, activity)
  if (!row) throw new Error(`没有找到活动「${activity}」`)
  const ci = columnIndex(table.header, column)
  if (ci < 0) throw new Error(`没有找到列「${column}」；表头是：${table.header.join(' / ')}`)
  const oldValue = row.cells[ci] || ''
  table.lines[row.line] = setCell(table.lines[row.line], ci, value)
  return { markdown: table.lines.join('\n'), activity, column: table.header[ci], oldValue, newValue: String(value) }
}

/** Edit one process-metrics row and recompute the three cost columns. */
export function updateMetrics(markdown, { id, activity, minutes, frequency, errorRate, costPerError, hourlyRate, who }) {
  const table = findTable(markdown, header => header.some(h => h.includes('耗时')) && header.some(h => h.includes('日频次')))
  if (!table) throw new Error('process-metrics.md 里没有找到数字表')
  const row = id ? rowById(table, id) : rowByActivity(table, activity)
  if (!row) throw new Error(id ? `没有找到环节「${id}」` : `没有找到活动「${activity}」`)

  const set = (needles, value) => {
    if (value === undefined) return
    const ci = columnIndex(table.header, ...needles)
    if (ci < 0) throw new Error(`没有找到列「${needles[0]}」`)
    table.lines[row.line] = setCell(table.lines[row.line], ci, value)
  }
  const iId = columnIndex(table.header, '环节ID', '环节 ID')
  const iActivity = columnIndex(table.header, '环节/活动', '环节')
  set(['耗时'], minutes)
  set(['日频次'], frequency)
  set(['出错率'], errorRate === undefined ? undefined : `${errorRate}%`)
  set(['单次代价'], costPerError)
  set(['人力单价'], hourlyRate)
  set(['谁做', '职级'], who)

  const updatedCells = cells(table.lines[row.line])
  const computed = recompute(updatedCells, table.header)
  if (computed) {
    const setComputed = (needles, value) => {
      const ci = columnIndex(table.header, ...needles)
      if (ci >= 0) table.lines[row.line] = setCell(table.lines[row.line], ci, value.toFixed(2))
    }
    setComputed(['每天人力成本', '人力成本'], computed.labor)
    setComputed(['每天风险成本', '风险成本'], computed.risk)
    setComputed(['改进上限'], computed.ceiling)
  }
  return {
    markdown: table.lines.join('\n'),
    id: iId >= 0 ? updatedCells[iId] : '',
    activity: iActivity >= 0 ? updatedCells[iActivity] : '',
    computed,
    line: row.line + 1,
  }
}

/** Simple line diff: changed region only, enough for previews. */
export function diffLines(before, after) {
  const a = String(before).split('\n')
  const b = String(after).split('\n')
  let start = 0
  while (start < a.length && start < b.length && a[start] === b[start]) start++
  let endA = a.length - 1
  let endB = b.length - 1
  while (endA >= start && endB >= start && a[endA] === b[endB]) { endA--; endB-- }
  const out = []
  for (let i = start; i <= endA; i++) out.push('- ' + a[i])
  for (let i = start; i <= endB; i++) out.push('+ ' + b[i])
  return out.join('\n')
}

/** Apply multiple metrics updates in order. */
export function updateMetricsBatch(markdown, updates) {
  let current = markdown
  const results = []
  for (const update of updates) {
    const result = updateMetrics(current, update)
    current = result.markdown
    results.push({ id: result.id, activity: result.activity, line: result.line, computed: result.computed })
  }
  return { markdown: current, results }
}

/** Apply multiple activity-cell updates in order. */
export function updateActivitiesBatch(markdown, updates) {
  let current = markdown
  const results = []
  for (const update of updates) {
    const result = updateActivities(current, update)
    current = result.markdown
    results.push({ activity: result.activity, column: result.column, oldValue: result.oldValue, newValue: result.newValue })
  }
  return { markdown: current, results }
}
