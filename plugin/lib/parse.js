/**
 * Markdown table parsing for the M2 read-only tools.
 *
 * These functions are intentionally dependency-free so they can be tested
 * with `node --test` without a DSH runtime.
 */

/** @typedef {{ header: string[], rows: string[][] }} Table */

/** Split a markdown table row into trimmed cells. */
export function cells(line) {
  return line.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(cell => cell.trim())
}

function isSeparator(row) {
  return row.length > 0 && row.every(cell => /^:?-{3,}:?$/.test(cell) || /^---$/.test(cell))
}

/** Extract all markdown tables (header + body rows). */
export function parseTables(markdown) {
  const lines = String(markdown).split('\n')
  /** @type {Table[]} */
  const tables = []
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    if (!line.startsWith('|')) continue
    const header = cells(line)
    const next = (lines[i + 1] || '').trim()
    if (!next.startsWith('|')) continue
    const sep = cells(next)
    if (!isSeparator(sep)) continue
    /** @type {string[][]} */
    const rows = []
    let j = i + 2
    for (; j < lines.length; j++) {
      const rowLine = lines[j].trim()
      if (!rowLine.startsWith('|')) break
      const row = cells(rowLine)
      if (!isSeparator(row)) rows.push(row)
    }
    tables.push({ header, rows })
    i = j - 1
  }
  return tables
}

/** Count players and relations in a chain.md. */
export function chainStats(markdown) {
  let players = 0
  let relations = 0
  for (const table of parseTables(markdown)) {
    const header = table.header.join(' ')
    if (/玩家/.test(header) && /现状/.test(header)) {
      players += table.rows.filter(row => row[0] && !/^玩家$/.test(row[0])).length
    }
    if (/^from$/i.test(table.header[0] || '') && /关系/.test(header) && /to/i.test(header)) {
      relations += table.rows.filter(row => row[0]).length
    }
  }
  return { players, relations }
}

/** Count activity rows/columns and ❓ rows in an activities.md. */
export function activityStats(markdown) {
  for (const table of parseTables(markdown)) {
    const header = table.header.join(' ')
    if (!/业务域/.test(header) || !/流程/.test(header) || !/环节/.test(header)) continue
    const rows = table.rows.filter(row => row.some(cell => cell.length > 0))
    const uncertain = rows.filter(row => row.some(cell => cell.includes('❓'))).length
    return { rows: rows.length, columns: table.header.length, uncertain }
  }
  return { rows: 0, columns: 0, uncertain: 0 }
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

function findColumn(header, ...needles) {
  return header.findIndex(h => needles.some(n => h.includes(n)))
}

/** Compute four-number process metrics from process-metrics.md. */
export function metricsStats(markdown, days = 250) {
  const empty = {
    rows: 0, computed: 0, incomplete: 0,
    laborPerDay: 0, riskPerDay: 0, ceilingPerDay: 0, ceilingPerYear: 0, top: [],
  }
  for (const table of parseTables(markdown)) {
    const h = table.header
    if (!h.some(x => x.includes('耗时')) || !h.some(x => x.includes('日频次'))) continue
    const iId = findColumn(h, '环节ID', '环节 ID')
    const iActivity = findColumn(h, '环节/活动', '环节')
    const iMinutes = findColumn(h, '耗时')
    const iFreq = findColumn(h, '日频次')
    const iRate = findColumn(h, '出错率')
    const iCost = findColumn(h, '单次代价')
    const iHourly = findColumn(h, '人力单价')
    if (iMinutes < 0 || iFreq < 0 || iHourly < 0) continue
    const rows = table.rows.filter(row => row.some(cell => cell.length > 0))
    let computed = 0
    let incomplete = 0
    let labor = 0
    let risk = 0
    const top = []
    for (const row of rows) {
      const minutes = parseNumber(row[iMinutes])
      const freq = parseNumber(row[iFreq])
      const hourly = parseNumber(row[iHourly])
      const rate = iRate >= 0 ? parseRate(row[iRate]) : 0
      const cost = iCost >= 0 ? parseNumber(row[iCost]) : 0
      if (minutes === undefined || freq === undefined || hourly === undefined) {
        incomplete++
        continue
      }
      const laborRow = minutes / 60 * freq * hourly
      const riskRow = (rate ?? 0) * freq * (cost ?? 0)
      const ceiling = laborRow + riskRow
      labor += laborRow
      risk += riskRow
      computed++
      top.push({
        id: iId >= 0 ? row[iId] : '',
        activity: iActivity >= 0 ? row[iActivity] : '',
        ceiling: Math.round(ceiling * 100) / 100,
      })
    }
    top.sort((a, b) => b.ceiling - a.ceiling)
    const ceiling = labor + risk
    return {
      rows: rows.length,
      computed,
      incomplete,
      laborPerDay: Math.round(labor * 100) / 100,
      riskPerDay: Math.round(risk * 100) / 100,
      ceilingPerDay: Math.round(ceiling * 100) / 100,
      ceilingPerYear: Math.round(ceiling * days * 100) / 100,
      top: top.slice(0, 5),
    }
  }
  return empty
}

/** Parse AI opportunities and pick the first project (rightmost in the first quadrant). */
export function opportunityStats(markdown) {
  const empty = { count: 0, scored: 0, red: 0, firstProject: '', note: '没有找到机会表' }
  const tables = parseTables(markdown)
  const candidateTable = tables.find(t => t.header.some(h => h.includes('机会ID')) && t.header.some(h => h.includes('信号')))
  const scoreTable = tables.find(t => t.header.some(h => h.includes('业务价值')) && t.header.some(h => h.includes('可行性')))
  if (!candidateTable && !scoreTable) return empty

  const candidates = new Map()
  if (candidateTable) {
    const h = candidateTable.header
    const iId = findColumn(h, '机会ID')
    const iSignals = findColumn(h, '命中信号', '信号')
    for (const row of candidateTable.rows) {
      const id = iId >= 0 ? row[iId] : row[0]
      if (!id) continue
      const signals = new Set(String(iSignals >= 0 ? row[iSignals] : '').match(/[1-6]/g) ?? [])
      candidates.set(id, { id, signals: signals.size })
    }
  }

  const scored = new Map()
  if (scoreTable) {
    const h = scoreTable.header
    const iId = findColumn(h, '机会')
    const iValue = findColumn(h, '业务价值')
    const iFeas = findColumn(h, '可行性')
    const iData = findColumn(h, '数据可得性')
    const iPolitics = findColumn(h, '政治阻力')
    const iRed = findColumn(h, '红灯')
    for (const row of scoreTable.rows) {
      const id = iId >= 0 ? row[iId] : row[0]
      if (!id) continue
      const value = parseNumber(row[iValue])
      const feasibility = parseNumber(row[iFeas])
      const data = parseNumber(row[iData])
      const politics = parseNumber(row[iPolitics])
      const redText = iRed >= 0 ? String(row[iRed]).trim() : ''
      const red = (data !== undefined && data <= 2) || (politics !== undefined && politics <= 2) || /红/.test(redText)
      scored.set(id, { id, value, feasibility, data, politics, red })
    }
  }

  const ids = new Set([...candidates.keys(), ...scored.keys()])
  const items = [...ids].map(id => ({ ...(candidates.get(id) ?? { id, signals: 0 }), ...(scored.get(id) ?? { id }) }))
  const red = items.filter(i => i.red).length
  const qualified = items.filter(i => !i.red && (i.value ?? 0) >= 4 && (i.feasibility ?? 0) >= 4)
  qualified.sort((a, b) => (b.feasibility ?? 0) - (a.feasibility ?? 0) || (b.value ?? 0) - (a.value ?? 0))
  return {
    count: items.length,
    scored: scored.size,
    red,
    firstProject: qualified[0]?.id ?? '',
    note: qualified.length
      ? '第一项目 = 第一象限（价值/可行性≥4 且无红灯）里可行性最高者；不是价值最高者。'
      : '没有满足「价值/可行性≥4 且无红灯」的机会；先解决红灯或补评分。',
    items,
  }
}
