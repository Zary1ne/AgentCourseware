<template>
  <section id="stats" class="stats">
    <div class="stats__inner">
      <div class="stats__header">
        <span class="section-label">数据仪表盘</span>
        <h2 class="stats__title">系统实时运行状态</h2>
        <p class="stats__subtitle">知识库概览与系统健康度一目了然</p>
      </div>

      <div class="stats__grid">
        <div v-for="(card, i) in cards" :key="card.label" :class="['stat-card', 'card-spotlight']" v-scroll-in="{ delay: i * 80 }" @mousemove="onCardMove($event, i)" ref="cardRefs">
          <div class="stat-card__top">
            <span class="stat-card__label">{{ card.label }}</span>
            <span v-if="card.status" class="stat-card__status">
              <span class="stat-card__dot" />{{ card.status }}
            </span>
          </div>
          <span class="stat-card__value">{{ card.value }}</span>
          <span class="stat-card__unit">{{ card.unit }}</span>
          <div class="stat-card__trend">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M2 10l4-5 3 3 3-6" stroke="var(--accent)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>较上月增长 12%</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted, getCurrentInstance } from 'vue'
import { getKnowledgeDocuments, getAdminStats } from '../api'

const docCount = ref(0)
const docTypes = ref(0)
const activeTasks = ref(0)
const displayDocCount = ref(0)
const displayDocTypes = ref(0)
const displayActiveTasks = ref(0)
const cardRefs = ref([])

function onCardMove(e, i) {
  const card = cardRefs.value?.[i]
  if (!card) return
  const rect = card.getBoundingClientRect()
  card.style.setProperty('--mx', `${e.clientX - rect.left}px`)
  card.style.setProperty('--my', `${e.clientY - rect.top}px`)
}

function animateNumber(from, target, duration, callback) {
  const start = performance.now()
  function frame(now) {
    const elapsed = now - start
    const progress = Math.min(elapsed / duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)
    callback(Math.round(from + (target - from) * eased))
    if (progress < 1) requestAnimationFrame(frame)
  }
  requestAnimationFrame(frame)
}

let numObserver
let animated = false
const rootEl = getCurrentInstance()?.proxy?.$el

onMounted(async () => {
  try {
    const [docsRes, adminRes] = await Promise.allSettled([getKnowledgeDocuments(), getAdminStats()])
    const docs = docsRes.status === 'fulfilled' ? docsRes.value.data : { documents:[], total:0 }
    const admin = adminRes.status === 'fulfilled' ? adminRes.value.data : {}
    docCount.value = docs.total ?? 0
    docTypes.value = docs.documents?.length ?? 0
    activeTasks.value = admin.active_sessions ?? admin.task_count ?? 0
  } catch {}

  // Trigger number animation when section enters viewport
  numObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !animated) {
        animated = true
        animateNumber(0, docCount.value, 1500, (v) => displayDocCount.value = v)
        animateNumber(0, docTypes.value, 1500, (v) => displayDocTypes.value = v)
        animateNumber(0, activeTasks.value, 1500, (v) => displayActiveTasks.value = v)
      }
    })
  }, { threshold: 0.3 })
  if (rootEl) numObserver.observe(rootEl)
})

onUnmounted(() => { if (numObserver) numObserver.disconnect() })

const cards = [
  { key:'docs', label:'知识文档', value:displayDocCount, unit:'份已索引' },
  { key:'types', label:'文档类型', value:displayDocTypes, unit:'种来源格式' },
  { key:'tasks', label:'活跃任务', value:displayActiveTasks, unit:'个进行中' },
  { key:'status', label:'系统状态', value:'正常', unit:'', status:'运行中' },
]
</script>

<style scoped>
.stats { padding: 80px 40px; background: var(--bg-surface); }
.stats__inner { max-width: var(--max-width); margin: 0 auto; }

.stats__header { text-align: center; margin-bottom: 48px; }
.stats__title { font-size: clamp(28px, 3.5vw, 40px); font-weight: 700; letter-spacing: -0.015em; color: var(--text-primary); margin-bottom: 10px; }
.stats__subtitle { font-size: 16px; color: var(--text-secondary); }

.stats__grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }

.stat-card {
  background: var(--bg-card); border: 1px solid var(--border-light);
  border-radius: var(--r-lg); padding: 28px;
  display: flex; flex-direction: column; gap: 12px;
  transition: all var(--t-base) var(--ease-out);
}
.stat-card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-lg); transform: translateY(-2px);
}

.stat-card__top { display: flex; align-items: center; justify-content: space-between; }
.stat-card__label { font-size: 13px; font-weight: 600; color: var(--text-secondary); letter-spacing: -0.005em; }
.stat-card__status { display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 600; color: #34D399; }
.stat-card__dot { width: 6px; height: 6px; border-radius: 50%; background: #34D399; }

.stat-card__value { font-size: 44px; font-weight: 800; letter-spacing: -0.035em; color: var(--text-primary); line-height: 1; }
.stat-card__unit { font-size: 13px; color: var(--text-tertiary); font-weight: 500; margin-top: -8px; }

.stat-card__trend { display: flex; align-items: center; gap: 6px; margin-top: 4px; }
.stat-card__trend span { font-size: 12px; color: var(--text-tertiary); }

@media (max-width: 1000px) { .stats__grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 560px) { .stats__grid { grid-template-columns: 1fr; } }
</style>
