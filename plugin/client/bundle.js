/* Generated from client/index.js by scripts/build-client.mjs — do not edit by hand. */
window.__ModuleLoader__.load({
  id: "dsh-fde-ramp",
  factory: (require) => {
    var module = { exports: {} }
    var exports = module.exports
    Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" })
    var React = require("react")
    'use strict'

    /**
     * dsh-fde-ramp — client half (M3 panel).
     *
     * A DOM-only sidebar entry + full-screen overlay. It fetches
     * /fde-ramp/api/snapshot and renders:
     *   - four-number table with labor/risk/ceiling cards
     *   - opportunity quadrant (SVG) and the first-project hint
     *
     * Kept dependency-free on purpose: the Host half owns file access and parsing
     * is duplicated in a tiny, testable function set below.
     */

    const API = '/fde-ramp/api'
    const STYLE_ID = 'dsh-fde-ramp-style'
    const ENTRY_ID = 'dsh-fde-ramp-entry'
    const OVERLAY_ID = 'dsh-fde-ramp-overlay'
    const ENTRY_ATTR = 'data-dsh-fde-ramp-entry'

    function injectStyle() {
      if (document.getElementById(STYLE_ID)) return
      const style = document.createElement('style')
      style.id = STYLE_ID
      style.textContent = `
        .dsh-fde-ramp-entry{display:flex;align-items:center;gap:8px;width:100%;margin:2px 0 8px;padding:8px 10px;border:1px solid #d8dee4;border-radius:8px;background:#fff;color:#1f2328;cursor:pointer;font:inherit;text-align:left}
        .dsh-fde-ramp-entry:hover{background:#f6f8fa}
        .dsh-fde-ramp-entry-icon{font-size:16px}
        .dsh-fde-ramp-overlay{position:fixed;inset:0;z-index:9999;background:#f6f8fa;display:flex;flex-direction:column;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#1f2328}
        .dsh-fde-ramp-head{display:flex;align-items:center;gap:10px;padding:12px 16px;background:#fff;border-bottom:1px solid #d8dee4}
        .dsh-fde-ramp-head h2{font-size:16px;margin:0;white-space:nowrap}
        .dsh-fde-ramp-head input{flex:1;min-width:180px;padding:7px 9px;border:1px solid #d8dee4;border-radius:7px;font:inherit;font-size:13px}
        .dsh-fde-ramp-head button{padding:7px 12px;border:1px solid #d8dee4;border-radius:7px;background:#fff;cursor:pointer;font:inherit;font-size:13px}
        .dsh-fde-ramp-head button.primary{background:#1f883d;border-color:#1f883d;color:#fff}
        .dsh-fde-ramp-body{flex:1;overflow:auto;padding:18px;max-width:1180px;width:100%;margin:0 auto;box-sizing:border-box}
        .dsh-fde-ramp-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin-bottom:16px}
        .dsh-fde-ramp-card{background:#fff;border:1px solid #d8dee4;border-radius:10px;padding:12px 14px}
        .dsh-fde-ramp-card .k{font-size:12px;color:#57606a}
        .dsh-fde-ramp-card .v{font-size:21px;font-weight:650;margin-top:4px}
        .dsh-fde-ramp-section{background:#fff;border:1px solid #d8dee4;border-radius:12px;padding:14px 16px;margin-bottom:16px;overflow:auto}
        .dsh-fde-ramp-section h3{font-size:15px;margin:0 0 10px}
        .dsh-fde-ramp-table{border-collapse:collapse;width:100%;font-size:12.5px}
        .dsh-fde-ramp-table th,.dsh-fde-ramp-table td{border-bottom:1px solid #eaeef2;padding:6px 8px;text-align:left;white-space:nowrap}
        .dsh-fde-ramp-table th{background:#f6f8fa;color:#57606a;font-weight:600}
        .dsh-fde-ramp-table tr.first td{background:#ecfdf3;font-weight:600}
        .dsh-fde-ramp-table tr.danger td{background:#fff1f0}
        .dsh-fde-ramp-quadrant{max-width:600px;width:100%;height:auto;display:block;margin:0 auto}
        .dsh-fde-ramp-hint{font-size:12.5px;color:#57606a;line-height:1.6}
        .dsh-fde-ramp-error{background:#fff1f0;color:#b42318;border:1px solid #ffccc7;border-radius:8px;padding:10px 12px;font-size:13px}
      `
      document.head.appendChild(style)
    }

    function sidebarRoot() {
      const column = document.querySelector('[data-pane="sidebar"], [class*="sidebarCol"], .dshDesktopUpstreamSidebar, .dshDesktopSidebarSurface')
      if (column === null) return undefined
      const logoOwner = column.querySelector('[class*="logoRow"]') && column.querySelector('[class*="logoRow"]').parentElement
      return logoOwner || column.firstElementChild || undefined
    }

    function newSessionButton(root) {
      const nested = root.querySelector('button[class*="newSession"]')
      if (nested) return nested
      for (const child of root.children) {
        if (child instanceof HTMLButtonElement && !child.matches('[' + ENTRY_ATTR + ']')) return child
      }
      return Array.from(root.querySelectorAll('button')).find(b => !b.matches('[' + ENTRY_ATTR + ']') && /新会话|新建会话|new session/i.test(b.textContent || ''))
    }

    function placeEntry(root, entry) {
      const button = newSessionButton(root)
      if (!button) return false
      if (entry.parentElement !== root) {
        const row = button.closest('[class*="logoRow"]')
        const base = (row && row.parentElement === root) ? row : button
        root.insertBefore(entry, base.nextSibling)
      }
      return true
    }

    function cells(line) {
      return line.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(s => s.trim())
    }

    function isSep(row) {
      return row.length > 0 && row.every(c => /^:?-{3,}:?$/.test(c))
    }

    function parseTables(md) {
      const lines = String(md || '').split('\n')
      const out = []
      for (let i = 0; i < lines.length; i++) {
        if (!lines[i].trim().startsWith('|')) continue
        const header = cells(lines[i])
        if (!(lines[i + 1] || '').trim().startsWith('|')) continue
        if (!isSep(cells(lines[i + 1]))) continue
        const rows = []
        let j = i + 2
        for (; j < lines.length; j++) {
          if (!lines[j].trim().startsWith('|')) break
          const row = cells(lines[j])
          if (!isSep(row)) rows.push(row)
        }
        out.push({ header, rows })
        i = j - 1
      }
      return out
    }

    function col(header, ...needles) {
      for (const n of needles) {
        const exact = header.findIndex(h => h === n)
        if (exact >= 0) return exact
      }
      return header.findIndex(h => needles.some(n => h.includes(n)))
    }

    function num(value) {
      const m = String(value == null ? '' : value).replace(/,/g, '').match(/[-+]?\d+(?:\.\d+)?/)
      return m ? Number(m[0]) : undefined
    }

    function rate(value) {
      const n = num(value)
      if (n === undefined) return undefined
      if (String(value).includes('%')) return n / 100
      return n > 1 ? n / 100 : n
    }

    function get(row, header, ...needles) {
      const i = col(header, ...needles)
      return i >= 0 && i < row.length ? row[i] : ''
    }

    function money(v) {
      return v === undefined ? '' : Number(v).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }

    function escapeHtml(value) {
      return String(value == null ? '' : value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
    }

    function buildData(data) {
      const metrics = []
      for (const t of parseTables(data.metrics)) {
        if (col(t.header, '耗时') < 0 || col(t.header, '日频次') < 0) continue
        for (const row of t.rows) {
          if (!row.some(Boolean)) continue
          const minutes = num(get(row, t.header, '耗时'))
          const freq = num(get(row, t.header, '日频次'))
          const error = rate(get(row, t.header, '出错率'))
          const cost = num(get(row, t.header, '单次代价'))
          const hourly = num(get(row, t.header, '人力单价'))
          const labor = minutes !== undefined && freq !== undefined && hourly !== undefined ? minutes / 60 * freq * hourly : undefined
          const risk = error !== undefined && freq !== undefined && cost !== undefined ? error * freq * cost : undefined
          metrics.push({
            id: get(row, t.header, '环节ID'), domain: get(row, t.header, '业务域'), activity: get(row, t.header, '环节/活动', '环节'),
            who: get(row, t.header, '谁做'), minutes, freq, error, cost, hourly, labor,
            risk, ceiling: labor !== undefined && risk !== undefined ? labor + risk : undefined,
            confidence: get(row, t.header, '信心'),
          })
        }
        break
      }
      const candidates = new Map()
      for (const t of parseTables(data.opportunities)) {
        if (col(t.header, '机会ID') >= 0 && col(t.header, '信号') >= 0) {
          for (const row of t.rows) {
            const id = get(row, t.header, '机会ID')
            if (!id) continue
            candidates.set(id, { id, signals: new Set((get(row, t.header, '信号').match(/[1-6]/g) || [])).size, ceiling: num(get(row, t.header, '改进上限')) })
          }
        }
        if (col(t.header, '业务价值') >= 0 && col(t.header, '可行性') >= 0) {
          for (const row of t.rows) {
            const id = get(row, t.header, '机会')
            if (!id) continue
            const item = candidates.get(id) || { id, signals: 0 }
            item.value = num(get(row, t.header, '业务价值'))
            item.feas = num(get(row, t.header, '可行性'))
            item.data = num(get(row, t.header, '数据可得性'))
            item.politics = num(get(row, t.header, '政治阻力'))
            item.red = (item.data !== undefined && item.data <= 2) || (item.politics !== undefined && item.politics <= 2) || String(get(row, t.header, '红灯')).includes('红')
            candidates.set(id, item)
          }
        }
      }
      const ops = [...candidates.values()]
      const qualified = ops.filter(o => !o.red && (o.value || 0) >= 4 && (o.feas || 0) >= 4)
      qualified.sort((a, b) => (b.feas || 0) - (a.feas || 0) || (b.value || 0) - (a.value || 0))
      return { metrics, ops, first: qualified[0] ? qualified[0].id : '' }
    }

    function renderSnapshot(container, data) {
      const { metrics, ops, first } = buildData(data)
      const totals = metrics.reduce((acc, x) => ({ labor: acc.labor + (x.labor || 0), risk: acc.risk + (x.risk || 0), ceiling: acc.ceiling + (x.ceiling || 0) }), { labor: 0, risk: 0, ceiling: 0 })
      const w = 560, h = 380, p = 46
      const sx = v => p + Math.max(0, Math.min(5, v || 0)) / 5 * (w - p * 2)
      const sy = v => h - p - Math.max(0, Math.min(5, v || 0)) / 5 * (h - p * 2)
      const points = ops.map(o => {
        const color = o.red ? '#b42318' : (o.id === first ? '#0a7f3f' : '#2563eb')
        return `<circle cx="${sx(o.feas).toFixed(1)}" cy="${sy(o.value).toFixed(1)}" r="${o.id === first ? 8 : 6}" fill="${color}"/><text x="${(sx(o.feas) + 9).toFixed(1)}" y="${(sy(o.value) + 4).toFixed(1)}" font-size="12">${escapeHtml(o.id)}</text>`
      }).join('')
      const metricRows = metrics.length ? metrics.map(x => `<tr><td>${escapeHtml(x.id)}</td><td>${escapeHtml(x.domain)}</td><td>${escapeHtml(x.activity)}</td><td>${escapeHtml(x.who)}</td><td>${x.minutes === undefined ? '' : x.minutes}</td><td>${x.freq === undefined ? '' : x.freq}</td><td>${x.error === undefined ? '' : (x.error * 100).toFixed(1) + '%'}</td><td>${money(x.cost)}</td><td>${money(x.hourly)}</td><td>${money(x.labor)}</td><td>${money(x.risk)}</td><td>${money(x.ceiling)}</td><td>${escapeHtml(x.confidence)}</td></tr>`).join('') : '<tr><td colspan="13">还没有填写 process-metrics.md</td></tr>'
      const opRows = ops.length ? ops.map(o => `<tr class="${o.red ? 'danger' : (o.id === first ? 'first' : '')}"><td>${escapeHtml(o.id)}</td><td>${o.signals}</td><td>${o.value ?? ''}</td><td>${o.feas ?? ''}</td><td>${o.data ?? ''}</td><td>${o.politics ?? ''}</td><td>${o.red ? '红灯' : '—'}</td><td>${money(o.ceiling)}</td></tr>`).join('') : '<tr><td colspan="8">还没有填写 opportunities.md</td></tr>'
      container.innerHTML = `
        <div class="dsh-fde-ramp-cards">
          <div class="dsh-fde-ramp-card"><div class="k">每天人力成本</div><div class="v">${money(totals.labor)} 元</div></div>
          <div class="dsh-fde-ramp-card"><div class="k">每天风险成本</div><div class="v">${money(totals.risk)} 元</div></div>
          <div class="dsh-fde-ramp-card"><div class="k">改进上限 / 天</div><div class="v">${money(totals.ceiling)} 元</div></div>
          <div class="dsh-fde-ramp-card"><div class="k">改进上限 / 年</div><div class="v">${money(totals.ceiling * 250)} 元</div></div>
        </div>
        <section class="dsh-fde-ramp-section"><h3>1. 四个数字与成本</h3>
          <table class="dsh-fde-ramp-table"><thead><tr><th>ID</th><th>业务域</th><th>环节</th><th>谁做</th><th>耗时</th><th>日频次</th><th>出错率</th><th>单次代价</th><th>人力单价</th><th>人力/天</th><th>风险/天</th><th>改进上限/天</th><th>信心</th></tr></thead><tbody>${metricRows}</tbody></table>
          <p class="dsh-fde-ramp-hint">数字不全的行不计入合计；人力单价必须来自 HR/财务或明确标“估算”。</p></section>
        <section class="dsh-fde-ramp-section"><h3>2. 机会象限：先右后上</h3>
          <svg class="dsh-fde-ramp-quadrant" viewBox="0 0 ${w} ${h}" role="img" aria-label="机会象限图">
            <rect x="${p}" y="${p}" width="${w - p * 2}" height="${h - p * 2}" fill="#fafafa" stroke="#d0d7de"/>
            <line x1="${p + (w - p * 2) / 2}" y1="${p}" x2="${p + (w - p * 2) / 2}" y2="${h - p}" stroke="#d0d7de" stroke-dasharray="4 4"/>
            <line x1="${p}" y1="${p + (h - p * 2) / 2}" x2="${w - p}" y2="${p + (h - p * 2) / 2}" stroke="#d0d7de" stroke-dasharray="4 4"/>
            <text x="${p + 8}" y="${p + 18}" font-size="12" fill="#0a7f3f">先做</text>
            <text x="${w - p - 50}" y="${p + 18}" font-size="12" fill="#6b7280">有价值但难</text>
            <text x="${p + 8}" y="${h - p - 8}" font-size="12" fill="#6b7280">先不做</text>
            <text x="${w - p - 80}" y="${h - p - 8}" font-size="12" fill="#6b7280">容易但价值低</text>
            ${points}
          </svg>
          <table class="dsh-fde-ramp-table"><thead><tr><th>机会</th><th>信号数</th><th>业务价值</th><th>可行性</th><th>数据可得性</th><th>政治阻力</th><th>红灯</th><th>改进上限/天</th></tr></thead><tbody>${opRows}</tbody></table>
          <p class="dsh-fde-ramp-hint">第一项目建议：<strong>${escapeHtml(first) || '暂无（需要价值/可行性≥4 且无红灯）'}</strong>。选第一象限里最靠右的，不是价值最高的。</p></section>
      `
    }

    function openOverlay() {
      let overlay = document.getElementById(OVERLAY_ID)
      if (overlay) { overlay.style.display = 'flex'; return }
      overlay = document.createElement('div')
      overlay.id = OVERLAY_ID
      overlay.className = 'dsh-fde-ramp-overlay'
      overlay.innerHTML = `
        <div class="dsh-fde-ramp-head">
          <h2>FDE 行业速成 · 算账与机会</h2>
          <input id="dsh-fde-ramp-root" value="${escapeHtml(localStorage.getItem('dsh-fde-ramp-root') || 'ramp')}" aria-label="ramp 路径">
          <button id="dsh-fde-ramp-refresh" class="primary">刷新</button>
          <button id="dsh-fde-ramp-close">关闭</button>
        </div>
        <div class="dsh-fde-ramp-body" id="dsh-fde-ramp-body"><p class="dsh-fde-ramp-hint">加载中…</p></div>`
      document.body.appendChild(overlay)
      const rootInput = overlay.querySelector('#dsh-fde-ramp-root')
      const body = overlay.querySelector('#dsh-fde-ramp-body')
      const load = async () => {
        const root = rootInput.value.trim() || 'ramp'
        localStorage.setItem('dsh-fde-ramp-root', root)
        body.innerHTML = '<p class="dsh-fde-ramp-hint">加载中…</p>'
        try {
          const res = await fetch(`${API}/snapshot?root=${encodeURIComponent(root)}`)
          const data = await res.json()
          if (!res.ok || !data.ok) throw new Error(data.error || res.statusText)
          renderSnapshot(body, data)
        } catch (error) {
          body.innerHTML = `<div class="dsh-fde-ramp-error">加载失败：${escapeHtml(error.message || error)}</div>`
        }
      }
      overlay.querySelector('#dsh-fde-ramp-refresh').addEventListener('click', load)
      overlay.querySelector('#dsh-fde-ramp-close').addEventListener('click', () => { overlay.style.display = 'none' })
      rootInput.addEventListener('keydown', event => { if (event.key === 'Enter') load() })
      load()
    }

    function mountEntry() {
      injectStyle()
      const entry = document.createElement('button')
      entry.id = ENTRY_ID
      entry.setAttribute(ENTRY_ATTR, '')
      entry.className = 'dsh-fde-ramp-entry'
      entry.innerHTML = '<span class="dsh-fde-ramp-entry-icon">📊</span><span>算账面板</span>'
      entry.addEventListener('click', openOverlay)
      let root
      let placed = false
      const tryPlace = () => {
        if (root && !root.isConnected) { root = undefined; placed = false }
        if (placed && document.body.contains(entry)) return
        root = root || sidebarRoot()
        if (!root) return
        placed = placeEntry(root, entry)
      }
      const observer = new MutationObserver(() => tryPlace())
      observer.observe(document.body, { childList: true, subtree: true })
      const timer = setInterval(tryPlace, 2000)
      tryPlace()
      return () => {
        observer.disconnect()
        clearInterval(timer)
        try { entry.remove() } catch {}
        try { document.getElementById(OVERLAY_ID)?.remove() } catch {}
      }
    }

    module.exports = {
      name: 'dsh-fde-ramp',
      inject: [],
      apply(ctx) {
        const dispose = mountEntry()
        if (ctx && typeof ctx.effect === 'function') ctx.effect(() => () => dispose(), 'dsh-fde-ramp: panel')
        else window.addEventListener('beforeunload', dispose, { once: true })
      },
    }

    return module.exports
  }
})
