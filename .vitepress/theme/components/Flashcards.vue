<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { withBase } from 'vitepress'

interface Card {
  id: string
  q: string
  a: string
  source: string
}

interface CardState {
  ef: number // 难度因子
  interval: number // 间隔（天）
  due: number // 下次到期时间戳
  reps: number // 连续答对次数
}

const STORAGE_KEY = 'ai-notes:cards:v1'

const cards = ref<Card[]>([])
const states = ref<Record<string, CardState>>({})
const session = ref<Card[]>([])
const idx = ref(0)
const flipped = ref(false)
const loading = ref(true)
const error = ref('')
const mode = ref<'due' | 'all'>('due')

const DAY = 86400_000

function loadStates() {
  try {
    states.value = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')
  } catch {
    states.value = {}
  }
}

function saveStates() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(states.value))
  } catch {
    /* 隐私模式下写入失败，忽略 */
  }
}

function stateOf(id: string): CardState {
  return states.value[id] ?? { ef: 2.5, interval: 0, due: 0, reps: 0 }
}

const dueCount = computed(() => cards.value.filter((c) => stateOf(c.id).due <= Date.now()).length)
const current = computed(() => session.value[idx.value])
const done = computed(() => idx.value >= session.value.length)

function start(next: 'due' | 'all' = mode.value) {
  mode.value = next
  const now = Date.now()
  session.value = next === 'all' ? [...cards.value] : cards.value.filter((c) => stateOf(c.id).due <= now)
  idx.value = 0
  flipped.value = false
}

/** 0 重来 / 1 困难 / 2 良好 / 3 简单 */
function grade(g: 0 | 1 | 2 | 3) {
  const card = current.value
  if (!card) return

  const s: CardState = { ...stateOf(card.id) }

  if (g === 0) {
    s.reps = 0
    s.interval = 0
    s.due = Date.now() + 10 * 60_000 // 10 分钟后再来
  } else {
    s.reps += 1
    if (s.reps === 1) s.interval = 1
    else if (s.reps === 2) s.interval = 3
    else s.interval = Math.max(1, Math.round(s.interval * s.ef))

    if (g === 1) s.interval = Math.max(1, Math.round(s.interval * 0.6))
    if (g === 3) s.interval = Math.round(s.interval * 1.3)

    s.due = Date.now() + s.interval * DAY
  }

  const delta = g === 0 ? -0.2 : g === 1 ? -0.15 : g === 2 ? 0 : 0.15
  s.ef = Math.min(3.0, Math.max(1.3, s.ef + delta))

  states.value[card.id] = s
  saveStates()

  flipped.value = false
  idx.value += 1
}

function nextLabel(g: 0 | 1 | 2 | 3): string {
  const card = current.value
  if (!card) return ''
  const s = stateOf(card.id)
  if (g === 0) return '10 分钟'
  const reps = s.reps + 1
  let interval: number
  if (reps === 1) interval = 1
  else if (reps === 2) interval = 3
  else interval = Math.max(1, Math.round(s.interval * s.ef))
  if (g === 1) interval = Math.max(1, Math.round(interval * 0.6))
  if (g === 3) interval = Math.round(interval * 1.3)
  return interval >= 30 ? `${Math.round(interval / 30)} 个月` : `${interval} 天`
}

onMounted(async () => {
  loadStates()
  try {
    const res = await fetch(withBase('/cards.json'))
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    cards.value = await res.json()
    start('due')
  } catch (e) {
    error.value = `加载卡片失败：${(e as Error).message}`
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="fc">
    <div v-if="loading" class="fc-hint">加载中…</div>

    <div v-else-if="error" class="fc-hint fc-err">{{ error }}</div>

    <div v-else-if="cards.length === 0" class="fc-hint">
      <p>还没有卡片。</p>
      <p>在任意 <code>notes/</code> 下的 Markdown 里写一行：</p>
      <pre><code>- 问题::答案</code></pre>
      <p>重新推送后就会出现在这里。</p>
    </div>

    <template v-else>
      <div class="fc-bar">
        <div class="fc-tabs">
          <button :class="{ on: mode === 'due' }" @click="start('due')">
            今日待复习 <span class="fc-badge">{{ dueCount }}</span>
          </button>
          <button :class="{ on: mode === 'all' }" @click="start('all')">
            全部 <span class="fc-badge">{{ cards.length }}</span>
          </button>
        </div>
        <div v-if="!done" class="fc-progress">{{ idx + 1 }} / {{ session.length }}</div>
      </div>

      <div v-if="done" class="fc-hint">
        <p v-if="mode === 'due'">今天的卡片都复习完了 🎉</p>
        <p v-else>这一轮结束了 🎉</p>
        <p v-if="mode === 'all' && dueCount > 0">
          还有 {{ dueCount }} 张今天到期，<a href="#" @click.prevent="start('due')">去做今日复习</a>
        </p>
      </div>

      <div v-else-if="current" class="fc-card" @click="flipped = !flipped">
        <div class="fc-q">{{ current.q }}</div>

        <div v-if="flipped" class="fc-a">
          <div class="fc-divider"></div>
          <div>{{ current.a }}</div>
        </div>
        <div v-else class="fc-tap">点击卡片查看答案</div>

        <div class="fc-src">{{ current.source }}</div>
      </div>

      <div v-if="!done && current" class="fc-actions">
        <template v-if="flipped">
          <button class="fc-btn g0" @click="grade(0)">重来<span>{{ nextLabel(0) }}</span></button>
          <button class="fc-btn g1" @click="grade(1)">困难<span>{{ nextLabel(1) }}</span></button>
          <button class="fc-btn g2" @click="grade(2)">良好<span>{{ nextLabel(2) }}</span></button>
          <button class="fc-btn g3" @click="grade(3)">简单<span>{{ nextLabel(3) }}</span></button>
        </template>
        <button v-else class="fc-btn fc-flip" @click="flipped = true">显示答案</button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.fc {
  max-width: 720px;
  margin: 0 auto;
}

.fc-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.fc-tabs {
  display: flex;
  gap: 8px;
}

.fc-tabs button {
  padding: 6px 12px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-2);
  font-size: 14px;
  cursor: pointer;
}

.fc-tabs button.on {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
  background: var(--vp-c-brand-soft);
}

.fc-badge {
  font-size: 12px;
  opacity: 0.8;
}

.fc-progress {
  font-size: 14px;
  color: var(--vp-c-text-3);
}

.fc-card {
  min-height: 220px;
  padding: 28px 24px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 14px;
  background: var(--vp-c-bg-soft);
  cursor: pointer;
  user-select: none;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.fc-q {
  font-size: 20px;
  font-weight: 600;
  line-height: 1.6;
  text-align: center;
}

.fc-a {
  margin-top: 20px;
  font-size: 17px;
  line-height: 1.7;
  text-align: center;
  color: var(--vp-c-text-1);
}

.fc-divider {
  height: 1px;
  background: var(--vp-c-divider);
  margin-bottom: 20px;
}

.fc-tap {
  margin-top: 24px;
  text-align: center;
  font-size: 13px;
  color: var(--vp-c-text-3);
}

.fc-src {
  margin-top: 24px;
  text-align: center;
  font-size: 12px;
  color: var(--vp-c-text-3);
  word-break: break-all;
}

.fc-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-top: 16px;
}

.fc-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 12px 8px;
  border-radius: 10px;
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  font-size: 15px;
  cursor: pointer;
  transition: border-color 0.15s;
}

.fc-btn span {
  font-size: 11px;
  color: var(--vp-c-text-3);
}

.fc-btn:hover {
  border-color: var(--vp-c-brand-1);
}

.fc-flip {
  grid-column: 1 / -1;
  font-weight: 600;
  background: var(--vp-c-brand-soft);
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
}

.g0 { border-color: #e5484d55; }
.g1 { border-color: #f5a52455; }
.g2 { border-color: #30a46c55; }
.g3 { border-color: #0090ff55; }

.fc-hint {
  padding: 32px 8px;
  text-align: center;
  color: var(--vp-c-text-2);
  line-height: 1.9;
}

.fc-err {
  color: #e5484d;
}

@media (max-width: 640px) {
  .fc-card {
    min-height: 180px;
    padding: 20px 16px;
  }
  .fc-q {
    font-size: 18px;
  }
  .fc-a {
    font-size: 16px;
  }
  .fc-actions {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
