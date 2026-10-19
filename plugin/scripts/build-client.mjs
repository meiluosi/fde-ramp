/**
 * Build plugin/client/bundle.js from plugin/client/index.js.
 *
 * Static client bundle protocol: window.__ModuleLoader__.load({ id, factory }).
 * The factory receives require; React is provided as a platform module even
 * though this panel is DOM-only.
 */
import { readFileSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const sourcePath = join(here, '..', 'client', 'index.js')
const bundlePath = join(here, '..', 'client', 'bundle.js')
const pkg = JSON.parse(readFileSync(join(here, '..', 'package.json'), 'utf8'))
const source = readFileSync(sourcePath, 'utf8')

const banner = `/* Generated from client/index.js by scripts/build-client.mjs — do not edit by hand. */
window.__ModuleLoader__.load({
  id: ${JSON.stringify(pkg.name)},
  factory: (require) => {
    var module = { exports: {} }
    var exports = module.exports
    Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" })
    var React = require("react")
`

const footer = `
    return module.exports
  }
})
`

const indent = (code) => code
  .split('\n')
  .map((line) => (line.length === 0 ? line : '    ' + line))
  .join('\n')

writeFileSync(bundlePath, banner + indent(source) + footer, 'utf8')
console.log(`built ${bundlePath} (${source.length} source bytes)`)
