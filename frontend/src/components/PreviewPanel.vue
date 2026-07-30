<template>
  <div class="preview-panel">
    <!-- 步骤指示器 -->
    <div class="steps">
      <div v-for="(s, i) in stepItems" :key="i" :class="['step-item', { active: step === i + 1, done: step > i + 1 }]">
        <span>{{ i + 1 }}</span>
        <strong>{{ s }}</strong>
      </div>
    </div>

    <div class="workflow-card">
      <!-- 生成进度遮罩 -->
      <div v-if="showOverlay" class="generate-overlay">
        <div class="generate-card">
          <div class="generate-spinner" />
          <div class="generate-percent">{{ genPercent }}%</div>
          <p class="generate-text">{{ genText }}</p>
          <div class="generate-track"><div class="generate-bar" :style="{ width: genPercent + '%' }" /></div>
        </div>
      </div>

      <!-- ======== Step 1: 选择类型与模板 ======== -->
      <div v-show="step === 1" class="workflow-panel">
        <div class="panel-head">
          <div>
            <p class="panel-head__eyebrow">Step 01</p>
            <h2 class="panel-head__title">请选择课件类型和模板风格</h2>
          </div>
          <span class="panel-head__tag">当前：{{ typeName }} · {{ templateName }}</span>
        </div>

        <div class="choose-layout">
          <div>
            <h3>课件类型</h3>
            <div class="option-grid">
              <button
                v-for="opt in typeOptions" :key="opt.value"
                :class="['option-card', { active: type === opt.value }]"
                @click="type = opt.value; typeName = opt.label"
              >
                <span class="option-emoji">{{ opt.emoji }}</span>
                <strong>{{ opt.label }}</strong>
                <span>{{ opt.desc }}</span>
              </button>
            </div>
          </div>

          <div>
            <h3>模板风格</h3>
            <div class="option-grid template-options">
              <button
                v-for="tpl in templateOptions" :key="tpl.value"
                :class="['option-card', { active: template === tpl.value }]"
                @click="template = tpl.value; templateName = tpl.label"
              >
                <span class="option-emoji">{{ tpl.emoji }}</span>
                <strong>{{ tpl.label }}</strong>
                <span>{{ tpl.desc }}</span>
              </button>
            </div>
          </div>
        </div>

        <div class="actions">
          <button class="primary-btn" @click="goToPreview">下一步：实时预览与在线编辑</button>
        </div>
      </div>

      <!-- ======== Step 2: 实时预览与在线编辑 ======== -->
      <div v-show="step === 2" class="workflow-panel">
        <div class="panel-head">
          <div>
            <p class="panel-head__eyebrow">Step 02</p>
            <h2 class="panel-head__title">实时预览与在线编辑</h2>
          </div>
          <span class="panel-head__tag">{{ typeName }} · {{ templateName }}</span>
        </div>

        <!-- PPT/动画/思维导图 预览布局 -->
        <div v-if="type !== 'Word'" class="preview-layout">
          <!-- 缩略图侧边栏 -->
          <aside class="thumb-list">
            <button
              v-for="(item, index) in slides" :key="index"
              :class="['thumb', { active: index === current }]"
              @click="current = index"
            >
              <span class="thumb-top">
                <span class="thumb-kind" :style="{ background: PAGE_KIND_LABELS[item.kind]?.color || '#2da44e' }">
                  {{ PAGE_KIND_LABELS[item.kind]?.name || '正文' }}
                </span>
                <span class="thumb-no">第 {{ index + 1 }} 页</span>
              </span>
              <strong>{{ item.title }}</strong>
            </button>
          </aside>

          <!-- 幻灯片区域 -->
          <article class="slide-area">
            <div class="slide-toolbar">
              <button class="plain-btn" @click="current = Math.max(0, current - 1)" :disabled="current <= 0">上一页</button>
              <span class="slide-toolbar__info">第 {{ current + 1 }} 页 / 共 {{ slides.length }} 页</span>
              <button class="plain-btn" @click="current = Math.min(slides.length - 1, current + 1)" :disabled="current >= slides.length - 1">下一页</button>
              <button class="plain-btn" @click="zoom = Math.max(0.7, zoom - 0.1)">缩小</button>
              <span class="slide-toolbar__info">{{ Math.round(zoom * 100) }}%</span>
              <button class="plain-btn" @click="zoom = Math.min(1.3, zoom + 0.1)">放大</button>
            </div>

            <div class="slide-frame">
              <div :class="slideCardClass" :style="{ transform: 'scale(' + zoom + ')' }">
                <p class="slide-kicker">{{ typeName }} · 第 {{ current + 1 }} 页</p>
                <span class="slide-kind-badge" :style="{ background: currentKindColor }">{{ currentKindName }}</span>
                <h2 class="slide-title">{{ currentSlide.title }}</h2>
                <div class="slide-body" v-html="slideBodyHtml" />
              </div>
            </div>
          </article>

          <!-- 编辑器 -->
          <aside class="editor">
            <h3>编辑当前页</h3>
            <label>
              <span>页面类型</span>
              <select v-model="currentSlide.kind">
                <option v-for="(info, key) in PAGE_KIND_LABELS" :key="key" :value="key">{{ info.name }}</option>
              </select>
            </label>
            <label>
              <span>页面标题</span>
              <input v-model="currentSlide.title" type="text" />
            </label>
            <label>
              <span>页面内容</span>
              <textarea v-model="currentSlide.body" rows="9" />
            </label>
            <div class="editor-actions">
              <button class="plain-btn" @click="saveCurrentSlide">保存修改</button>
              <button class="plain-btn" @click="addSlide">新增页</button>
              <button class="plain-btn" @click="moveSlide(-1)">上移</button>
              <button class="plain-btn" @click="moveSlide(1)">下移</button>
              <button class="danger-btn" @click="deleteSlide">删除页</button>
            </div>
            <p class="edit-status">{{ editStatus }}</p>
          </aside>
        </div>

        <!-- Word 文档预览布局（独立） -->
        <div v-else class="preview-layout preview-layout--word">
          <!-- Word 文档展示区 -->
          <article class="word-area">
            <div class="slide-toolbar">
              <span class="word-doc-label">Word 文档预览</span>
              <button class="plain-btn" @click="zoom = Math.max(0.7, zoom - 0.1)">缩小</button>
              <span class="slide-toolbar__info">{{ Math.round(zoom * 100) }}%</span>
              <button class="plain-btn" @click="zoom = Math.min(1.3, zoom + 0.1)">放大</button>
            </div>

            <div class="word-frame">
              <div class="word-doc-card" :style="{ transform: 'scale(' + zoom + ')' }">
                <div v-for="(slide, i) in slides" :key="i">
                  <!-- 封面 -->
                  <template v-if="slide.kind === 'cover'">
                    <h2 class="word-doc-cover-title">{{ slide.title }}</h2>
                    <p v-for="(line, j) in slide.body.split('\n').filter(Boolean)" :key="'c'+j" class="word-doc-subtitle">{{ line }}</p>
                    <hr class="word-doc-divider">
                  </template>
                  <!-- 目录 -->
                  <template v-else-if="slide.kind === 'catalog'">
                    <h3 class="word-doc-heading">{{ slide.title }}</h3>
                    <ol class="word-doc-list">
                      <li v-for="(line, j) in slide.body.split('\n').filter(Boolean)" :key="'t'+j">{{ line.replace(/^\d+\.\s*/, '') }}</li>
                    </ol>
                  </template>
                  <!-- 正文 -->
                  <template v-else-if="slide.kind === 'content'">
                    <h3 class="word-doc-heading">{{ slide.title }}</h3>
                    <p v-for="(line, j) in slide.body.split('\n').filter(Boolean)" :key="'b'+j" class="word-doc-para">{{ line }}</p>
                  </template>
                  <!-- 总结 -->
                  <template v-else-if="slide.kind === 'summary'">
                    <h3 class="word-doc-heading">{{ slide.title }}</h3>
                    <div class="word-doc-summary-box">
                      <p v-for="(line, j) in slide.body.split('\n').filter(Boolean)" :key="'s'+j" class="word-doc-para word-doc-para--noindent">{{ line }}</p>
                    </div>
                  </template>
                </div>
              </div>
            </div>
          </article>

          <!-- Word 编辑器 -->
          <aside class="editor">
            <h3>编辑 Word 文档</h3>
            <label>
              <span>文档标题</span>
              <input v-model="wordDocTitle" type="text" />
            </label>
            <label>
              <span>文档内容（每段以【类型】开头）</span>
              <textarea v-model="wordDocBody" rows="18" />
            </label>
            <div class="editor-actions">
              <button class="plain-btn" @click="saveWordDoc">保存文档</button>
            </div>
            <p class="edit-status">{{ wordEditStatus }}</p>
          </aside>
        </div>

        <div class="actions between">
          <button class="plain-btn" @click="step = 1">返回选择</button>
          <button class="primary-btn" @click="goToExport">确定为最终版</button>
        </div>
      </div>

      <!-- ======== Step 3: 导出下载 ======== -->
      <div v-show="step === 3" class="workflow-panel">
        <div class="panel-head">
          <div>
            <p class="panel-head__eyebrow">Step 03</p>
            <h2 class="panel-head__title">导出下载</h2>
          </div>
          <span class="panel-head__tag">等待导出</span>
        </div>

        <div class="export-layout">
          <div class="final-card">
            <h3>最终版信息</h3>
            <dl>
              <div><dt>课件类型</dt><dd>{{ typeName }}</dd></div>
              <div><dt>模板风格</dt><dd>{{ templateName }}</dd></div>
              <div><dt>页面数量</dt><dd>{{ slides.length }} 页</dd></div>
              <div><dt>课件主题</dt><dd>{{ slides[0]?.title || '未命名' }}</dd></div>
            </dl>
          </div>

          <div class="download-card">
            <h3>选择导出格式</h3>
            <div class="export-buttons-row">
              <button class="export-btn" @click="startDownload('pptx')">下载 .pptx</button>
              <button class="export-btn" @click="startDownload('docx')">下载 .docx</button>
              <button class="export-btn" @click="startDownload('pdf')">下载 .pdf</button>
            </div>

            <div class="download-progress">
              <div class="progress-meta">
                <span>{{ downloadText }}</span>
                <strong>{{ downloadPercent }}%</strong>
              </div>
              <div class="progress-track">
                <div class="progress-bar" :style="{ width: downloadPercent + '%' }" />
              </div>
            </div>

            <div class="download-log">{{ downloadLog }}</div>
          </div>
        </div>

        <div class="actions between">
          <button class="plain-btn" @click="step = 2">返回编辑</button>
          <button class="plain-btn" @click="step = 1">重新选择</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { getDownloadUrl } from '../api'

const props = defineProps({
  files: { type: Object, default: () => ({}) },
  loading: Boolean,
})
const emit = defineEmits(['revise'])

// ---- 页面类型系统 ----
const PAGE_KIND_LABELS = {
  cover: { name: '封面', color: '#1f6feb' },
  catalog: { name: '目录', color: '#6f42c1' },
  content: { name: '正文', color: '#2da44e' },
  summary: { name: '总结', color: '#d29922' },
}

// ---- 初始课件数据 ----
const initialSlides = [
  { kind: 'cover', title: '牛顿第一定律', body: '高一物理 · 45分钟\n从生活中的惯性现象导入，建立学生对运动状态保持的直观认识。' },
  { kind: 'catalog', title: '目录', body: '1. 情境导入\n2. 定律讲解\n3. 实验探究\n4. 课堂练习\n5. 总结回顾' },
  { kind: 'content', title: '教学目标', body: '理解力和运动状态变化的关系。\n能用牛顿第一定律解释生活中的惯性现象。\n通过实验培养证据推理能力。' },
  { kind: 'content', title: '实验演示', body: '演示小车在不同粗糙程度平面上的运动距离。\n引导学生观察阻力越小，小车运动越远的规律。' },
  { kind: 'content', title: '课堂练习', body: '公交车突然刹车时，乘客为什么会向前倾？\n冰壶离手后为什么还能继续向前滑行？' },
  { kind: 'summary', title: '总结回顾', body: '物体不受外力或所受合力为零时，将保持静止或匀速直线运动状态。\n惯性是物体保持原有运动状态的性质。' },
]

// ---- 选项配置 ----
const stepItems = ['选择类型与模板', '实时预览与编辑', '导出下载']
const typeOptions = [
  { value: 'PPT', label: 'PPT', emoji: '📊', desc: '适合课堂演示，展示封面、目录、正文和总结页。' },
  { value: 'Word', label: 'Word', emoji: '📄', desc: '适合打印讲义，按教学目标和教学过程形成文档。' },
  { value: '动画', label: '动画', emoji: '🎬', desc: '适合演示实验步骤，生成分镜和过程说明。' },
  { value: '思维导图', label: '思维导图', emoji: '🧠', desc: '适合梳理知识结构，突出概念关系和重点。' },
]
const templateOptions = [
  { value: 'academic', label: '学术严谨风', emoji: '🎓', desc: '黑白边框、层次清晰，适合理科课程和正式展示。' },
  { value: 'lively', label: '活泼互动风', emoji: '🎨', desc: '高对比块面，适合课堂活动、实验和互动环节。' },
  { value: 'minimal', label: '极简商务风', emoji: '✨', desc: '留白更足，信息克制，适合答辩或汇报型课件。' },
]

// ---- 状态 ----
const step = ref(1)
const type = ref('PPT')
const typeName = ref('PPT')
const template = ref('academic')
const templateName = ref('学术严谨风')
const slides = ref(JSON.parse(JSON.stringify(initialSlides)))
const current = ref(0)
const zoom = ref(1)
const editStatus = ref('当前内容已载入，可直接修改。')

// 生成动画
const showOverlay = ref(false)
const genPercent = ref(0)
const genText = ref('正在解析教学大纲...')
let genTimer = null

// 下载动画
const downloadPercent = ref(0)
const downloadText = ref('尚未开始下载')
const downloadLog = ref('确认最终版后，可选择格式导出。')
let downloadTimer = null

// Word 文档编辑状态
const wordDocTitle = ref('')
const wordDocBody = ref('')
const wordEditStatus = ref('当前内容已载入，可直接修改。')

// ---- 计算属性 ----
const currentSlide = computed(() => slides.value[current.value] || slides.value[0])
const currentKindColor = computed(() => PAGE_KIND_LABELS[currentSlide.value.kind]?.color || '#2da44e')
const currentKindName = computed(() => PAGE_KIND_LABELS[currentSlide.value.kind]?.name || '正文')

const slideCardClass = computed(() => [
  'slide-card',
  'template-' + template.value,
  'kind-' + currentSlide.value.kind,
])

const slideBodyHtml = computed(() => {
  const slide = currentSlide.value
  if (type.value === '思维导图') return renderMindmap(slide)
  if (type.value === '动画') return renderAnimation(slide)
  if (type.value === 'Word') return renderWord(slide)
  return escapeHtml(slide.body).replace(/\n/g, '<br>')
})

// ---- 渲染函数 ----
function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
}

function renderMindmap(slide) {
  const lines = slide.body.split('\n').filter(Boolean)
  const center = slide.title || '主题'
  const items = lines.map(l => l.replace(/^\d+\.\s*/, '').replace(/^[·•-]\s*/, '').trim())
  let html = `<div class="mm-center"><span>${escapeHtml(center)}</span></div>`
  if (items.length === 1) {
    html += `<div class="mm-row"><div class="mm-node mm-leaf"><span>${escapeHtml(items[0])}</span></div></div>`
  } else {
    html += '<div class="mm-row">'
    items.forEach(t => { html += `<div class="mm-node mm-leaf"><span>${escapeHtml(t)}</span></div>` })
    html += '</div>'
  }
  return `<div class="mindmap-canvas">${html}</div>`
}

function renderAnimation(slide) {
  const lines = slide.body.split('\n').filter(Boolean)
  let html = '<div class="anim-track">'
  lines.forEach((line, i) => {
    html += `<div class="anim-step"><div class="anim-dot">${i + 1}</div><div class="anim-label">${escapeHtml(line)}</div></div>`
  })
  html += '</div>'
  return `<div class="anim-canvas">${html}</div>`
}

function renderWord(slide) {
  const lines = slide.body.split('\n').filter(Boolean)
  let html = `<h2 class="word-title">${escapeHtml(slide.title)}</h2>`
  lines.forEach(line => { html += `<p class="word-para">${escapeHtml(line)}</p>` })
  return `<div class="word-doc">${html}</div>`
}

// ---- 操作函数 ----
function saveCurrentSlide() {
  slides.value[current.value].title = currentSlide.value.title.trim() || '未命名页面'
  slides.value[current.value].body = currentSlide.value.body.trim() || '暂无内容'
  editStatus.value = `第 ${current.value + 1} 页已保存。`
}

function addSlide() {
  slides.value.splice(current.value + 1, 0, { kind: 'content', title: '新增教学页面', body: '在这里补充新的教学内容、课堂活动或练习题。' })
  current.value += 1
  editStatus.value = '已新增一页。'
}

function deleteSlide() {
  if (slides.value.length === 1) { editStatus.value = '至少需要保留一页。'; return }
  slides.value.splice(current.value, 1)
  current.value = Math.max(0, current.value - 1)
  editStatus.value = '页面已删除。'
}

function moveSlide(offset) {
  const target = current.value + offset
  if (target < 0 || target >= slides.value.length) { editStatus.value = '当前页面已经在边界位置。'; return }
  const item = slides.value.splice(current.value, 1)[0]
  slides.value.splice(target, 0, item)
  current.value = target
  editStatus.value = '页面顺序已调整。'
}

// ---- 生成进度动画 ----
function runGenerateAnimation() {
  showOverlay.value = true
  genPercent.value = 0
  const labels = ['正在解析教学大纲...', '正在生成封面...', '正在生成目录...', '正在生成正文页面...', '正在生成总结页...', '正在套用模板风格...']
  let li = 0
  clearInterval(genTimer)
  genTimer = setInterval(() => {
    genPercent.value += Math.ceil(Math.random() * 8) + 3
    if (genPercent.value > 100) genPercent.value = 100
    const idx = Math.min(labels.length - 1, Math.floor((genPercent.value / 100) * labels.length))
    if (idx !== li) { li = idx; genText.value = labels[li] }
    if (genPercent.value >= 100) {
      clearInterval(genTimer)
      setTimeout(() => {
        showOverlay.value = false
        step.value = 2
      }, 350)
    }
  }, 200)
}

function goToPreview() {
  editStatus.value = '当前内容已载入，可直接修改。'
  wordEditStatus.value = '当前内容已载入，可直接修改。'
  if (type.value === 'Word') syncWordEditor()
  runGenerateAnimation()
}

function goToExport() {
  if (type.value === 'Word') saveWordDoc()
  else saveCurrentSlide()
  downloadPercent.value = 0
  downloadText.value = '尚未开始下载'
  downloadLog.value = '最终版已确认，请选择导出格式。'
  step.value = 3
}

// ---- Word 文档编辑 ----
function syncWordEditor() {
  wordDocTitle.value = slides.value[0]?.title || ''
  wordDocBody.value = slides.value
    .map(s => `【${PAGE_KIND_LABELS[s.kind]?.name || '正文'}】${s.title}\n${s.body}`)
    .join('\n\n')
}

function saveWordDoc() {
  const body = wordDocBody.value.trim()
  if (!body) { wordEditStatus.value = '文档内容不能为空。'; return }

  const blocks = body.split('\n\n').filter(Boolean)
  const newSlides = []

  blocks.forEach((block) => {
    const lines = block.split('\n')
    const firstLine = lines[0]
    const kindMatch = firstLine.match(/^【(.+?)】/)

    let kind = 'content'
    let slideTitle = firstLine

    if (kindMatch) {
      const kindLabel = kindMatch[1]
      for (const [key, val] of Object.entries(PAGE_KIND_LABELS)) {
        if (val.name === kindLabel) { kind = key; break }
      }
      slideTitle = firstLine.replace(/^【.+?】/, '').trim()
    }

    const slideBody = lines.slice(1).join('\n').trim() || '暂无内容'
    newSlides.push({ kind, title: slideTitle || '未命名', body: slideBody })
  })

  if (newSlides.length > 0) {
    slides.value = newSlides
    current.value = 0
  }

  wordEditStatus.value = 'Word 文档已保存。'
}

// ---- 下载进度动画 ----
function startDownload(format) {
  clearInterval(downloadTimer)
  const fileName = `${slides.value[0]?.title || '课件'}.${format}`
  downloadPercent.value = 0
  downloadText.value = '正在准备文件'
  downloadLog.value = `正在生成 ${fileName}，请稍候。`
  let v = 0
  downloadTimer = setInterval(() => {
    v += Math.ceil(Math.random() * 10)
    if (v > 100) v = 100
    downloadPercent.value = v
    if (v < 35) downloadText.value = '正在整理最终版内容'
    else if (v < 70) downloadText.value = '正在生成导出文件'
    else if (v < 100) downloadText.value = '正在写入下载数据'
    if (v >= 100) {
      clearInterval(downloadTimer)
      downloadText.value = '下载完成'
      downloadLog.value = `已完成：${fileName}。前端演示版已模拟下载进度，请通过后端接口获取真实文件。`
    }
  }, 230)
}

// ---- 监听 loading 变化（来自父组件） ----
watch(() => props.loading, (v) => {
  if (v) runGenerateAnimation()
})

// ---- 清理 ----
onUnmounted(() => {
  clearInterval(genTimer)
  clearInterval(downloadTimer)
})
</script>

<style scoped>
/* ========== 整体 ========== */
.preview-panel { display:flex; flex-direction:column; height:100%; overflow-y:auto; padding:16px 20px; gap:14px; }

/* ========== 步骤指示器 ========== */
.steps { display:flex; align-items:center; gap:0; flex-shrink:0; }
.step-item { display:flex; align-items:center; gap:8px; color:var(--text-tertiary); flex:1; }
.step-item span {
  width:30px; height:30px; display:grid; place-items:center;
  border:1px solid var(--border-subtle); border-radius:50%; font-weight:700; font-size:13px;
  background:var(--glass-sm); flex-shrink:0;
}
.step-item strong { font-size:13px; white-space:nowrap; }
.step-item.done { color:var(--text-secondary); }
.step-item.done span,
.step-item.active span { color:#fff; background:var(--accent); border-color:var(--accent); }
.step-item.active { color:var(--text-primary); }
.step-item:not(:last-child)::after {
  content:''; flex:1; height:1px; background:var(--border-subtle); margin:0 6px;
}

/* ========== 工作区卡片 ========== */
.workflow-card {
  flex:1; position:relative; min-height:0; overflow-y:auto;
  padding:20px; border:1px solid var(--border-ghost); border-radius:var(--r-md);
  background:var(--glass-sm); backdrop-filter:var(--blur-sm); -webkit-backdrop-filter:var(--blur-sm);
}
.workflow-panel { animation:fadeIn 0.2s ease; }

/* ========== 生成进度遮罩 ========== */
.generate-overlay {
  position:absolute; inset:0; z-index:20; display:flex; align-items:center; justify-content:center;
  border-radius:var(--r-md); background:rgba(6,10,20,0.88); backdrop-filter:blur(4px);
}
.generate-card { width:min(360px,80%); text-align:center; }
.generate-spinner {
  width:46px; height:46px; margin:0 auto 16px;
  border:4px solid var(--border-subtle); border-top-color:var(--accent);
  border-radius:50%; animation:spin 0.8s linear infinite;
}
.generate-percent { margin:10px 0; font-size:28px; font-weight:800; color:var(--text-primary); }
.generate-text { margin:0 0 16px; color:var(--text-secondary); font-size:14px; }
.generate-track { height:8px; border-radius:999px; background:var(--glass-md); overflow:hidden; }
.generate-bar { height:100%; background:linear-gradient(90deg,var(--accent),var(--text-primary)); transition:width 0.2s ease; }

/* ========== 面板头部 ========== */
.panel-head { display:flex; align-items:flex-start; justify-content:space-between; gap:14px; margin-bottom:18px; }
.panel-head__eyebrow { margin:0 0 4px; color:var(--text-tertiary); font-size:12px; font-weight:700; }
.panel-head__title { margin:0; font-size:22px; color:var(--text-primary); letter-spacing:-0.01em; }
.panel-head__tag { padding:6px 10px; border-radius:999px; color:var(--text-secondary); background:var(--glass-md); font-size:12px; white-space:nowrap; }

/* ========== 选择布局 ========== */
.choose-layout { display:grid; gap:22px; }
.choose-layout h3 { margin:0 0 10px; font-size:15px; color:var(--text-primary); }

.option-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; }
.template-options { grid-template-columns:repeat(3,1fr); }
.option-card {
  min-height:130px; padding:16px; border:1px solid var(--border-ghost); border-radius:var(--r-sm);
  background:var(--glass-sm); text-align:left; cursor:pointer;
  transition:all var(--t-fast) var(--ease-out); font-family:inherit; color:var(--text-secondary);
  backdrop-filter:var(--blur-sm); -webkit-backdrop-filter:var(--blur-sm);
}
.option-card strong { display:block; margin-bottom:8px; font-size:18px; color:var(--text-primary); }
.option-card span { font-size:13px; line-height:1.6; }
.option-emoji { display:block; font-size:28px; margin-bottom:6px; line-height:1; }
.option-card.active,
.option-card:hover { background:var(--glass-lg); border-color:var(--border-glow); transform:translateY(-2px); }
.option-card.active { position:relative; }
.option-card.active::after {
  content:'✓'; position:absolute; top:8px; right:10px;
  width:22px; height:22px; border-radius:50%;
  background:var(--border-glow); color:#fff; font-size:12px; font-weight:700;
  display:flex; align-items:center; justify-content:center;
}

/* ========== 按钮 ========== */
.actions { display:flex; justify-content:flex-end; gap:10px; margin-top:18px; }
.actions.between { justify-content:space-between; }
.primary-btn, .plain-btn, .danger-btn, .export-btn {
  min-height:38px; padding:0 14px; border-radius:var(--r-sm); font-size:13px;
  cursor:pointer; font-family:inherit; transition:all var(--t-fast) var(--ease-out); border:1px solid;
}
.primary-btn, .export-btn { color:#fff; background:var(--accent); border-color:var(--accent); }
.primary-btn:hover, .export-btn:hover { opacity:0.85; transform:translateY(-1px); }
.plain-btn { color:var(--text-secondary); background:var(--glass-sm); border-color:var(--border-subtle); }
.plain-btn:hover { background:var(--glass-md); border-color:var(--border-glow); }
.plain-btn:disabled { opacity:0.4; cursor:not-allowed; }
.danger-btn { color:#DC2626; background:rgba(220,38,38,0.08); border-color:rgba(220,38,38,0.25); }
.danger-btn:hover { background:rgba(220,38,38,0.15); }

/* ========== 预览布局 ========== */
.preview-layout { display:grid; grid-template-columns:150px minmax(0,1fr) 280px; gap:14px; }
.thumb-list { display:grid; align-content:start; gap:8px; max-height:440px; overflow-y:auto; }
.thumb {
  min-height:72px; padding:10px; border:1px solid var(--border-ghost); border-radius:var(--r-sm);
  color:var(--text-secondary); background:var(--glass-sm); text-align:left;
  cursor:pointer; font-family:inherit; transition:all var(--t-fast) var(--ease-out);
  backdrop-filter:var(--blur-sm); -webkit-backdrop-filter:var(--blur-sm);
}
.thumb.active { background:var(--glass-lg); border-color:var(--border-glow); }
.thumb-top { display:flex; align-items:center; justify-content:space-between; margin-bottom:5px; }
.thumb-kind { padding:2px 6px; border-radius:999px; color:#fff; font-size:10px; font-weight:700; }
.thumb-no { font-size:11px; opacity:0.65; }
.thumb strong { display:block; font-size:13px; line-height:1.35; }

/* ========== 幻灯片区域 ========== */
.slide-toolbar { display:flex; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:12px; }
.slide-toolbar__info { color:var(--text-tertiary); font-size:12px; }
.slide-frame {
  min-height:380px; display:flex; align-items:center; justify-content:center;
  padding:18px; border:1px dashed var(--border-subtle); border-radius:var(--r-sm);
  background:var(--glass-sm); overflow:auto;
}

/* ---- 幻灯片卡片 ---- */
.slide-card {
  width:min(680px,100%); aspect-ratio:16/9; padding:36px 44px;
  border:1px solid var(--border-subtle); border-radius:var(--r-sm);
  background:var(--glass-sm); box-shadow:0 12px 32px rgba(0,0,0,0.18);
  transform-origin:center; transition:transform 0.18s ease; overflow:auto;
}
.slide-kicker { margin:0 0 14px; color:var(--text-tertiary); font-size:13px; }
.slide-kind-badge {
  display:inline-block; padding:3px 10px; margin-bottom:10px;
  border-radius:999px; color:#fff; font-size:11px; font-weight:700;
}
.slide-title { margin:0 0 18px; font-size:32px; letter-spacing:-0.01em; color:var(--text-primary); }
.slide-body { color:var(--text-secondary); font-size:17px; line-height:1.75; white-space:pre-line; }

/* 学术严谨风 */
.slide-card.template-academic { border-top:10px solid #1f6feb; border-color:#1f6feb; }
.slide-card.template-academic .slide-title { color:#90caf9; border-bottom:2px solid #1f6feb; padding-bottom:8px; }
.slide-card.template-academic .slide-body { color:#b0bec5; }

/* 活泼互动风 */
.slide-card.template-lively {
  border:3px solid #ff6b6b; border-radius:14px;
  background:linear-gradient(135deg,rgba(255,107,107,0.06),rgba(255,184,0,0.04));
}
.slide-card.template-lively .slide-title { color:#ff6b6b; font-size:30px; }
.slide-card.template-lively .slide-body { color:#e0e0e0; font-size:16px; }

/* 极简商务风 */
.slide-card.template-minimal {
  border:1px solid var(--border-subtle); border-left:5px solid #888;
  border-radius:4px; box-shadow:none;
}
.slide-card.template-minimal .slide-title { font-weight:300; font-size:30px; letter-spacing:1px; }
.slide-card.template-minimal .slide-body { color:var(--text-tertiary); font-size:16px; }

/* 封面页 */
.slide-card.kind-cover { display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; }
.slide-card.kind-cover .slide-title { font-size:40px; margin-bottom:10px; }
.slide-card.kind-cover .slide-body { font-size:15px; color:var(--text-tertiary); text-align:center; }

/* 总结页 */
.slide-card.kind-summary .slide-body { border-left:3px solid var(--border-glow); padding-left:14px; opacity:0.9; }

/* ========== 编辑器 ========== */
.editor { padding:14px; border:1px solid var(--border-ghost); border-radius:var(--r-sm); background:var(--glass-sm); }
.editor h3 { margin:0 0 12px; font-size:14px; color:var(--text-primary); }
.editor label { display:grid; gap:6px; margin-bottom:10px; color:var(--text-tertiary); font-size:12px; }
.editor input, .editor textarea, .editor select {
  width:100%; border:1px solid var(--border-subtle); border-radius:var(--r-sm);
  padding:9px; color:var(--text-primary); background:var(--glass-sm);
  font-family:inherit; font-size:13px; outline:none; transition:border-color var(--t-fast) var(--ease-out);
}
.editor input:focus, .editor textarea:focus, .editor select:focus { border-color:var(--border-glow); }
.editor-actions { display:grid; grid-template-columns:repeat(2,1fr); gap:7px; }
.editor-actions .danger-btn { grid-column:span 2; }
.edit-status { margin:10px 0 0; padding:10px; border-radius:var(--r-sm); color:var(--text-tertiary); background:var(--glass-sm); font-size:12px; line-height:1.5; }

/* ========== 导出布局 ========== */
.export-layout { display:grid; grid-template-columns:0.9fr 1.1fr; gap:16px; }
.final-card, .download-card { padding:18px; border:1px solid var(--border-ghost); border-radius:var(--r-sm); background:var(--glass-sm); }
.final-card h3, .download-card h3 { margin:0 0 12px; font-size:15px; color:var(--text-primary); }
dl { margin:0; display:grid; gap:10px; }
dl div { display:flex; align-items:center; justify-content:space-between; gap:10px; padding-bottom:10px; border-bottom:1px solid var(--border-ghost); }
dt { color:var(--text-tertiary); font-size:13px; }
dd { margin:0; font-weight:700; color:var(--text-primary); font-size:13px; }

.export-buttons-row { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }
.export-btn { min-height:48px; }

.download-progress { margin-top:18px; }
.progress-meta { display:flex; align-items:center; justify-content:space-between; color:var(--text-tertiary); font-size:13px; }
.progress-track { height:8px; margin-top:10px; border-radius:999px; background:var(--glass-md); overflow:hidden; }
.progress-bar { height:100%; background:var(--accent); transition:width 0.22s ease; }
.download-log { margin-top:12px; padding:10px; border-radius:var(--r-sm); color:var(--text-tertiary); background:var(--glass-sm); font-size:12px; line-height:1.5; }

/* ========== 思维导图画布 ========== */
.mindmap-canvas { display:flex; flex-direction:column; align-items:center; gap:20px; padding:8px 0; }
.mm-center { padding:12px 24px; border-radius:12px; background:linear-gradient(135deg,#1f6feb,#6f42c1); color:#fff; font-size:20px; font-weight:700; box-shadow:0 6px 18px rgba(31,111,235,0.25); }
.mm-row { display:flex; flex-wrap:wrap; justify-content:center; gap:12px; }
.mm-node { position:relative; padding:8px 14px; border:2px solid #1f6feb; border-radius:8px; color:#90caf9; font-size:14px; font-weight:600; }
.mm-node::before { content:''; position:absolute; top:-14px; left:50%; width:2px; height:14px; background:#1f6feb; }

/* ========== 动画/分镜画布 ========== */
.anim-track { display:flex; flex-direction:column; gap:14px; }
.anim-step { display:flex; align-items:center; gap:12px; }
.anim-dot {
  flex-shrink:0; width:28px; height:28px; display:grid; place-items:center;
  border-radius:50%; background:#ff6b6b; color:#fff; font-size:12px; font-weight:700;
}
.anim-step:not(:last-child) .anim-dot { position:relative; }
.anim-step:not(:last-child) .anim-dot::after {
  content:''; position:absolute; top:28px; left:50%; width:2px; height:14px; background:var(--border-subtle);
}
.anim-label { padding:8px 12px; border-left:3px solid #ff6b6b; background:rgba(255,107,107,0.08); border-radius:0 8px 8px 0; font-size:14px; color:var(--text-secondary); }

/* ========== Word 文档画布 ========== */
.word-doc { text-align:left; }
.word-title { margin:0 0 16px; padding-bottom:8px; border-bottom:2px solid var(--border-subtle); font-size:24px; color:var(--text-primary); }
.word-para { margin:0 0 12px; font-size:15px; line-height:1.8; color:var(--text-secondary); text-indent:2em; }

/* ========== Word 独立预览布局 ========== */
.preview-layout--word { grid-template-columns: minmax(0, 1fr) 320px; }
.word-area { display:flex; flex-direction:column; }
.word-doc-label { color:var(--text-primary); font-size:14px; font-weight:600; }

.word-frame {
  min-height:420px; display:flex; align-items:flex-start; justify-content:center;
  padding:18px; border:1px dashed var(--border-subtle); border-radius:var(--r-sm);
  background:var(--glass-sm); overflow:auto;
}

.word-doc-card {
  width:min(720px, 100%); min-height:380px; padding:40px 48px;
  border:1px solid var(--border-subtle); border-radius:var(--r-sm);
  background:var(--glass-sm); box-shadow:0 12px 32px rgba(0,0,0,0.18);
  transform-origin:top center; transition:transform 0.18s ease;
  text-align:left; color:var(--text-primary);
}

.word-doc-cover-title {
  margin:0 0 10px; text-align:center; font-size:30px; font-weight:700;
  padding-bottom:10px; border-bottom:2px solid var(--border-subtle);
}
.word-doc-subtitle {
  margin:0 0 6px; text-align:center; color:var(--text-tertiary);
  font-size:14px; text-indent:0;
}
.word-doc-divider { border:none; border-top:1px solid var(--border-ghost); margin:20px 0; }

.word-doc-heading {
  margin:20px 0 12px; font-size:22px; font-weight:600;
  padding-bottom:6px; border-bottom:2px solid var(--border-subtle);
}
.word-doc-para {
  margin:0 0 12px; font-size:15px; line-height:1.9;
  color:var(--text-secondary); text-indent:2em;
}
.word-doc-para--noindent { text-indent:0; }

.word-doc-list {
  margin:0 0 16px; padding-left:2em; line-height:2;
  color:var(--text-primary); font-size:15px;
}
.word-doc-summary-box {
  border-left:3px solid var(--border-glow); padding:8px 16px;
  margin:10px 0; background:rgba(31,111,235,0.04);
}

/* ========== 动画 ========== */
@keyframes fadeIn { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
@keyframes spin { to{transform:rotate(360deg)} }
</style>
