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
import { resolve } from 'node:path'
import { defineTool } from '@deepseek-ai/dsh-tools'
import z from '@deepseek-ai/schemastery'
import { activityStats, chainStats } from './parse.js'

export const name = 'dsh-fde-ramp'
export const inject = ['tools']

export const Config = z.object({
  /** Default ramp root relative to the session workspace. */
  root: z.string().default('ramp'),
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

function readinessLabel(state) {
  const dims = state?.dimensions
  if (dims === undefined) return 'unknown'
  const values = ['structure', 'language', 'players', 'decision', 'dialogue']
    .map(k => Number(dims[k] ?? 0))
  const avg = values.reduce((a, b) => a + b, 0) / values.length
  return `${avg.toFixed(1)} (min ${Math.min(...values)})`
}

export function apply(ctx, config = {}) {
  const settings = { root: 'ramp', ...config }

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
        const text = await readText(resolve(root, 'activities.md'))
        if (text === undefined) {
          return { root, initialized: false, rows: 0, columns: 0, uncertain: 0, note: '没有 activities.md' }
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
  })
}
