/**
 * Web-only companion: serves /fde-ramp/api/snapshot for the client panel.
 *
 * Split from the Host tools plugin so a headless profile (no webServer) can
 * still load the tools without waiting on an unavailable service.
 */
import { readFile } from 'node:fs/promises'
import { homedir } from 'node:os'
import { resolve, sep } from 'node:path'
import z from '@deepseek-ai/schemastery'

export const name = 'dsh-fde-ramp-panel'
export const inject = ['webServer']

export const Config = z.object({
  root: z.string().default('ramp'),
  workspaceRoot: z.string().default(''),
})

export function apply(ctx, config = {}) {
  const settings = { root: 'ramp', workspaceRoot: '', ...config }
  const workspaceRoot = resolve(settings.workspaceRoot || process.env.FDE_RAMP_WORKSPACE || resolve(homedir(), 'Documents', 'GitHub'))
  const webServer = ctx.webServer
  if (!webServer || typeof webServer.register !== 'function') return

  const sendJson = (res, status, value) => {
    res.writeHead(status, { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' })
    res.end(JSON.stringify(value))
  }

  ctx.effect(() => {
    const dispose = webServer.register({
      kind: 'prefix',
      path: '/fde-ramp/api',
      handler: async (req, res) => {
        if (ctx.connection && typeof ctx.connection.requestRejection === 'function') {
          const rejection = ctx.connection.requestRejection(req)
          if (rejection !== undefined) { res.writeHead(rejection); res.end(); return }
        }
        try {
          const url = new URL(req.url || '/', 'http://dsh.local')
          if (url.pathname !== '/fde-ramp/api/snapshot') {
            sendJson(res, 404, { ok: false, error: 'not found' })
            return
          }
          const requested = url.searchParams.get('root') || settings.root
          const root = resolve(workspaceRoot, requested)
          const inside = root === workspaceRoot || root.startsWith(workspaceRoot + sep)
          if (!inside) { sendJson(res, 403, { ok: false, error: 'root must be inside the configured workspace' }); return }
          const read = async (name) => {
            try { return await readFile(resolve(root, name), 'utf8') } catch { return undefined }
          }
          const state = await read('state.json')
          if (state === undefined) { sendJson(res, 404, { ok: false, error: `no ramp at ${root}` }); return }
          sendJson(res, 200, {
            ok: true,
            root,
            workspaceRoot,
            metrics: (await read('process-metrics.md')) ?? '',
            opportunities: (await read('opportunities.md')) ?? '',
            state: JSON.parse(state),
          })
        } catch (error) {
          sendJson(res, 500, { ok: false, error: String(error?.message || error) })
        }
      },
    })
    return () => { try { dispose?.() } catch {} }
  }, 'dsh-fde-ramp: dashboard api')
}
