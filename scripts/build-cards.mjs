#!/usr/bin/env node
/**
 * 从 notes/ 下的 Markdown 抽取记忆卡片
 *
 * 语法：一行以 - 或 * 开头，用 :: 分隔问题和答案
 *     - temperature 越高输出越随机::对
 *
 * 输出：public/cards.json（构建时生成，不进 git）
 */

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const SRC_DIR = path.join(ROOT, 'notes')
const OUT_DIR = path.join(ROOT, 'public')
const OUT_FILE = path.join(OUT_DIR, 'cards.json')

const CARD_RE = /^\s*[-*]\s+(.+?)::(.+?)\s*$/

function walk(dir) {
  if (!fs.existsSync(dir)) return []
  const out = []
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith('.')) continue
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) out.push(...walk(full))
    else if (entry.name.endsWith('.md')) out.push(full)
  }
  return out
}

const cards = []

for (const file of walk(SRC_DIR)) {
  const rel = path.relative(ROOT, file).split(path.sep).join('/')
  const lines = fs.readFileSync(file, 'utf8').split(/\r?\n/)
  let inCode = false
  lines.forEach((line, i) => {
    // 跳过围栏代码块里的内容（含 ``` 和 ~~~）
    if (/^\s*(```|~~~)/.test(line)) {
      inCode = !inCode
      return
    }
    if (inCode) return
    const m = line.match(CARD_RE)
    if (!m) return
    cards.push({
      id: `${rel}#${i + 1}`,
      q: m[1].trim(),
      a: m[2].trim(),
      source: rel,
    })
  })
}

fs.mkdirSync(OUT_DIR, { recursive: true })
fs.writeFileSync(OUT_FILE, JSON.stringify(cards, null, 2), 'utf8')

console.log(`cards: ${cards.length} 张 → ${path.relative(ROOT, OUT_FILE)}`)
