/**
 * dsh-fde-ramp — minimal M2 skeleton.
 *
 * Registers `ramp_status`, a read-only tool that inspects a ramp workspace.
 * The full toolset (ramp_chain / ramp_activities / ramp_metrics /
 * ramp_opportunities) is planned in plugin/roadmap.md.
 *
 * This package intentionally has no build step: it is plain ESM and can be
 * loaded by a DSH profile after `dsh plugin add`.
 */
import { readFile } from 'node:fs/promises'
import { homedir } from 'node:os'
import { resolve, sep } from 'node:path'
import { defineTool } from '@deepseek-ai/dsh-tools'
import z from '@deepseek-ai/schemastery'
import { activityStats, chainStats, metricsStats, opportunityStats } from './parse.js'
import { diffLines, updateActivities, updateActivitiesBatch, updateMetrics, updateMetricsBatch } from './edit.js'

export const name = 'dsh-fde-ramp'
export const inject = ['tools']

export const Config = z.object({
  /** Default ramp root relative to the workspace root. */
  root: z.string().default('ramp'),
  /** Workspace root used by the dashboard API; defaults to ~/Documents/GitHub. */
  workspaceRoot: z.string().default(''),
})

function sessionCwd(exec) {
  return exec?.agent?.session?.header?.cwd || process.cwd()
}

async function readJson(path) {
  try {
    return JSON.parse(await readFile(path, 'utf8'))
  } catch {
    return undefined
  }
}

async function readText(path) {
  try {
    return await readFile(path, 'utf8')
  } catch {
    return undefined
  }
}

async function countLines(path) {
  try {
    const text = await readFile(path, 'utf8')
    return text.split('\n').filter(line => line.trim()).length
  } catch {
    return 0
  }
}

async function writeBackup(ctx, exec, root, fileName, content) {
  const stamp = new Date().toISOString().replace(/[:.]/g, '-')
  const path = resolve(root, `.${fileName}.${stamp}.bak`)
  await writeWithPolicy(ctx, exec, path, content)
  return path
}

async function writeWithPolicy(ctx, exec, filePath, content) {
  const fs = ctx.get('fs')
  if (!fs || typeof fs.resolve !== 'function' || typeof fs.writeText !== 'function') {
    throw new Error('当前 profile 没有可写的 fs 服务')
  }
  const cwd = sessionCwd(exec)
  const target = await fs.resolve(filePath, { cwd, signal: exec.signal })
  const policy = ctx.get('sandboxPolicy')?.resolve({ session: exec.agent?.session })
  await fs.writeText(target, content, undefined, exec.signal, policy)
}

function readinessLabel(state) {
  const dims = state?.dimensions
  if (dims === undefined) return 'unknown'
  const values = ['structure', 'language', 'players', 'decision', 'dialogue']
    .map(k => Number(dims[k] ?? 0))
  const avg = values.reduce((a, b) => a + b, 0) / values.length
  return `${avg.toFixed(1)} (min ${Math.min(...values)})`
}

export function apply(ctx, config = {}) {
  const settings = { root: 'ramp', workspaceRoot: '', ...config }
  const workspaceRoot = resolve(settings.workspaceRoot || process.env.FDE_RAMP_WORKSPACE || resolve(homedir(), 'Documents', 'GitHub'))

  ctx.effect(function* registerRampTools() {
    yield ctx.tools.register(defineTool({
      name: 'ramp_status',
      description: '读取 fde-ramp 工作区状态：是否存在、来源/活动/术语计数、五维自检分数。只读，不修改任何文件。',
      parameters: {
        root: { type: 'string', description: 'ramp 工作区路径；默认取配置 root（相对会话工作区）' },
      },
      output: {
        schema: {
          type: 'object',
          properties: {
            root: { type: 'string', required: true },
            initialized: { type: 'boolean', required: true },
            sources: { type: 'number', required: true },
            activities: { type: 'number', required: true },
            readiness: { type: 'string', required: true },
            note: { type: 'string', required: true },
          },
          additionalProperties: false,
        },
        render: (_args, value) => [{
          type: 'text',
          text: value.initialized
            ? `ramp: ${value.root}\nsources: ${value.sources}  activities: ${value.activities}\nreadiness: ${value.readiness}\n${value.note}`
            : `ramp 未初始化: ${value.root}\n${value.note}`,
        }],
      },
      async execute(args, exec) {
        const cwd = sessionCwd(exec)
        const root = resolve(cwd, args.root || settings.root)
        const state = await readJson(resolve(root, 'state.json'))
        if (state === undefined) {
          return {
            root,
            initialized: false,
            sources: 0,
            activities: 0,
            readiness: 'unknown',
            note: '没有 state.json；先运行 scripts/init_ramp.py 生成工作区。',
          }
        }
        const sources = await countLines(resolve(root, 'sources.jsonl'))
        const activities = Number(state?.counts?.activities ?? 0)
        return {
          root,
          initialized: true,
          sources,
          activities,
          readiness: readinessLabel(state),
          note: '只读检查；完整校验请运行 scripts/validate_artifacts.py --strict 与 scripts/readiness.py --check。',
        }
      },
    }))

    yield ctx.tools.register(defineTool({
      name: 'ramp_chain',
      description: '读取 ramp/chain.md，统计玩家表与关系表行数。只读，不修改文件。',
      parameters: {
        root: { type: 'string', description: 'ramp 工作区路径；默认取配置 root' },
      },
      output: {
        schema: {
          type: 'object',
          properties: {
            root: { type: 'string', required: true },
            initialized: { type: 'boolean', required: true },
            players: { type: 'number', required: true },
            relations: { type: 'number', required: true },
            note: { type: 'string', required: true },
          },
          additionalProperties: false,
        },
        render: (_args, value) => [{
          type: 'text',
          text: value.initialized
            ? `chain: ${value.root}\nplayers: ${value.players}  relations: ${value.relations}\n${value.note}`
            : `chain.md 不存在: ${value.root}`,
        }],
      },
      async execute(args, exec) {
        const cwd = sessionCwd(exec)
        const root = resolve(cwd, args.root || settings.root)
        const text = await readText(resolve(root, 'chain.md'))
        if (text === undefined) {
          return { root, initialized: false, players: 0, relations: 0, note: '没有 chain.md' }
        }
        const stats = chainStats(text)
        return {
          root,
          initialized: true,
          players: stats.players,
          relations: stats.relations,
          note: '口径：玩家表 = 表头含「玩家+现状」的行；关系表 = 表头含 from/关系类型/to。',
        }
      },
    }))

    yield ctx.tools.register(defineTool({
      name: 'ramp_activities',
      description: '读取 ramp/activities.md，统计活动行数、列数、含 ❓ 的行数。只读，不修改文件。',
      parameters: {
        root: { type: 'string', description: 'ramp 工作区路径；默认取配置 root' },
      },
      output: {
        schema: {
          type: 'object',
          properties: {
            root: { type: 'string', required: true },
            initialized: { type: 'boolean', required: true },
            rows: { type: 'number', required: true },
            columns: { type: 'number', required: true },
            uncertain: { type: 'number', required: true },
            note: { type: 'string', required: true },
          },
          additionalProperties: false,
        },
        render: (_args, value) => [{
          type: 'text',
          text: value.initialized
            ? `activities: ${value.root}\nrows: ${value.rows}  columns: ${value.columns}  uncertain: ${value.uncertain}\n${value.note}`
            : `activities.md 不存在: ${value.root}`,
        }],
      },
      async execute(args, exec) {
        const cwd = sessionCwd(exec)
        const root = resolve(cwd, args.root || settings.root)
        let text = await readText(resolve(root, 'activities.md'))
        if (text === undefined) text = await readText(resolve(root, 'business.md'))
        if (text === undefined) {
          return { root, initialized: false, rows: 0, columns: 0, uncertain: 0, note: '没有 activities.md / business.md' }
        }
        const stats = activityStats(text)
        return {
          root,
          initialized: true,
          rows: stats.rows,
          columns: stats.columns,
          uncertain: stats.uncertain,
          note: '口径：表头含「业务域+流程+环节」的首张表；uncertain = 任一单元格含 ❓ 的行。',
        }
      },
    }))

    yield ctx.tools.register(defineTool({
      name: 'ramp_metrics',
      description: '读取 ramp/process-metrics.md，按四个数字（耗时/日频次/出错率/单次代价）+ 人力单价计算每天人力成本、风险成本、改进上限。只读，不修改文件。',
      parameters: {
        root: { type: 'string', description: 'ramp 工作区路径；默认取配置 root' },
        days: { type: 'number', description: '年化工作日，默认 250' },
      },
      output: {
        schema: {
          type: 'object',
          properties: {
            root: { type: 'string', required: true },
            initialized: { type: 'boolean', required: true },
            rows: { type: 'number', required: true },
            computed: { type: 'number', required: true },
            incomplete: { type: 'number', required: true },
            laborPerDay: { type: 'number', required: true },
            riskPerDay: { type: 'number', required: true },
            ceilingPerDay: { type: 'number', required: true },
            ceilingPerYear: { type: 'number', required: true },
            note: { type: 'string', required: true },
          },
          additionalProperties: false,
        },
        render: (_args, value) => [{
          type: 'text',
          text: value.initialized
            ? `metrics: ${value.root}\nrows: ${value.rows}  computed: ${value.computed}  incomplete: ${value.incomplete}\n`
              + `labor/day: ${value.laborPerDay}  risk/day: ${value.riskPerDay}\n`
              + `ceiling/day: ${value.ceilingPerDay}  ceiling/year: ${value.ceilingPerYear}\n${value.note}`
            : `process-metrics.md 不存在: ${value.root}`,
        }],
      },
      async execute(args, exec) {
        const cwd = sessionCwd(exec)
        const root = resolve(cwd, args.root || settings.root)
        const text = await readText(resolve(root, 'process-metrics.md'))
        if (text === undefined) {
          return { root, initialized: false, rows: 0, computed: 0, incomplete: 0, laborPerDay: 0, riskPerDay: 0, ceilingPerDay: 0, ceilingPerYear: 0, note: '没有 process-metrics.md；先按模板填四个数字。' }
        }
        const days = Number.isFinite(args.days) && args.days > 0 ? args.days : 250
        const stats = metricsStats(text, days)
        const { top, ...rest } = stats
        return { root, initialized: true, ...rest, note: stats.incomplete > 0 ? `有 ${stats.incomplete} 行数字不全，未计入合计；补齐后再算。` : '全部行已计算。' }
      },
    }))

    yield ctx.tools.register(defineTool({
      name: 'ramp_opportunities',
      description: '读取 ramp/opportunities.md，读六个信号命中数、四维打分、红灯，并按「第一象限最靠右」给出第一项目建议。只读，不修改文件。',
      parameters: {
        root: { type: 'string', description: 'ramp 工作区路径；默认取配置 root' },
      },
      output: {
        schema: {
          type: 'object',
          properties: {
            root: { type: 'string', required: true },
            initialized: { type: 'boolean', required: true },
            count: { type: 'number', required: true },
            scored: { type: 'number', required: true },
            red: { type: 'number', required: true },
            firstProject: { type: 'string', required: true },
            note: { type: 'string', required: true },
          },
          additionalProperties: false,
        },
        render: (_args, value) => [{
          type: 'text',
          text: value.initialized
            ? `opportunities: ${value.root}\ncount: ${value.count}  scored: ${value.scored}  red: ${value.red}\nfirst project: ${value.firstProject || '(无)'}\n${value.note}`
            : `opportunities.md 不存在: ${value.root}`,
        }],
      },
      async execute(args, exec) {
        const cwd = sessionCwd(exec)
        const root = resolve(cwd, args.root || settings.root)
        const text = await readText(resolve(root, 'opportunities.md'))
        if (text === undefined) {
          return { root, initialized: false, count: 0, scored: 0, red: 0, firstProject: '', note: '没有 opportunities.md；先按模板填机会与四维打分。' }
        }
        const stats = opportunityStats(text)
        const { items, ...rest } = stats
        return { root, initialized: true, ...rest }
      },
    }))

    yield ctx.tools.register(defineTool({
      name: 'ramp_metrics_update',
      description: '更新 process-metrics.md 中一个环节的四个数字（耗时/日频次/出错率/单次代价）+ 人力单价，并重算每天人力成本、风险成本、改进上限。会写入文件。',
      parameters: {
        root: { type: 'string', description: 'ramp 工作区路径；默认取配置 root' },
        id: { type: 'string', description: '环节ID，如 A01；与 activity 二选一' },
        activity: { type: 'string', description: '活动名（包含匹配）；与 id 二选一' },
        minutes: { type: 'number', description: '耗时（分钟/次）' },
        frequency: { type: 'number', description: '日频次（次/天）' },
        errorRate: { type: 'number', description: '出错率（百分数，如 3 表示 3%）' },
        costPerError: { type: 'number', description: '单次代价（元/次）' },
        hourlyRate: { type: 'number', description: '人力单价（元/小时）' },
        who: { type: 'string', description: '谁做/职级（可选）' },
      },
      output: {
        schema: {
          type: 'object',
          properties: {
            root: { type: 'string', required: true },
            id: { type: 'string', required: true },
            activity: { type: 'string', required: true },
            line: { type: 'number', required: true },
            laborPerDay: { type: 'number', required: true },
            riskPerDay: { type: 'number', required: true },
            ceilingPerDay: { type: 'number', required: true },
            note: { type: 'string', required: true },
          },
          additionalProperties: false,
        },
        render: (_args, value) => [{
          type: 'text',
          text: `updated ${value.id || value.activity} (line ${value.line})\n`
            + `labor/day: ${value.laborPerDay}  risk/day: ${value.riskPerDay}  ceiling/day: ${value.ceilingPerDay}\n${value.note}`,
        }],
      },
      async execute(args, exec) {
        const cwd = sessionCwd(exec)
        const root = resolve(cwd, args.root || settings.root)
        const path = resolve(root, 'process-metrics.md')
        const text = await readText(path)
        if (text === undefined) throw new Error(`没有 process-metrics.md: ${path}`)
        if (args.minutes === undefined && args.frequency === undefined && args.errorRate === undefined
          && args.costPerError === undefined && args.hourlyRate === undefined && args.who === undefined) {
          throw new Error('至少提供一个要更新的字段')
        }
        const result = updateMetrics(text, args)
        await writeWithPolicy(ctx, exec, path, result.markdown)
        const computed = result.computed
        return {
          root,
          id: result.id,
          activity: result.activity,
          line: result.line,
          laborPerDay: computed ? Math.round(computed.labor * 100) / 100 : 0,
          riskPerDay: computed ? Math.round(computed.risk * 100) / 100 : 0,
          ceilingPerDay: computed ? Math.round(computed.ceiling * 100) / 100 : 0,
          note: computed ? '已重算并写回三个成本列。' : '四个数字不全，已写回输入，但未重算成本。',
        }
      },
    }))

    yield ctx.tools.register(defineTool({
      name: 'ramp_activities_update',
      description: '编辑 activities.md 中某一行活动表的一个单元格（按活动名匹配行、按列名包含匹配列），并写入文件。',
      parameters: {
        root: { type: 'string', description: 'ramp 工作区路径；默认取配置 root' },
        activity: { type: 'string', required: true, description: '活动名（包含匹配）' },
        column: { type: 'string', required: true, description: '列名（包含匹配），如「做什么」「谁做」「信心」' },
        value: { type: 'string', required: true, description: '新值' },
      },
      output: {
        schema: {
          type: 'object',
          properties: {
            root: { type: 'string', required: true },
            activity: { type: 'string', required: true },
            column: { type: 'string', required: true },
            oldValue: { type: 'string', required: true },
            newValue: { type: 'string', required: true },
            note: { type: 'string', required: true },
          },
          additionalProperties: false,
        },
        render: (_args, value) => [{
          type: 'text',
          text: `updated ${value.activity} / ${value.column}\n${value.oldValue || '(空)'} -> ${value.newValue}`,
        }],
      },
      async execute(args, exec) {
        const cwd = sessionCwd(exec)
        const root = resolve(cwd, args.root || settings.root)
        let path = resolve(root, 'activities.md')
        let text = await readText(path)
        if (text === undefined) { path = resolve(root, 'business.md'); text = await readText(path) }
        if (text === undefined) throw new Error(`没有 activities.md / business.md: ${path}`)
        const result = updateActivities(text, args)
        await writeWithPolicy(ctx, exec, path, result.markdown)
        return {
          root,
          activity: result.activity,
          column: result.column,
          oldValue: result.oldValue,
          newValue: result.newValue,
          note: '已写入 activities.md（只改一个单元格）。',
        }
      },
    }))

    yield ctx.tools.register(defineTool({
      name: 'ramp_metrics_batch',
      description: '批量更新 process-metrics.md 的多个环节数字，重算成本列；写前自动备份，支持 dryRun 预览 diff。会写入文件（dryRun 除外）。',
      parameters: {
        root: { type: 'string', description: 'ramp 工作区路径；默认取配置 root' },
        dryRun: { type: 'boolean', description: '只预览 diff，不写文件、不备份' },
        updates: {
          type: 'array',
          required: true,
          description: '更新列表；每项与 ramp_metrics_update 参数相同',
          items: {
            type: 'object',
            properties: {
              id: { type: 'string' }, activity: { type: 'string' },
              minutes: { type: 'number' }, frequency: { type: 'number' },
              errorRate: { type: 'number' }, costPerError: { type: 'number' },
              hourlyRate: { type: 'number' }, who: { type: 'string' },
            },
            additionalProperties: false,
          },
        },
      },
      output: {
        schema: {
          type: 'object',
          properties: {
            root: { type: 'string', required: true },
            count: { type: 'number', required: true },
            dryRun: { type: 'boolean', required: true },
            backup: { type: 'string', required: true },
            diff: { type: 'string', required: true },
            note: { type: 'string', required: true },
          },
          additionalProperties: false,
        },
        render: (_args, value) => [{
          type: 'text',
          text: `${value.dryRun ? 'preview' : 'updated'} ${value.count} rows in ${value.root}\n`
            + (value.backup ? `backup: ${value.backup}\n` : '')
            + `diff:\n${value.diff}`,
        }],
      },
      async execute(args, exec) {
        const cwd = sessionCwd(exec)
        const root = resolve(cwd, args.root || settings.root)
        const updates = Array.isArray(args.updates) ? args.updates : []
        if (updates.length === 0) throw new Error('updates 不能为空')
        const path = resolve(root, 'process-metrics.md')
        const text = await readText(path)
        if (text === undefined) throw new Error(`没有 process-metrics.md: ${path}`)
        const result = updateMetricsBatch(text, updates)
        const diff = diffLines(text, result.markdown)
        const dryRun = args.dryRun === true
        let backup = ''
        if (!dryRun) {
          backup = await writeBackup(ctx, exec, root, 'process-metrics.md', text)
          await writeWithPolicy(ctx, exec, path, result.markdown)
        }
        return {
          root,
          count: result.results.length,
          dryRun,
          backup,
          diff,
          note: dryRun ? '预览模式：没有写文件。' : '已写文件；备份是隐藏文件，可手动恢复。',
        }
      },
    }))

    yield ctx.tools.register(defineTool({
      name: 'ramp_activities_batch',
      description: '批量编辑 activities.md 的多个单元格；写前自动备份，支持 dryRun 预览 diff。会写入文件（dryRun 除外）。',
      parameters: {
        root: { type: 'string', description: 'ramp 工作区路径；默认取配置 root' },
        dryRun: { type: 'boolean', description: '只预览 diff，不写文件、不备份' },
        updates: {
          type: 'array',
          required: true,
          description: '更新列表；每项是 {activity, column, value}',
          items: {
            type: 'object',
            properties: {
              activity: { type: 'string' }, column: { type: 'string' }, value: { type: 'string' },
            },
            additionalProperties: false,
          },
        },
      },
      output: {
        schema: {
          type: 'object',
          properties: {
            root: { type: 'string', required: true },
            count: { type: 'number', required: true },
            dryRun: { type: 'boolean', required: true },
            backup: { type: 'string', required: true },
            diff: { type: 'string', required: true },
            note: { type: 'string', required: true },
          },
          additionalProperties: false,
        },
        render: (_args, value) => [{
          type: 'text',
          text: `${value.dryRun ? 'preview' : 'updated'} ${value.count} cells in ${value.root}\n`
            + (value.backup ? `backup: ${value.backup}\n` : '')
            + `diff:\n${value.diff}`,
        }],
      },
      async execute(args, exec) {
        const cwd = sessionCwd(exec)
        const root = resolve(cwd, args.root || settings.root)
        const updates = Array.isArray(args.updates) ? args.updates : []
        if (updates.length === 0) throw new Error('updates 不能为空')
        let path = resolve(root, 'activities.md')
        let text = await readText(path)
        if (text === undefined) { path = resolve(root, 'business.md'); text = await readText(path) }
        if (text === undefined) throw new Error(`没有 activities.md / business.md: ${path}`)
        const result = updateActivitiesBatch(text, updates)
        const diff = diffLines(text, result.markdown)
        const dryRun = args.dryRun === true
        let backup = ''
        if (!dryRun) {
          backup = await writeBackup(ctx, exec, root, 'activities.md', text)
          await writeWithPolicy(ctx, exec, path, result.markdown)
        }
        return {
          root,
          count: result.results.length,
          dryRun,
          backup,
          diff,
          note: dryRun ? '预览模式：没有写文件。' : '已写文件；备份是隐藏文件，可手动恢复。',
        }
      },
    }))
  })

}
