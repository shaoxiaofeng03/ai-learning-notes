import { defineConfig, type DefaultTheme } from 'vitepress'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const REPO = path.resolve(HERE, '..')

/** 扫描目录生成侧边栏，新增 .md 自动出现，不用改配置 */
function collect(dir: string, prefix: string): DefaultTheme.SidebarItem[] {
  const items: DefaultTheme.SidebarItem[] = []
  if (!fs.existsSync(dir)) return items

  const entries = fs
    .readdirSync(dir, { withFileTypes: true })
    .sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'))

  for (const entry of entries) {
    if (entry.name.startsWith('.')) continue
    // README.md 是目录说明，不进导航
    if (entry.isFile() && entry.name === 'README.md') continue

    if (entry.isDirectory()) {
      const children = collect(path.join(dir, entry.name), `${prefix}/${entry.name}`)
      if (children.length > 0) {
        items.push({ text: entry.name, collapsed: false, items: children })
      }
    } else if (entry.name.endsWith('.md')) {
      const name = entry.name.replace(/\.md$/, '')
      items.push({ text: name, link: `${prefix}/${name}` })
    }
  }
  return items
}

const noteGroups = collect(path.join(REPO, 'notes'), '/notes')

export default defineConfig({
  lang: 'zh-CN',
  title: 'AI 学习笔记',
  description: 'AI 全栈工程师学习笔记 · 记忆卡片',
  cleanUrls: true,
  lastUpdated: true,

  // 只把笔记和首页当作站点内容，其余目录全部排除
  srcExclude: [
    'bak/**',
    'projects/**',
    'scripts/**',
    'node_modules/**',
    '.opencode/**',
    '.vitepress/**',
    'README.md',
  ],

  // 笔记里常有指向未收录文件的链接，首次部署先不阻断构建
  ignoreDeadLinks: true,

  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: '笔记', link: '/notes/W1-大模型核心概念速记' },
      { text: '路线图', link: '/AI全栈工程师-学习路线图' },
      { text: '记忆卡片', link: '/cards' },
    ],

    sidebar: [
      { text: '开始', items: [{ text: '首页', link: '/' }] },
      ...(noteGroups.length ? [{ text: '笔记', items: noteGroups }] : []),
      {
        text: '复习',
        items: [{ text: '记忆卡片', link: '/cards' }],
      },
    ],

    search: { provider: 'local' },

    outline: { level: [2, 3], label: '本页目录' },

    docFooter: { prev: '上一篇', next: '下一篇' },

    returnToTopLabel: '回到顶部',
    sidebarMenuLabel: '目录',
    darkModeSwitchLabel: '主题',
    lightModeSwitchTitle: '切换到浅色',
    darkModeSwitchTitle: '切换到深色',

    footer: {
      message: '基于 VitePress 构建 · 由 cnb.cool 推送自动部署',
      copyright: 'AI 学习笔记',
    },
  },
})
