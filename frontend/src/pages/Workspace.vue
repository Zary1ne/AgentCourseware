<template>
  <div class="workspace">
    <TaskSidebar />
    <div class="workspace__main">
      <div class="workspace__content">
        <KnowledgePanel v-show="currentStep === 0" :activeTask="activeTask" :taskId="activeTask.id" @file-uploaded="onFileUploaded" />
        <ChatPanel v-show="currentStep === 1" :messages="activeTask.messages" :loading="chatLoading" :intent="activeTask.intent" @send="onSendMessage" @generate="onGenerate" @stop="onStopChat" />
        <PreviewPanel v-show="currentStep === 2" :files="activeTask.genFiles" :loading="genLoading" @revise="onRevise" />
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
import { ref, computed } from 'vue'
import { useTaskStore } from '../composables/useTaskStore'
import TaskSidebar from '../components/TaskSidebar.vue'
import KnowledgePanel from '../components/KnowledgePanel.vue'
import ChatPanel from '../components/ChatPanel.vue'
import PreviewPanel from '../components/PreviewPanel.vue'
import { sendMessage, extractIntent, generateAll } from '../api'

const { activeTask, currentStep, setStep } = useTaskStore()
const chatLoading = ref(false)
const genLoading = ref(false)
let abortController = null

const fileCount = computed(() => Object.keys(activeTask.value.genFiles).length)

function onFileUploaded(result) {
  if (result.knowledge_base?.success) {
    activeTask.value.messages.push({ role:'assistant', content:'参考资料：**'+result.filename+'**（'+result.knowledge_base.chunks+' 块）' })
  }
}

function onStopChat() { if (abortController) { abortController.abort(); abortController = null } chatLoading.value = false }

async function onSendMessage(text) {
  if (!text.trim() || chatLoading.value) return
  activeTask.value.messages.push({ role:'user', content:text })
  chatLoading.value = true; abortController = new AbortController()
  try {
    const response = await sendMessage(activeTask.value.messages.map(m=>({role:m.role,content:m.content})), true, abortController.signal)
    if (!response.ok) throw new Error('请求失败')
    const assistantMsg = { role:'assistant', content:'' }; activeTask.value.messages.push(assistantMsg)
    const reader = response.body.getReader(); const decoder = new TextDecoder(); let buffer = ''
    while (true) {
      const { done, value } = await reader.read(); if (done) break
      buffer += decoder.decode(value, { stream:true })
      const lines = buffer.split('\n'); buffer = lines.pop() || ''
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6); if (data === '[DONE]') continue
          try { const p = JSON.parse(data); if (typeof p === 'string') assistantMsg.content += p; else activeTask.value.intent = p }
          catch { assistantMsg.content += data }
        }
      }
    }
    if (assistantMsg.content.includes('[INTENT_READY]')) {
      assistantMsg.content = assistantMsg.content.replace('[INTENT_READY]','')
      const m = assistantMsg.content.match(/\{[\s\S]*?"subject"\s*:\s*"[^"]*"[\s\S]*?\}/)
      if (m) { try { activeTask.value.intent = JSON.parse(m[0]); assistantMsg.content = assistantMsg.content.replace(m[0],'') } catch {} }
    }
    assistantMsg.content = assistantMsg.content.trim()
  } catch (e) { if (e.name !== 'AbortError') activeTask.value.messages.push({ role:'assistant', content:'错误：'+e.message }) }
  finally { chatLoading.value = false; abortController = null }
}

async function onGenerate() {
  if (!activeTask.value.intent) {
    try {
      const res = await extractIntent(activeTask.value.messages.map(m=>({role:m.role,content:m.content})))
      if (res.data?.intent) { activeTask.value.intent = res.data.intent; activeTask.value.messages.push({ role:'assistant', content:'已从对话中提取教学意图，正在生成课件...' }) }
    } catch { activeTask.value.messages.push({ role:'assistant', content:'无法提取教学意图，请在对话中更详细地描述教学需求后再试。' }); return }
  }
  genLoading.value = true
  try {
    const res = await generateAll(activeTask.value.intent)
    activeTask.value.genFiles = res.data.files || {}
    activeTask.value.messages.push({ role:'assistant', content:'课件已生成。正在跳转到预览页...' })
    setStep(2)
  } catch (e) { activeTask.value.messages.push({ role:'assistant', content:'生成失败：'+(e.response?.data?.detail||e.message) }) }
  finally { genLoading.value = false }
}

function onRevise(instruction) { activeTask.value.messages.push({ role:'user', content:instruction }); onSendMessage(instruction) }
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