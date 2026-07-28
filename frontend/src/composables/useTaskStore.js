import { ref, computed, watch } from 'vue'

const STORAGE_KEY = 'teaching_agent_tasks'

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

const tasks = ref([])
const activeTaskId = ref(null)
const currentStep = ref(0)

function loadTasks() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) { const data = JSON.parse(raw); tasks.value = data.tasks || []; activeTaskId.value = data.activeTaskId || null }
  } catch {}
}

function saveTasks() {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify({ tasks: tasks.value, activeTaskId: activeTaskId.value })) } catch {}
}

loadTasks()
if (tasks.value.length === 0) {
  const t = makeTask(); tasks.value.push(t); activeTaskId.value = t.id; saveTasks()
}

const activeTask = computed(() => tasks.value.find(t => t.id === activeTaskId.value) || tasks.value[0])

function createTask(name) { const t = makeTask(name); tasks.value.unshift(t); activeTaskId.value = t.id; saveTasks(); return t }
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
function renameTask(id, name) { const t = tasks.value.find(t => t.id === id); if (t) { t.name = name; saveTasks() } }
function setStep(n) { if (n >= 0 && n <= 2) currentStep.value = n }

watch(tasks, saveTasks, { deep: true })

export function useTaskStore() {
  return { tasks, activeTaskId, activeTask, currentStep, setStep, createTask, switchTask, deleteTask, renameTask }
}