import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

const STORAGE_PREFIX = 'teaching_agent_tasks'

function getStorageKey() {
  try {
    const info = sessionStorage.getItem('loginInfo')
    if (!info) return STORAGE_PREFIX + '_anonymous'
    const loginInfo = JSON.parse(info)
    return STORAGE_PREFIX + '_' + (loginInfo.userId || loginInfo.username || 'anonymous')
  } catch { return STORAGE_PREFIX + '_anonymous' }
}

function getCurrentUserId() {
  try {
    const info = sessionStorage.getItem('loginInfo')
    if (!info) return ''
    return JSON.parse(info).userId || ''
  } catch { return '' }
}

function makeTask(name = '') {
  return {
    id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
    name: name || '新任务',
    createdAt: new Date().toISOString(),
    docs: [],
    messages: [{ role: 'assistant', content: '你好，我是 AI 教学智能助手。\n\n请告诉我你想准备的课程信息。' }],
    intent: null,
    genFiles: {},
  }
}

export const useTaskStore = defineStore('task', () => {
  const tasks = ref([])
  const activeTaskId = ref(null)
  const currentStep = ref(0)

  const activeTask = computed(() => tasks.value.find(t => t.id === activeTaskId.value) || tasks.value[0])

  function saveTasks() {
    try {
      localStorage.setItem(getStorageKey(), JSON.stringify({ tasks: tasks.value, activeTaskId: activeTaskId.value }))
    } catch {}
  }

  function loadTasks() {
    try {
      const raw = localStorage.getItem(getStorageKey())
      if (raw) {
        const data = JSON.parse(raw)
        tasks.value = data.tasks || []
        activeTaskId.value = data.activeTaskId || null
      }
    } catch {}
  }

  function createTask(name) {
    const t = makeTask(name)
    tasks.value.unshift(t)
    activeTaskId.value = t.id
    saveTasks()
    return t
  }

  function switchTask(id) { activeTaskId.value = id; saveTasks() }

  function deleteTask(id) {
    const idx = tasks.value.findIndex(t => t.id === id); if (idx === -1) return
    tasks.value.splice(idx, 1)
    if (activeTaskId.value === id) {
      if (tasks.value.length > 0) activeTaskId.value = tasks.value[0].id
      else { const t = makeTask(); tasks.value.push(t); activeTaskId.value = t.id }
    }
    saveTasks()
  }

  function renameTask(id, name) {
    const t = tasks.value.find(t => t.id === id)
    if (t) { t.name = name; saveTasks() }
  }

  function setStep(n) { if (n >= 0 && n <= 2) currentStep.value = n }

  // Pinia 深响应式自动追踪状态变更，此处保留以兼容旧调用方
  function triggerTaskUpdate() {}

  loadTasks()
  if (tasks.value.length === 0) {
    const t = makeTask(); tasks.value.push(t); activeTaskId.value = t.id; saveTasks()
  }

  watch(tasks, saveTasks, { deep: true })

  return { tasks, activeTaskId, currentStep, activeTask, setStep, createTask, switchTask, deleteTask, renameTask, getCurrentUserId, triggerTaskUpdate }
})
