<template>
  <div class="chat-panel">
    <div class="chat-header">
      <div class="chat-header__title">AI 教学助手</div>
      <div :class="['chat-header__status', apiOnline ? 'status-ok' : 'status-error']">{{ apiOnline ? 'API已连接' : '服务未连接' }}</div>
    </div>

    <div class="chat-messages" ref="msgContainer">
      <!-- 初始欢迎消息 -->
      <div v-if="messages.length === 0" class="chat-msg chat-msg--assistant">
        <div class="chat-msg__avatar">AI</div>
        <div class="chat-msg__bubble">
          <p>你好！我是 AI 教学助手，可以帮你备课、生成课件和教案。</p>
          <p>直接告诉我你想教什么内容，或者点击下方的快捷功能开始。</p>
        </div>
      </div>

      <!-- 消息列表 -->
      <div v-for="(m, i) in messages" :key="i" :class="['chat-msg', 'chat-msg--' + m.role]">
        <div class="chat-msg__avatar">{{ m.role === 'assistant' ? 'AI' : '我' }}</div>
        <div class="chat-msg__body">
          <div class="chat-msg__bubble" v-html="renderContent(m.content)" />
          <!-- 下载按钮：当用户消息包含 PPT/Word 关键词时，在 AI 回复后显示 -->
          <div v-if="m.role === 'assistant' && m.content && getExportType(i)" class="export-buttons">
            <button
              v-if="getExportType(i) === 'docx'"
              class="btn-export btn-export-docx"
              @click="$emit('generate')"
            >下载 Word 文档</button>
            <button
              v-if="getExportType(i) === 'pptx'"
              class="btn-export btn-export-pptx"
              @click="$emit('generate')"
            >下载 PPT 课件</button>
            <button
              v-if="getExportType(i) === 'docx'"
              class="btn-export btn-export-pptx"
              @click="$emit('generate')"
            >下载 PPT 课件</button>
          </div>
        </div>
      </div>

      <!-- 快捷功能区（首次发送消息后隐藏） -->
      <div v-if="messages.length === 0 && !showQuickPromptsHidden" class="quick-prompts">
        <div class="quick-prompts__title">快捷功能</div>
        <div class="quick-prompt-grid">
          <button class="quick-prompt-btn" @click="sendQuick('请帮我设计一堂课的完整教学方案，包含教学目标、教学过程和课堂活动')">
            <span class="qp-icon">📖</span>
            <span class="qp-text">生成完整教学方案</span>
          </button>
          <button class="quick-prompt-btn" @click="sendQuick('帮我生成一份教学PPT课件，包含封面、目录、正文和总结页')">
            <span class="qp-icon">📝</span>
            <span class="qp-text">生成PPT课件</span>
          </button>
          <button class="quick-prompt-btn" @click="sendQuick('请帮我设计一份互动式课堂活动，包含问题和评估方式')">
            <span class="qp-icon">🧬</span>
            <span class="qp-text">设计课堂活动</span>
          </button>
          <button class="quick-prompt-btn" @click="sendQuick('帮我写一份详细的教案文档，适合打印分发')">
            <span class="qp-icon">📊</span>
            <span class="qp-text">生成Word教案</span>
          </button>
        </div>
      </div>

      <div v-if="loading" class="chat-msg chat-msg--assistant">
        <div class="chat-msg__avatar">AI</div>
        <div class="chat-msg__typing"><span /><span /><span /></div>
      </div>
      <div ref="bottomRef" />
    </div>

    <div class="chat-input-area">
      <div class="chat-input-row">
        <textarea
          v-model="input"
          class="chat-input"
          placeholder="输入你的问题，按 Enter 发送，Shift+Enter 换行..."
          rows="2"
          :disabled="loading"
          @keydown="handleKeyDown"
        />
        <div class="chat-input-actions">
          <button v-if="loading" class="btn-stop" @click="$emit('stop')">停止</button>
          <button v-else class="btn btn-primary btn-sm" @click="handleSend" :disabled="!input.trim() || loading">发送</button>
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
import { ref, nextTick, watch, onMounted } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  messages: { type: Array, default: () => [] },
  loading: Boolean,
  intent: Object,
})
const emit = defineEmits(['send', 'generate', 'stop'])

const input = ref('')
const bottomRef = ref(null)
const apiOnline = ref(false)
const showQuickPromptsHidden = ref(false)

// ---- 健康检查 ----
async function checkHealth() {
  try {
    const resp = await fetch('/api/health')
    if (resp.ok) { apiOnline.value = true }
  } catch { apiOnline.value = false }
}

// ---- 关键词检测：判断用户是否想要导出文件 ----
function detectExportType(text) {
  const t = text.toLowerCase()
  if (/ppt|课件|幻灯片|演示文稿|powerpoint|presentation/.test(t)) return 'pptx'
  if (/教案|word|文档|docx|教学设计|方案|导学案|教学目标|教学方案/.test(t)) return 'docx'
  return null
}

// 根据当前 AI 消息索引，检查前一条用户消息是否触发导出类型
function getExportType(aiMsgIndex) {
  if (aiMsgIndex <= 0) return null
  const prevMsg = props.messages[aiMsgIndex - 1]
  if (prevMsg && prevMsg.role === 'user') {
    return detectExportType(prevMsg.content)
  }
  return null
}

// ---- 渲染 Markdown ----
function renderContent(c) {
  try { return marked.parse(c, { breaks: true }) } catch { return c }
}

function handleSend() {
  if (!input.value.trim() || props.loading) return
  showQuickPromptsHidden.value = true
  emit('send', input.value.trim())
  input.value = ''
}

function handleKeyDown(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
}

// 快捷按钮：填入预设文字并自动发送
function sendQuick(text) {
  showQuickPromptsHidden.value = true
  emit('send', text)
}

// 自动滚动到底部
watch(() => props.messages.length, () => nextTick(() => bottomRef.value?.scrollIntoView({ behavior: 'smooth' })))
watch(() => props.loading, (v) => { if (v) nextTick(() => bottomRef.value?.scrollIntoView({ behavior: 'smooth' })) })

onMounted(() => { checkHealth() })
</script>

<style scoped>
/* ========== 整体布局 ========== */
.chat-panel { display:flex; flex-direction:column; height:100%; overflow:hidden; }

/* ========== 头部状态 ========== */
.chat-header {
  display:flex; align-items:center; justify-content:space-between;
  padding:14px 28px; border-bottom:1px solid var(--border-ghost);
  background:rgba(6,10,20,0.50); backdrop-filter:var(--blur-md); -webkit-backdrop-filter:var(--blur-md);
  flex-shrink:0; min-height:56px;
}
.chat-header__title { font-size:16px; font-weight:700; color:var(--text-primary); }
.chat-header__status {
  font-size:12px; padding:4px 10px; border-radius:12px;
  background:var(--glass-sm); color:var(--text-tertiary); transition:all 0.2s;
}
.chat-header__status.status-ok { background:rgba(5,150,105,0.12); color:var(--success); }
.chat-header__status.status-error { background:rgba(220,38,38,0.10); color:#DC2626; }

/* ========== 消息列表 ========== */
.chat-messages {
  flex:1; overflow-y:auto; padding:20px 28px;
  display:flex; flex-direction:column; gap:16px;
}
.chat-msg { display:flex; gap:12px; max-width:85%; animation:fadeIn 0.3s ease; }
.chat-msg--user { align-self:flex-end; flex-direction:row-reverse; }
.chat-msg--assistant { align-self:flex-start; }
.chat-msg__avatar {
  width:36px; height:36px; border-radius:var(--r-sm); flex-shrink:0;
  display:flex; align-items:center; justify-content:center;
  font-size:11px; font-weight:700; font-family:var(--font-mono);
  background:var(--glass-sm); color:var(--text-tertiary); border:1px solid var(--border-ghost);
}
.chat-msg--assistant .chat-msg__avatar { background:var(--accent-glow); color:var(--accent); border-color:var(--border-accent); }
.chat-msg__body { min-width:0; }
.chat-msg__bubble {
  padding:14px 18px; border-radius:var(--r-lg); font-size:14px; line-height:1.75;
  color:var(--text-primary); background:var(--glass-sm);
  border:1px solid var(--border-ghost);
  backdrop-filter:var(--blur-sm); -webkit-backdrop-filter:var(--blur-sm);
}
.chat-msg--user .chat-msg__bubble { background:var(--accent-glow); border-color:var(--border-accent); }
.chat-msg__bubble :deep(p) { margin-bottom:8px; color:inherit; }
.chat-msg__bubble :deep(p:last-child) { margin-bottom:0; }
.chat-msg__bubble :deep(ul) { margin:8px 0; padding-left:20px; }
.chat-msg__bubble :deep(li) { margin-bottom:4px; }

/* ========== 快捷功能区 ========== */
.quick-prompts { align-self:flex-start; margin-left:48px; animation:fadeIn 0.4s ease; }
.quick-prompts__title { font-size:13px; color:var(--text-tertiary); margin-bottom:10px; padding-left:2px; }
.quick-prompt-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:10px; max-width:480px; }
.quick-prompt-btn {
  display:flex; align-items:center; gap:10px; padding:14px 16px;
  background:var(--glass-sm); border:1px solid var(--border-ghost); border-radius:var(--r-md);
  cursor:pointer; font-family:inherit; font-size:13px; color:var(--text-secondary);
  text-align:left; transition:all var(--t-fast) var(--ease-out);
  backdrop-filter:var(--blur-sm); -webkit-backdrop-filter:var(--blur-sm);
}
.quick-prompt-btn:hover {
  border-color:var(--border-glow); background:var(--glass-md);
  transform:translateY(-2px); box-shadow:0 4px 12px rgba(99,102,241,0.12);
}
.quick-prompt-btn:hover .qp-text { color:var(--accent); }
.qp-icon { font-size:20px; flex-shrink:0; }
.qp-text { font-weight:500; color:var(--text-secondary); transition:color 0.2s; }

/* ========== 下载按钮 ========== */
.export-buttons { display:flex; gap:8px; margin-top:12px; padding-top:12px; border-top:1px solid var(--border-ghost); flex-wrap:wrap; }
.btn-export {
  display:inline-flex; align-items:center; gap:6px;
  padding:7px 16px; border-radius:20px; font-size:13px; font-weight:500;
  cursor:pointer; border:1px solid; transition:all 0.2s; font-family:inherit;
}
.btn-export:disabled { opacity:0.5; cursor:wait; }
.btn-export-docx { background:rgba(5,150,105,0.08); color:var(--success); border-color:rgba(5,150,105,0.25); }
.btn-export-docx:hover:not(:disabled) { background:rgba(5,150,105,0.15); }
.btn-export-pptx { background:rgba(217,119,6,0.08); color:#D97706; border-color:rgba(217,119,6,0.25); }
.btn-export-pptx:hover:not(:disabled) { background:rgba(217,119,6,0.15); }

/* ========== 打字动画 ========== */
.chat-msg__typing { display:flex; gap:4px; padding:16px 20px; background:var(--glass-sm); border:1px solid var(--border-ghost); border-radius:var(--r-lg); }
.chat-msg__typing span { width:6px; height:6px; border-radius:50%; background:var(--text-tertiary); animation:typing-dot 1.4s ease-in-out infinite both; }
.chat-msg__typing span:nth-child(2) { animation-delay:0.2s; }
.chat-msg__typing span:nth-child(3) { animation-delay:0.4s; }

/* ========== 输入区 ========== */
.chat-input-area {
  padding:16px 24px; border-top:1px solid var(--border-ghost);
  background:rgba(6,10,20,0.50); backdrop-filter:var(--blur-md); -webkit-backdrop-filter:var(--blur-md);
  flex-shrink:0;
}
.chat-input-row { display:flex; gap:10px; align-items:flex-end; }
.chat-input {
  flex:1; resize:none; min-height:44px; max-height:120px; line-height:1.5;
  padding:10px 14px; border:1px solid var(--border-subtle); border-radius:var(--r-md);
  font-size:14px; font-family:inherit; color:var(--text-primary);
  background:var(--glass-sm); outline:none;
  backdrop-filter:var(--blur-sm); -webkit-backdrop-filter:var(--blur-sm);
  transition:border-color var(--t-fast) var(--ease-out);
}
.chat-input:focus { border-color:var(--accent); }
.chat-input::placeholder { color:var(--text-tertiary); }
.chat-input:disabled { opacity:0.5; }
.chat-input-actions { display:flex; gap:8px; padding-bottom:2px; flex-shrink:0; }
.btn-stop {
  height:44px; flex-shrink:0; display:flex; align-items:center; justify-content:center; gap:6px;
  padding:0 18px; background:rgba(220,38,38,0.12); color:#DC2626;
  border:1px solid rgba(220,38,38,0.25); border-radius:var(--r-sm);
  font-size:14px; font-weight:500; cursor:pointer; font-family:inherit; transition:all 0.2s;
}
.btn-stop:hover { background:rgba(220,38,38,0.20); }
.input-hints { margin-top:8px; font-size:12px; color:var(--text-tertiary); text-align:center; }
.chat-intent-bar { display:flex; align-items:center; justify-content:space-between; margin-top:10px; padding:0 2px; }

/* ========== 动画 ========== */
@keyframes fadeIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
@keyframes typing-dot { 0%,80%,100%{transform:scale(0.6);opacity:0.4} 40%{transform:scale(1);opacity:1} }
</style>
