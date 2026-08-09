<template>
  <div class="chat-panel">
    <!-- 星空背景 -->
    <div class="stars-bg" aria-hidden="true">
      <div v-for="(s, i) in stars" :key="i" :class="['star', s.size]" :style="s.style" />
    </div>

    <!-- 头部 -->
    <div class="chat-header">
      <div class="chat-title">AI 教学助手</div>
      <div class="header-actions">
        <div :class="['chat-status', apiOnline ? 'status-ok' : 'status-error']">
          {{ apiOnline ? 'API已连接' : '服务未连接' }}
        </div>
        <button class="btn-new-chat" @click="$emit('new-session')" title="开始新会话">
          <span>&#x27F3;</span> 新会话
        </button>
      </div>
    </div>

    <!-- 消息区 -->
    <div class="chat-messages" ref="msgContainer" @scroll="onScroll">
      <!-- 欢迎区 + 功能卡片 -->
      <div v-if="messages.length === 0" class="welcome-section">
        <div class="welcome-avatar">
          <svg viewBox="0 0 48 48">
            <ellipse cx="24" cy="24" rx="16" ry="14" />
            <circle cx="24" cy="20" r="6" />
            <circle cx="24" cy="19" r="2" />
            <line x1="24" y1="35" x2="18" y2="45" />
            <line x1="24" y1="35" x2="30" y2="45" />
            <line x1="24" y1="10" x2="24" y2="4" />
            <line x1="20" y1="11" x2="18" y2="5" />
            <line x1="28" y1="11" x2="30" y2="5" />
          </svg>
        </div>
        <div class="welcome-title">您好，困困</div>
        <div class="welcome-subtitle">我是您的全科 AI 教学助手，可以根据学科和学习情况，为您提供智能备课、知识讲解和学习建议。</div>

        <div class="feature-cards">
          <div
            v-for="card in featureCards"
            :key="card.type"
            class="feature-card"
            @click="sendByType(card.type, card.preset)"
          >
            <div :class="['feature-icon-box', card.iconClass]">{{ card.icon }}</div>
            <div class="feature-title">{{ card.title }}</div>
            <div class="feature-desc">{{ card.desc }}</div>
            <div class="feature-tags">
              <span
                v-for="tag in card.tags"
                :key="tag.label"
                class="feature-tag"
                @click.stop="onTagClick(tag)"
              >{{ tag.label }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 消息列表 -->
      <div
        v-for="(m, i) in messages"
        :key="i"
        :class="['message', m.role === 'user' ? 'msg-user' : 'msg-assistant']"
        :data-idx="i"
      >
        <div class="msg-avatar">
          <svg v-if="m.role === 'user'" viewBox="0 0 48 48">
            <rect x="8" y="10" width="32" height="34" rx="4" />
            <ellipse cx="24" cy="22" rx="10" ry="8" />
            <circle cx="18" cy="20" r="2" />
            <circle cx="30" cy="20" r="2" />
            <path d="M18 26 Q24 32 30 26" />
            <rect x="10" y="36" width="8" height="6" rx="2" />
            <rect x="30" y="36" width="8" height="6" rx="2" />
          </svg>
          <svg v-else viewBox="0 0 48 48">
            <ellipse cx="24" cy="24" rx="16" ry="14" />
            <circle cx="24" cy="20" r="6" />
            <circle cx="24" cy="19" r="2" />
            <line x1="24" y1="35" x2="18" y2="45" />
            <line x1="24" y1="35" x2="30" y2="45" />
            <line x1="24" y1="10" x2="24" y2="4" />
            <line x1="20" y1="11" x2="18" y2="5" />
            <line x1="28" y1="11" x2="30" y2="5" />
          </svg>
        </div>
        <div class="msg-body">
          <div class="msg-content">
            <template v-for="(block, bi) in parseContent(m.content)" :key="bi">
              <!-- 文本块 -->
              <div v-if="block.type === 'text'" class="msg-text-block">{{ block.text }}</div>
              <!-- 选择题（只显示第一个未回答的） -->
              <div
                v-else-if="block.type === 'choice'"
                class="interaction-block"
                v-show="isInteractionVisible(m, bi)"
              >
                <div class="interaction-prompt">{{ block.prompt }}</div>
                <div class="choice-options">
                  <button
                    v-for="(opt, oi) in block.options"
                    :key="oi"
                    class="choice-btn"
                    :disabled="block.answered"
                    @click="onChoiceClick(m, bi, block, opt)"
                  >{{ opt }}</button>
                </div>
              </div>
              <!-- 数字输入（只显示第一个未回答的） -->
              <div
                v-else-if="block.type === 'input'"
                class="interaction-block"
                v-show="isInteractionVisible(m, bi)"
              >
                <div class="interaction-prompt">{{ block.prompt }}</div>
                <div class="input-option">
                  <input
                    v-model="block.inputValue"
                    type="number"
                    class="number-input"
                    :placeholder="block.placeholder"
                    :disabled="block.answered"
                    @keyup.enter="onInputSubmit(m, bi, block)"
                  />
                  <button
                    class="btn-submit"
                    :disabled="block.answered"
                    @click="onInputSubmit(m, bi, block)"
                  >确认</button>
                </div>
              </div>
            </template>
          </div>
          <span v-if="loading && i === messages.length - 1 && m.role === 'assistant'" class="typing-cursor" />
          <!-- 直接导出按钮：AI 回复且前一条用户消息命中关键词 -->
          <div v-if="m.role === 'assistant' && m.content && getExportType(i)" class="export-buttons">
            <button
              v-if="getExportType(i) === 'docx'"
              class="btn-export btn-export-docx"
              :disabled="exporting"
              @click="onExport('docx', i)"
            >📄 下载 Word 文档</button>
            <button
              class="btn-export btn-export-pptx"
              :disabled="exporting"
              @click="onExport('pptx', i)"
            >📊 下载 PPT 课件</button>
            <button
              class="btn-export btn-export-preview"
              @click="onSendToPreview(i)"
            >✏️ 送入预览编辑</button>
          </div>
        </div>
      </div>

      <!-- 打字指示器 -->
      <div v-if="loading && (messages.length === 0 || messages[messages.length - 1].role !== 'assistant')" class="message msg-assistant">
        <div class="msg-avatar">
          <svg viewBox="0 0 48 48">
            <ellipse cx="24" cy="24" rx="16" ry="14" />
            <circle cx="24" cy="20" r="6" />
            <line x1="24" y1="35" x2="18" y2="45" />
            <line x1="24" y1="35" x2="30" y2="45" />
            <line x1="24" y1="10" x2="24" y2="4" />
          </svg>
        </div>
        <div class="msg-body"><div class="typing-indicator"><span /><span /><span /></div></div>
      </div>

      <div ref="bottomRef" />
    </div>

    <!-- 右侧垂直居中滚动导航（相对 chat-panel 定位，不参与 flex 流） -->
    <div v-if="userMsgIndices.length > 1" class="scroll-nav">
      <div
        v-for="idx in userMsgIndices"
        :key="idx"
        :class="['scroll-dot', { active: idx === activeUserIdx }]"
        @click="scrollToMessage(idx)"
      />
    </div>

    <!-- 输入区 -->
    <div class="chat-input-area">
      <div class="input-wrapper">
        <textarea
          ref="inputEl"
          v-model="input"
          class="chat-input"
          placeholder="发消息..."
          rows="1"
          :disabled="loading"
          @input="autoResize"
          @keydown="handleKeyDown"
        />
        <div class="input-actions">
          <button
            class="btn-icon-mic"
            :class="{ listening: micListening }"
            :title="micListening ? '正在聆听...点击停止' : '语音输入'"
            @click="toggleMic"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="3" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0 0 14 0"/><line x1="12" y1="18" x2="12" y2="22"/></svg>
          </button>
          <button v-if="loading" class="btn-stop-circle" @click="$emit('stop')" title="停止">
            <svg viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>
          </button>
          <button v-else class="btn-send-circle" :disabled="!input.trim()" @click="handleSend" title="发送">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>
          </button>
        </div>
      </div>
      <div class="input-hints">AI 可能会产生不准确的信息，请核实重要内容</div>
      <div v-if="intent" class="chat-intent-bar">
        <span class="badge badge-accent">意图就绪</span>
        <button class="btn btn-primary btn-sm" @click="$emit('generate')">生成课件</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, onMounted, computed, reactive } from 'vue'

import { exportDocument } from '../api'

const props = defineProps({
  messages: { type: Array, default: () => [] },
  loading: Boolean,
  intent: Object,
})
const emit = defineEmits(['send', 'generate', 'stop', 'new-session', 'send-to-preview'])

const input = ref('')
const inputEl = ref(null)
const msgContainer = ref(null)
const bottomRef = ref(null)
const apiOnline = ref(false)
const exporting = ref(false)
const activeUserIdx = ref(-1)

// 追踪每条 AI 消息已回答到第几个交互组件
// key: message index, value: answered block index
const answeredMap = reactive({})

// 判断某个交互块是否可见（只显示第一个未回答的交互组件）
function isInteractionVisible(msg, blockIdx) {
  if (msg.role !== 'assistant') return true
  const blocks = parseContent(msg.content)
  // 找到所有交互块
  const interactionBlocks = blocks
    .map((b, idx) => ({ block: b, idx }))
    .filter(b => b.block.type === 'choice' || b.block.type === 'input')
  if (interactionBlocks.length === 0) return true
  // 找到第一个未回答的
  const msgKey = msg._id || msg.id || 'latest'
  const answeredCount = answeredMap[msgKey] ?? 0
  const targetIdx = interactionBlocks[answeredCount]?.idx
  return blockIdx === targetIdx
}

// ---- 星空 ----
const stars = ref([])
function createStars() {
  const sizes = ['small', 'medium', 'large']
  const arr = []
  for (let i = 0; i < 100; i++) {
    arr.push({
      size: sizes[Math.floor(Math.random() * sizes.length)],
      style: {
        left: Math.random() * 100 + '%',
        top: Math.random() * 100 + '%',
        animationDelay: Math.random() * 3 + 's',
        animationDuration: (2 + Math.random() * 3) + 's',
      },
    })
  }
  stars.value = arr
}

// ---- 功能卡片 + 标签预设（来自 AITEACH script.js） ----
const featureCards = [
  {
    type: 'analysis', icon: '📝', iconClass: 'icon-purple',
    title: '教学解析', desc: '分析教学重点难点，提供突破方法和教学策略',
    preset: '请帮我进行教学解析：选择一个你正在教或想教的知识点，我会为你详细分析教学重点、难点和突破方法。',
    tags: [
      { label: '高一数学', type: 'analysis', text: '请帮我分析高一数学的教学重点和难点，提供突破方法。' },
      { label: '语文教案', type: 'analysis', text: '请帮我设计一份语文教案，包括教学目标、重难点和教学过程。' },
      { label: '物理课件', type: 'analysis', text: '请帮我制作物理课件的教学设计，包含重点难点分析。' },
    ],
  },
  {
    type: 'explain', icon: '💡', iconClass: 'icon-blue',
    title: '知识讲解', desc: '由浅入深讲解知识点原理，帮助理解掌握',
    preset: '请帮我讲解一个知识点：告诉我你想学的概念或主题，我会用最简单的方式解释清楚。',
    tags: [
      { label: '数学解析', type: 'explain', text: '请帮我详细解析数学知识点，从基础到进阶逐步讲解。' },
      { label: '语法分析', type: 'explain', text: '请帮我分析英语语法，用通俗易懂的方式讲解。' },
      { label: '化学原理', type: 'explain', text: '请帮我讲解化学原理，结合实例说明。' },
    ],
  },
  {
    type: 'suggestions', icon: '🎯', iconClass: 'icon-green',
    title: '学习建议', desc: '个性化学习计划，智能答疑解惑，高效提升',
    preset: '请帮我提供学习建议：告诉我你正在学习的科目和内容，我会为你制定个性化的学习计划和方法。',
    tags: [
      { label: '学习计划', type: 'suggestions', text: '请帮我制定一个学习计划，帮助我系统学习相关知识。' },
      { label: '答疑解惑', type: 'suggestions', text: '请帮我解答学习中的疑问，提供详细的解释和思路。' },
      { label: '知识梳理', type: 'suggestions', text: '请帮我梳理知识体系，建立清晰的知识框架。' },
    ],
  },
]

function onTagClick(tag) { sendByType(tag.type, tag.text) }

// ---- 健康检查 ----
async function checkHealth() {
  try {
    const resp = await fetch('/api/health')
    if (resp.ok) apiOnline.value = true
  } catch { apiOnline.value = false }
}

// ---- 关键词导出检测（来自 AITEACH script.js） ----
function detectExportType(text) {
  const t = (text || '').toLowerCase()
  if (/ppt|课件|幻灯片|演示文稿|powerpoint|presentation/.test(t)) return 'pptx'
  if (/教案|word|文档|docx|教学设计|方案|导学案|教学目标|教学方案/.test(t)) return 'docx'
  return null
}
function getExportType(aiMsgIndex) {
  if (aiMsgIndex <= 0) return null
  const prev = props.messages[aiMsgIndex - 1]
  if (prev && prev.role === 'user') return detectExportType(prev.content)
  return null
}

// ---- 解析内容为结构化块（文本 + 交互组件） ----
// 解析 {{CHOICE:选项A|选项B}} 和 {{INPUT:提示|默认值}} 标记
function parseContent(c) {
  if (!c) return [{ type: 'text', text: '' }]
  // 将字面 \n 转换为真正的换行符（处理 SSE 传输中可能的转义问题）
  let content = c.replace(/\\r\\n/g, '\n').replace(/\\n/g, '\n')
  const blocks = []
  const regex = /\{\{(CHOICE|INPUT):([^}]+)\}\}/g
  let lastIdx = 0
  let match
  while ((match = regex.exec(content)) !== null) {
    // 标记前的文本
    if (match.index > lastIdx) {
      const text = content.slice(lastIdx, match.index)
      if (text) blocks.push({ type: 'text', text })
    }
    const tagType = match[1]
    const tagContent = match[2]
    if (tagType === 'CHOICE') {
      const options = tagContent.split('|').map(s => s.trim()).filter(Boolean)
      blocks.push({
        type: 'choice',
        prompt: '请选择：',
        options,
        answered: false,
      })
    } else if (tagType === 'INPUT') {
      const parts = tagContent.split('|')
      blocks.push({
        type: 'input',
        prompt: '请输入：',
        placeholder: parts[0] ? parts[0].trim() : '请输入',
        inputValue: parts[1] ? parts[1].trim() : '',
        answered: false,
      })
    }
    lastIdx = regex.lastIndex
  }
  // 检查是否有不完整的 {{ 标记（正在流式传输中）
  const lastOpen = content.lastIndexOf('{{')
  if (lastOpen > lastIdx) {
    // 有未闭合的 {{，将其后的内容作为普通文本处理
    if (lastIdx < lastOpen) {
      const text = content.slice(lastIdx, lastOpen)
      if (text) blocks.push({ type: 'text', text })
    }
    const partial = content.slice(lastOpen)
    if (partial) blocks.push({ type: 'text', text: partial })
    return blocks
  }
  // 剩余文本
  if (lastIdx < content.length) {
    const text = content.slice(lastIdx)
    if (text) blocks.push({ type: 'text', text })
  }
  if (blocks.length === 0) blocks.push({ type: 'text', text: content })
  return blocks
}

// ---- 交互：点击选项 ----
function onChoiceClick(msg, blockIdx, block, option) {
  if (block.answered) return
  block.answered = true
  // 标记该消息的交互进度
  const msgKey = msg._id || msg.id || 'latest'
  answeredMap[msgKey] = (answeredMap[msgKey] ?? 0) + 1
  emit('send', option, '')
}

// ---- 交互：提交数字输入 ----
function onInputSubmit(msg, blockIdx, block) {
  if (block.answered) return
  const val = block.inputValue?.trim()
  if (!val) return
  block.answered = true
  // 标记该消息的交互进度
  const msgKey = msg._id || msg.id || 'latest'
  answeredMap[msgKey] = (answeredMap[msgKey] ?? 0) + 1
  emit('send', val, '')
}

// ---- 发送 ----
function handleSend() {
  if (!input.value.trim() || props.loading) return
  emit('send', input.value.trim(), '')
  input.value = ''
  nextTick(autoResize)
}
function sendByType(promptType, text) {
  if (props.loading) return
  emit('send', text, promptType)
}
function handleKeyDown(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
}
function autoResize() {
  const el = inputEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
}

// ---- 直接导出（下载 docx / pptx） ----
async function onExport(format, aiMsgIndex) {
  const aiMsg = props.messages[aiMsgIndex]
  if (!aiMsg || !aiMsg.content) return
  const prevUser = props.messages[aiMsgIndex - 1]
  const rawTitle = (prevUser && prevUser.content) ? prevUser.content : '教学文档'
  const title = rawTitle.replace(/[\\/*?:"<>|]/g, '').substring(0, 30) || '教学文档'
  exporting.value = true
  try {
    const blob = await exportDocument(format, aiMsg.content, title)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = title + '.' + format
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (e) {
    alert('导出失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    exporting.value = false
  }
}

// ---- 送入预览编辑 ----
function onSendToPreview(aiMsgIndex) {
  const aiMsg = props.messages[aiMsgIndex]
  if (!aiMsg || !aiMsg.content) return
  const prevUser = props.messages[aiMsgIndex - 1]
  const rawTitle = (prevUser && prevUser.content) ? prevUser.content : '教学文档'
  const title = rawTitle.replace(/[\\/*?:"<>|]/g, '').substring(0, 30) || '教学文档'
  const exportType = getExportType(aiMsgIndex)
  emit('send-to-preview', { content: aiMsg.content, title, exportType })
}

// ---- 语音输入（Web Speech API，不可用时静默降级） ----
const micListening = ref(false)
let recognition = null
function toggleMic() {
  if (!recognition) { alert('当前浏览器不支持语音输入'); return }
  if (micListening.value) { recognition.stop(); return }
  try { recognition.start() } catch { /* ignore */ }
}
function initMic() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SR) return
  recognition = new SR()
  recognition.lang = 'zh-CN'
  recognition.continuous = false
  recognition.interimResults = true
  recognition.onstart = () => { micListening.value = true }
  recognition.onend = () => { micListening.value = false }
  recognition.onerror = () => { micListening.value = false }
  recognition.onresult = (e) => {
    let txt = ''
    for (let i = e.resultIndex; i < e.results.length; i++) txt += e.results[i][0].transcript
    input.value = txt
    nextTick(autoResize)
  }
}

// ---- 滚动导航 ----
const userMsgIndices = computed(() =>
  props.messages.map((m, i) => m.role === 'user' ? i : -1).filter(i => i >= 0)
)
function scrollToMessage(idx) {
  const el = msgContainer.value?.querySelector(`:scope > [data-idx="${idx}"]`)
  if (!el || !msgContainer.value) return
  const container = msgContainer.value
  const containerRect = container.getBoundingClientRect()
  const elRect = el.getBoundingClientRect()
  const offset = elRect.top - containerRect.top + container.scrollTop - 20
  container.scrollTo({ top: offset, behavior: 'smooth' })
}
function onScroll() {
  const c = msgContainer.value
  if (!c) return
  const containerTop = c.getBoundingClientRect().top
  let active = -1
  userMsgIndices.value.forEach(idx => {
    const el = c.querySelector(`[data-idx="${idx}"]`)
    if (!el) return
    const top = el.getBoundingClientRect().top - containerTop
    if (top <= 150) active = idx
  })
  activeUserIdx.value = active
}

// ---- 自动滚到底部 ----
watch(() => props.messages.length, () => nextTick(() => bottomRef.value?.scrollIntoView({ behavior: 'smooth' })))
watch(() => props.loading, (v) => { if (v) nextTick(() => bottomRef.value?.scrollIntoView({ behavior: 'smooth' })) })
watch(() => props.messages, () => {
  // 内容流式增长时也跟随滚到底（仅当用户已在底部附近）
  const c = msgContainer.value
  if (!c) return
  const nearBottom = c.scrollHeight - c.scrollTop - c.clientHeight < 120
  if (nearBottom) nextTick(() => bottomRef.value?.scrollIntoView({ behavior: 'smooth' }))
}, { deep: true })

onMounted(() => {
  checkHealth()
  createStars()
  initMic()
  nextTick(autoResize)
})
</script>

<style scoped>
.chat-panel {
  --bg-panel: #0C0C16;
  --bg-secondary: rgba(255, 255, 255, 0.04);
  --text-muted: #6A6A7C;
  --accent-soft: rgba(0, 212, 170, 0.15);

  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: var(--bg-panel);
}

.stars-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
  background: radial-gradient(ellipse at 30% 20%, rgba(0, 212, 170, 0.04) 0%, transparent 60%),
              radial-gradient(ellipse at 70% 80%, rgba(0, 180, 148, 0.03) 0%, transparent 50%);
}
.star {
  position: absolute;
  width: 2px; height: 2px;
  background: var(--accent);
  border-radius: 50%;
  animation: twinkle 3s infinite;
  box-shadow: 0 0 6px rgba(0, 212, 170, 0.6);
}
.star.large { width: 3px; height: 3px; box-shadow: 0 0 10px rgba(0, 212, 170, 0.8); }
.star.medium { width: 2px; height: 2px; box-shadow: 0 0 8px rgba(0, 212, 170, 0.5); }
.star.small { width: 1px; height: 1px; box-shadow: 0 0 4px rgba(0, 212, 170, 0.3); }
@keyframes twinkle { 0%,100% { opacity: 0.15; transform: scale(0.8); } 50% { opacity: 0.8; transform: scale(1.1); } }

.chat-header {
  position: relative; z-index: 2;
  padding: 14px 28px; background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
  min-height: 56px; flex-shrink: 0;
}
.chat-title {
  font-size: 16px; font-weight: 700; color: var(--text-primary);
  letter-spacing: -0.01em;
}
.header-actions { display: flex; align-items: center; gap: 12px; }
.chat-status {
  font-size: 12px; padding: 4px 10px; border-radius: 12px;
  background: var(--bg-raised); color: var(--text-muted); border: 1px solid var(--border);
}
.chat-status.status-ok { background: rgba(52, 211, 153, 0.1); color: var(--success); border-color: rgba(52, 211, 153, 0.25); }
.chat-status.status-error { background: rgba(248, 113, 113, 0.1); color: var(--danger); border-color: rgba(248, 113, 113, 0.25); }
.btn-new-chat {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 14px; background: var(--bg-raised);
  border: 1px solid var(--border); border-radius: 8px;
  color: var(--text-secondary); font-size: 12px; cursor: pointer;
  transition: all 0.2s; font-family: inherit;
}
.btn-new-chat:hover {
  background: var(--accent-soft); border-color: var(--accent);
  color: var(--accent);
}

.chat-messages {
  position: relative; z-index: 1;
  flex: 1; overflow-y: auto; padding: 20px 28px;
  display: flex; flex-direction: column; gap: 16px;
}
.message { display: flex; gap: 12px; width: 100%; max-width: 75%; animation: fadeIn 0.3s ease; }
.msg-user { align-self: flex-end; flex-direction: row-reverse; }
.msg-assistant { align-self: flex-start; }
.msg-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--bg-card); display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; border: 1px solid var(--border);
}
.msg-avatar svg { width: 26px; height: 26px; }
.msg-avatar svg :deep(path), .msg-avatar svg :deep(circle), .msg-avatar svg :deep(ellipse),
.msg-avatar svg :deep(line), .msg-avatar svg :deep(rect) {
  fill: none; stroke: var(--text-secondary); stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round;
}
.msg-body {
  background: var(--bg-card); padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid var(--border);
  max-width: 100%;
  width: fit-content;
}
.msg-assistant .msg-body {
  background: var(--bg-card); padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid var(--border);
}
.msg-user .msg-body {
  background: var(--accent);
  color: #0A0A12; border: none;
}
.msg-user .msg-body :deep(*) { color: #0A0A12 !important; }
.msg-content {
  font-size: 14px;
  line-height: 1.75;
  word-break: break-all;
  overflow-wrap: break-word;
  letter-spacing: 0.02em;
}
.msg-content .msg-text-block {
  white-space: pre-line;
}
.msg-content :deep(br) { display: block; }
.msg-content [style*="letter-spacing"] { letter-spacing: normal !important; }

/* 交互组件样式 */
.interaction-block {
  margin: 12px 0 8px;
  padding: 12px;
  background: var(--bg-secondary, rgba(255,255,255,0.04));
  border-radius: 10px;
  border: 1px solid var(--border);
}
.interaction-prompt {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  font-weight: 500;
}
.choice-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.choice-btn {
  padding: 8px 16px;
  font-size: 13px;
  background: var(--bg-card, #1e1e2a);
  color: var(--text-primary);
  border: 1px solid var(--accent, #6c5ce7);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}
.choice-btn:hover:not(:disabled) {
  background: var(--accent, #6c5ce7);
  color: #fff;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(108,92,231,0.3);
}
.choice-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.input-option {
  display: flex;
  gap: 8px;
  align-items: center;
}
.number-input {
  flex: 1;
  padding: 8px 12px;
  font-size: 14px;
  background: var(--bg-card, #1e1e2a);
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-radius: 8px;
  outline: none;
  transition: border-color 0.2s;
}
.number-input:focus {
  border-color: var(--accent, #6c5ce7);
}
.number-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn-submit {
  padding: 8px 16px;
  font-size: 13px;
  background: var(--accent, #6c5ce7);
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}
.btn-submit:hover:not(:disabled) {
  background: #5b4cdb;
  transform: translateY(-1px);
}
.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.typing-cursor {
  display: inline-block; width: 2px; height: 16px;
  background: var(--accent); margin-left: 2px;
  vertical-align: text-bottom; animation: blink 0.8s infinite;
}
@keyframes blink { 0%,50% { opacity: 1; } 51%,100% { opacity: 0; } }

.typing-indicator { display: flex; gap: 4px; padding: 4px 0; }
.typing-indicator span {
  width: 8px; height: 8px; background: var(--accent);
  border-radius: 50%; animation: pulse 1.4s infinite;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
@keyframes pulse { 0%,60%,100% { opacity: 0.3; transform: scale(0.8); } 30% { opacity: 1; transform: scale(1); } }

.welcome-section {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  flex: 1; padding: 40px 0 20px; animation: fadeIn 0.5s ease;
}
.welcome-avatar {
  width: 64px; height: 64px; border-radius: 50%;
  background: var(--bg-card); display: flex; align-items: center; justify-content: center;
  border: 2px solid var(--accent); margin-bottom: 16px;
}
.welcome-avatar svg { width: 40px; height: 40px; }
.welcome-avatar svg :deep(circle), .welcome-avatar svg :deep(ellipse),
.welcome-avatar svg :deep(line), .welcome-avatar svg :deep(rect) {
  fill: none; stroke: var(--accent); stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round;
}
.welcome-title {
  font-size: 28px; font-weight: 700; color: var(--text-primary); margin-bottom: 8px;
  letter-spacing: -0.02em;
}
.welcome-subtitle {
  font-size: 14px; color: var(--text-secondary); text-align: center;
  max-width: 520px; line-height: 1.6; margin-bottom: 24px;
}

.feature-cards {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px;
  width: 100%; max-width: 640px;
}
.feature-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 12px; padding: 18px 16px; cursor: pointer;
  transition: all 0.3s ease;
}
.feature-card:hover {
  border-color: var(--accent);
  background: var(--accent-soft);
  transform: translateY(-3px);
}
.feature-icon-box {
  width: 44px; height: 44px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; margin-bottom: 12px; border: 1px solid; transition: all 0.3s ease;
}
.icon-purple { background: var(--accent-soft); border-color: rgba(0, 212, 170, 0.35); }
.icon-blue { background: rgba(59, 130, 246, 0.12); border-color: rgba(59, 130, 246, 0.35); }
.icon-green { background: rgba(52, 211, 153, 0.12); border-color: rgba(52, 211, 153, 0.35); }
.feature-title {
  font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: 6px;
}
.feature-desc { font-size: 12px; color: var(--text-secondary); line-height: 1.5; margin-bottom: 14px; }
.feature-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.feature-tag {
  font-size: 12px; padding: 5px 10px;
  background: var(--bg-raised); border: 1px solid var(--border);
  border-radius: 6px; color: var(--text-secondary); cursor: pointer; transition: all 0.2s ease;
}
.feature-tag:hover {
  background: var(--accent-soft); border-color: var(--accent);
  color: var(--accent);
}

.export-buttons {
  display: flex; gap: 8px; margin-top: 12px; padding-top: 12px;
  border-top: 1px solid var(--border); flex-wrap: wrap;
}
.btn-export {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 16px; border-radius: 20px;
  font-size: 13px; font-weight: 500; cursor: pointer;
  border: 1px solid; transition: all 0.2s; font-family: inherit;
}
.btn-export:disabled { opacity: 0.5; cursor: wait; }
.btn-export-docx { background: rgba(52, 211, 153, 0.1); color: var(--success); border-color: rgba(52, 211, 153, 0.3); }
.btn-export-docx:hover:not(:disabled) { background: rgba(52, 211, 153, 0.15); }
.btn-export-pptx { background: rgba(251, 191, 36, 0.1); color: var(--warning); border-color: rgba(251, 191, 36, 0.3); }
.btn-export-pptx:hover:not(:disabled) { background: rgba(251, 191, 36, 0.15); }
.btn-export-preview { background: rgba(0, 212, 170, 0.1); color: var(--accent); border-color: rgba(0, 212, 170, 0.3); }
.btn-export-preview:hover { background: rgba(0, 212, 170, 0.15); transform: translateY(-1px); }

.scroll-nav {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  display: flex; flex-direction: column; gap: 8px; z-index: 5;
  background: rgba(20, 20, 32, 0.85); padding: 10px 6px; border-radius: 20px;
  border: 1px solid var(--border); backdrop-filter: blur(8px);
  overflow-y: auto; max-height: 60%;
}
.scroll-dot {
  width: 8px; height: 8px; background: var(--text-muted);
  border-radius: 50%; cursor: pointer; transition: all 0.2s ease;
  border: 1px solid var(--border);
}
.scroll-dot:hover { background: var(--accent); transform: scale(1.3); }
.scroll-dot.active { background: var(--accent); }

.chat-input-area {
  position: relative; z-index: 2;
  padding: 6px 28px 16px; background: var(--bg-panel); flex-shrink: 0;
}
.input-wrapper {
  max-width: 760px; margin: 0 auto; background: var(--bg-card);
  border: 1px solid var(--border); border-radius: 20px;
  padding: 6px 12px 4px; transition: all 0.2s ease;
  display: flex; flex-direction: row; align-items: center; gap: 8px;
}
.input-wrapper:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }
.chat-input {
  flex: 1; resize: none; min-height: 24px; max-height: 120px; line-height: 1.4;
  padding: 4px 0; border: none; border-radius: 0;
  font-size: 14px; font-family: inherit; color: var(--text-primary);
  background: transparent; outline: none; box-shadow: none;
}
.chat-input::placeholder { color: var(--text-muted); }
.chat-input:disabled { opacity: 0.5; }
.input-actions { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
.btn-icon-mic {
  width: 36px; height: 36px; border-radius: 50%;
  background: transparent; border: 1px solid var(--border);
  color: var(--text-secondary); cursor: pointer;
  display: flex; align-items: center; justify-content: center; transition: all 0.2s ease;
}
.btn-icon-mic svg { width: 18px; height: 18px; }
.btn-icon-mic:hover { color: var(--accent); border-color: var(--accent); }
.btn-icon-mic.listening { color: var(--danger); border-color: var(--danger); animation: pulse 1s infinite; }
.btn-send-circle {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--accent); border: none; color: #0A0A12; cursor: pointer;
  display: flex; align-items: center; justify-content: center; transition: all 0.2s ease;
}
.btn-send-circle svg { width: 18px; height: 18px; }
.btn-send-circle:hover:not(:disabled) { background: var(--accent-hover); transform: scale(1.05); }
.btn-send-circle:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-stop-circle {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--danger); border: none; color: #fff; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
}
.btn-stop-circle svg { width: 14px; height: 14px; }
.input-hints { margin-top: 8px; font-size: 12px; color: var(--text-muted); text-align: center; }
.chat-intent-bar { display: flex; align-items: center; justify-content: space-between; margin-top: 10px; max-width: 760px; margin-left: auto; margin-right: auto; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 640px) {
  .feature-cards { grid-template-columns: 1fr; }
  .welcome-title { font-size: 22px; }
  .message { max-width: 92%; }
  .chat-header, .chat-messages, .chat-input-area { padding-left: 16px; padding-right: 16px; }
}
</style>
