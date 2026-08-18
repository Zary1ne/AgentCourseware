<template>
  <div class="workspace">
    <TaskSidebar />
    <div class="workspace__main">
      <div class="workspace__content">
        <KnowledgePanel v-show="currentStep === 0" :activeTask="activeTask" :taskId="activeTask.id" @file-uploaded="onFileUploaded" />
        <ChatPanel v-show="currentStep === 1" :messages="activeTask.messages" :loading="chatLoading" :intent="activeTask.intent" @send="onSendMessage" @generate="onGenerate" @stop="onStopChat" @new-session="onNewSession" @send-to-preview="onSendToPreview" />
        <PreviewPanel v-show="currentStep === 2" :files="activeTask.genFiles" :loading="genLoading" :external-slides="previewSlides" @revise="onRevise" />
      </div>
      <div class="workspace__bar">
        <div class="workspace__bar-left">
          <span v-if="currentStep === 0">上传参考资料 —— AI 会在对话中参考这些内容</span>
          <span v-else-if="currentStep === 1">{{ activeTask.messages.length }} 条消息<span v-if="activeTask.intent" class="workspace__intent">&nbsp;· 意图已确认</span></span>
          <span v-else>{{ fileCount }} 个文件就绪</span>
        </div>
        <div class="workspace__bar-right">
          <button v-if="currentStep > 0" class="btn btn-secondary btn-sm" @click="setStep(currentStep - 1)">上一步</button>
          <button v-if="currentStep < 2" class="btn btn-primary btn-sm" @click="setStep(currentStep + 1)" :disabled="currentStep === 1 && !activeTask.intent">
            {{ currentStep === 0 ? '开始对话' : currentStep === 1 ? '查看预览' : '' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, triggerRef } from 'vue'
import { useTaskStore } from '../composables/useTaskStore'
import TaskSidebar from '../components/TaskSidebar.vue'
import KnowledgePanel from '../components/KnowledgePanel.vue'
import ChatPanel from '../components/ChatPanel.vue'
import PreviewPanel from '../components/PreviewPanel.vue'
import { sendMessage, extractIntent, generateAll } from '../api'

const { activeTask, currentStep, setStep, triggerTaskUpdate } = useTaskStore()
const chatLoading = ref(false)
const genLoading = ref(false)
let abortController = null

// 用于强制触发消息列表更新
const messageTick = ref(0)

const fileCount = computed(() => Object.keys(activeTask.value.genFiles).length)

// 从对话端送入预览端的 slides 数据
const previewSlides = ref(null)

// 解析 AI 文本内容为 slides 结构
function parseContentToSlides(content, title) {
  const slides = []
  // 统一换行符
  const text = content.replace(/\\r\\n/g, '\n').replace(/\\n/g, '\n').replace(/\r\n/g, '\n')
  // 按空行分段
  const sections = text.trim().split(/\n\n+/)

  for (const section of sections) {
    const lines = section.split('\n').filter(l => l.trim())
    if (lines.length === 0) continue

    const firstLine = lines[0].trim()
    let kind = 'content'
    let slideTitle = firstLine
    let body = lines.slice(1).join('\n')

    // 识别【封面】、【目录】、【总结】等标记
    if (/【封面|【课题|【标题/.test(firstLine)) {
      kind = 'cover'
      slideTitle = firstLine.replace(/^【.+?】/, '').trim() || title
      body = lines.slice(1).join('\n')
    } else if (/【目录|【内容|【导览/.test(firstLine)) {
      kind = 'catalog'
      slideTitle = firstLine.replace(/^【.+?】/, '').trim() || '目录'
    } else if (/【总结|【回顾|【小结/.test(firstLine)) {
      kind = 'summary'
      slideTitle = firstLine.replace(/^【.+?】/, '').trim() || '总结'
    } else if (firstLine.startsWith('【')) {
      slideTitle = firstLine.replace(/^【.+?】/, '').trim() || firstLine
    }

    // 第一页如果没有识别为封面，但有标题感（行数少），设为封面
    if (slides.length === 0 && kind === 'content' && lines.length <= 3) {
      kind = 'cover'
    }

    slides.push({ kind, title: slideTitle || '未命名', body: body || '暂无内容' })
  }

  // 兜底：如果解析失败，把全部内容作为封面
  if (slides.length === 0) {
    slides.push({ kind: 'cover', title: title || '教学课件', body: content })
  }

  return slides
}

// 接收 ChatPanel 的「送入预览编辑」事件
function onSendToPreview({ content, title, exportType }) {
  previewSlides.value = parseContentToSlides(content, title)
  // 根据 exportType 设置课件类型提示（存入 activeTask 供 PreviewPanel 使用）
  if (exportType) {
    activeTask.value.previewType = exportType === 'docx' ? 'Word' : 'PPT'
  }
  setStep(2)  // 跳转到预览步骤
}

function onFileUploaded(result) {
  if (result.knowledge_base?.success) {
    activeTask.value.messages.push({ role:'assistant', content:'参考资料：**'+result.filename+'**（'+result.knowledge_base.chunks+' 块）', _id: Date.now() + '_file' })
  }
}

function onStopChat() { if (abortController) { abortController.abort(); abortController = null } chatLoading.value = false }

function onNewSession() {
  if (chatLoading.value) onStopChat()
  activeTask.value.messages = []
  activeTask.value.intent = null
  activeTask.value.genFiles = {}
  setStep(1)
}

// 从 AI 回复中剥离 JSON 意图块（支持嵌套 { }）
function stripIntentJson(text) {
  if (!text) return text
  let out = text
  out = out.replace(/\[INTENT_READY\]/g, '')
  // 去掉 ```json ... ``` 代码块
  out = out.replace(/```json[\s\S]*?```/g, '')
  // 寻找包含 "subject" 或 "topic" 键的顶层 JSON 对象
  const subjectRe = /"subject"\s*:/
  const topicRe = /"topic"\s*:/
  const stack = []
  let i = 0
  let found = null
  while (i < out.length) {
    const ch = out[i]
    if (ch === '{') {
      stack.push(i)
    } else if (ch === '}') {
      const start = stack.pop()
      if (stack.length === 0 && start !== undefined) {
        const candidate = out.slice(start, i + 1)
        if (subjectRe.test(candidate) || topicRe.test(candidate)) {
          try {
            const parsed = JSON.parse(candidate)
            if (parsed && (parsed.subject || parsed.topic)) {
              found = { start, end: i + 1, parsed }
              break
            }
          } catch {}
        }
      }
    }
    i++
  }
  if (found) {
    if (found.parsed) activeTask.value.intent = found.parsed
    out = out.slice(0, found.start) + out.slice(found.end)
  }
  return out
}

// 智能合并：将流式输出中被意外切断的句子合并（行末无标点视为续行），保留合法的段落/列表换行
function normalizeContent(text) {
  if (!text) return ''
  let t = text.replace(/\r\n/g, '\n')
  // 将字面 \n 转换为真正的换行符
  t = t.replace(/\\r\\n/g, '\n').replace(/\\n/g, '\n')
  t = t.replace(/\[DONE\]/g, '').trim()
  t = stripIntentJson(t)
  t = t.replace(/\n{3,}/g, '\n\n')

  const lines = t.split('\n')
  const out = []
  const isListStart = (s) => /^\s*(?:\d+[\.、)）]|[·•\-—*])/.test(s) || /^\s*[一二三四五六七八九十]+[、)]/.test(s)
  const isSentenceEnd = (s) => /[。！？!?；;…]$/.test(s.trim())
  const isStructuralLine = (s) => /^[-*·•\u2014]\s*$/.test(s.trim()) || /^```/.test(s.trim())
  // 行末冒号 + 紧跟的下一行首字符是小写/中文 → 很可能是列表项的换行续行
  const isColonEnd = (s) => /[：:]$/.test(s.trim())

  let i = 0
  while (i < lines.length) {
    const line = lines[i]
    const trimmed = line.trim()
    if (trimmed === '') {
      out.push('')
      i++
      continue
    }

    const nextLine = i + 1 < lines.length ? lines[i + 1] : null
    const nextTrim = nextLine ? nextLine.trim() : ''

    // 结构性行 → 保留换行
    if (isStructuralLine(line)) {
      out.push(line)
      i++
      continue
    }

    // 列表项开头
    if (isListStart(line)) {
      // 列表项 + 以句末标点结束 → 保留
      if (isSentenceEnd(line)) {
        out.push(line)
        i++
        continue
      }
      // 列表项 + 以冒号结尾 + 下一行是列表项 → 保留当前，继续
      if (isColonEnd(line) && nextLine && isListStart(nextLine)) {
        out.push(line)
        i++
        continue
      }
      // 列表项 + 以冒号结尾 + 下一行不是列表项 → 合并（续行）
      if (isColonEnd(line)) {
        let merged = trimmed
        i++
        while (i < lines.length) {
          const n = lines[i]
          const nt = n.trim()
          if (nt === '' || isListStart(n) || isStructuralLine(n)) break
          merged += nt
          i++
          if (isSentenceEnd(merged)) break
        }
        out.push(merged)
        continue
      }
      // 列表项不以句末/冒号结尾 → 合并
      if (!isSentenceEnd(line)) {
        let merged = trimmed
        i++
        while (i < lines.length) {
          const n = lines[i]
          const nt = n.trim()
          if (nt === '' || isListStart(n) || isStructuralLine(n)) break
          merged += nt
          i++
          if (isSentenceEnd(merged)) break
        }
        out.push(merged)
        continue
      }
      out.push(line)
      i++
      continue
    }

    // 非列表项：以句末标点结束 → 保留换行
    if (isSentenceEnd(line)) {
      out.push(line)
      i++
      continue
    }

    // 非列表项：合并到句末标点或空行
    let merged = trimmed
    i++
    while (i < lines.length) {
      const n = lines[i]
      const nt = n.trim()
      if (nt === '' || isListStart(n) || isStructuralLine(n)) break
      merged += nt
      i++
      if (isSentenceEnd(merged)) break
    }
    out.push(merged)
  }
  return out.join('\n').replace(/\n{3,}/g, '\n\n').trim()
}

async function onSendMessage(text, promptType = '') {
  if (!text.trim() || chatLoading.value) return
  activeTask.value.messages.push({ role:'user', content:text, _id: Date.now() + '_user' })
  chatLoading.value = true; abortController = new AbortController()
  try {
    const response = await sendMessage(activeTask.value.messages.map(m=>({role:m.role,content:m.content})), true, abortController.signal, promptType)
    if (!response.ok) throw new Error('请求失败')
    // 用 reactive 创建：push 后本地变量与数组内是同一个代理，
    // 后续 content += 才能触发视图更新（否则流式期间界面不刷新，结束时一次性弹出）
    const assistantMsg = reactive({ role:'assistant', content:'', _id: Date.now() + '_ai' }); activeTask.value.messages.push(assistantMsg)
    const reader = response.body.getReader(); const decoder = new TextDecoder()
    let buffer = ''
    let eventDataLines = []
    let eventType = 'message'

    let intentReadyFlag = false

    function flushEvent() {
      if (eventDataLines.length === 0) return
      const dataStr = eventDataLines.join('\n')
      eventDataLines = []
      if (eventType === 'intents') {
        try { activeTask.value.intent = JSON.parse(dataStr) } catch {}
        return
      }
      if (eventType === 'done' || dataStr === '[DONE]') return
      if (intentReadyFlag) return

      // sse_starlette 输出格式：
      // - message 事件 data 是纯文本（后端 yield {"data": chunk}，chunk 已是字符串）
      // - intents/intent 事件 data 是 JSON 字符串
      // - done 事件 data 是 "[DONE]"
      let textChunk = ''
      if (eventType === 'message') {
        // 直接作为文本追加，sse_starlette 不做 JSON 编码
        textChunk = dataStr
      } else if (eventType === 'intent') {
        try { activeTask.value.intent = JSON.parse(dataStr) } catch {}
        return
      } else {
        textChunk = dataStr
      }

      if (textChunk.includes('[INTENT_READY]')) {
        intentReadyFlag = true
        textChunk = textChunk.slice(0, textChunk.indexOf('[INTENT_READY]'))
      }

      if (textChunk) {
        assistantMsg.content += textChunk
        triggerTaskUpdate()
      }
    }

    while (true) {
      const { done, value } = await reader.read(); if (done) break
      buffer += decoder.decode(value, { stream:true })
      // sse_starlette uses \r\n (CRLF) as separator, normalize to \n first
      buffer = buffer.replace(/\r\n/g, '\n')
      const parts = buffer.split('\n')
      buffer = parts.pop() || ''
      for (const line of parts) {
        if (line === '') {
          flushEvent()
        } else if (line.startsWith('event:')) {
          eventType = line.slice(6).trim()
        } else if (line.startsWith('data:')) {
          eventDataLines.push(line.slice(5).trimStart())
        }
      }
    }
    flushEvent()

    // 最终清理：剥离 JSON 意图块 + 规范排版
    assistantMsg.content = normalizeContent(assistantMsg.content)
  } catch (e) { if (e.name !== 'AbortError') activeTask.value.messages.push({ role:'assistant', content:'错误：'+e.message, _id: Date.now() + '_err' }) }
  finally { chatLoading.value = false; abortController = null }
}

async function onGenerate() {
  if (!activeTask.value.intent) {
    try {
      const res = await extractIntent(activeTask.value.messages.map(m=>({role:m.role,content:m.content})))
      if (res.data?.intent) { activeTask.value.intent = res.data.intent; activeTask.value.messages.push({ role:'assistant', content:'已从对话中提取教学意图，正在生成课件...', _id: Date.now() + '_intent' }) }
    } catch { activeTask.value.messages.push({ role:'assistant', content:'无法提取教学意图，请在对话中更详细地描述教学需求后再试。', _id: Date.now() + '_intent_err' }); return }
  }
  genLoading.value = true
  try {
    const res = await generateAll(activeTask.value.intent)
    activeTask.value.genFiles = res.data.files || {}
    activeTask.value.messages.push({ role:'assistant', content:'课件已生成。正在跳转到预览页...', _id: Date.now() + '_gen' })
    setStep(2)
  } catch (e) { activeTask.value.messages.push({ role:'assistant', content:'生成失败：'+(e.response?.data?.detail||e.message), _id: Date.now() + '_gen_err' }) }
  finally { genLoading.value = false }
}

function onRevise(instruction) { activeTask.value.messages.push({ role:'user', content:instruction, _id: Date.now() + '_user' }); onSendMessage(instruction) }
</script>

<style scoped>
.workspace { display:flex; height:100vh; overflow:hidden; background:var(--bg-page); }
.workspace__main { flex:1; min-width:0; display:flex; flex-direction:column; }
.workspace__content { flex:1; overflow:hidden; display:flex; flex-direction:column; }
.workspace__bar { display:flex; align-items:center; justify-content:space-between; padding:14px 28px; border-top:1px solid var(--border-ghost); background:rgba(6,10,20,0.55); backdrop-filter:var(--blur-md); -webkit-backdrop-filter:var(--blur-md); flex-shrink:0; gap:16px; }
.workspace__bar-left { flex:1; min-width:0; font-size:13px; color:var(--text-tertiary); font-family:var(--font-mono); }
.workspace__intent { color:var(--success); font-weight:600; }
.workspace__bar-right { display:flex; gap:10px; flex-shrink:0; }
</style>