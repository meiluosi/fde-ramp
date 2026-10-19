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
