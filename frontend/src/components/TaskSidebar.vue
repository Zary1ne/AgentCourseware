<template>
  <aside class="task-sidebar">
    <div class="task-sidebar__head">
      <span class="task-sidebar__title">任务列表</span>
      <button class="task-sidebar__add" @click="handleCreateTask()" title="新建任务">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
      </button>
    </div>
    <div class="task-sidebar__list">
      <div v-for="t in tasks" :key="t.id" :class="['task-item', { 'task-item--active': t.id === activeTaskId }]" @click="switchTask(t.id)">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="task-item__icon"><rect x="1" y="1" width="14" height="14" rx="3" stroke="currentColor" stroke-width="1.1"/><path d="M5 7h6M5 10h4" stroke="currentColor" stroke-width="0.7" stroke-linecap="round"/></svg>
        <input v-if="editingId === t.id" class="task-item__input" v-model="editName" @blur="confirmRename(t.id)" @keydown.enter="confirmRename(t.id)" @keydown.escape="cancelRename" @click.stop autofocus />
        <span v-else class="task-item__name" @dblclick="startRename(t)">{{ t.name }}</span>
        <div class="task-item__actions">
          <button v-if="editingId !== t.id" class="task-item__rename" @click.stop="startRename(t)" title="重命名">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M8.5 1.5l2 2-6 6-2.5.5.5-2.5 6-6z" stroke="currentColor" stroke-width="1" stroke-linejoin="round"/><line x1="7.5" y1="2.5" x2="9.5" y2="4.5" stroke="currentColor" stroke-width="1"/></svg>
          </button>
          <button class="task-item__delete" @click.stop="deleteTask(t.id)" title="删除">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M9 3L3 9M3 3l6 6" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
          </button>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useTaskStore } from '../stores/taskStore'
const store = useTaskStore()
const { tasks, activeTaskId } = storeToRefs(store)
const { switchTask, createTask, deleteTask, renameTask } = store
const editingId = ref(null)
const editName = ref('')

function handleCreateTask() {
  const t = createTask()  // 使用默认名称创建
  // 立即进入重命名模式
  editingId.value = t.id
  editName.value = t.name
  // 下一帧自动聚焦输入框
  nextTick(() => {
    const input = document.querySelector(`.task-item--active .task-item__input`)
    if (input) {
      input.focus()
      input.select()
    }
  })
}

function startRename(t) { editingId.value = t.id; editName.value = t.name }
function cancelRename() { editingId.value = null; editName.value = '' }
function confirmRename(id) { if (editName.value.trim()) renameTask(id, editName.value.trim()); editingId.value = null; editName.value = '' }
</script>

<style scoped>
.task-sidebar { width:248px; min-width:248px; display:flex; flex-direction:column; overflow:hidden; background:rgba(6,10,20,0.60); backdrop-filter:var(--blur-lg); -webkit-backdrop-filter:var(--blur-lg); border-right:1px solid var(--border-ghost); }
.task-sidebar__head { display:flex; align-items:center; justify-content:space-between; padding:18px 20px; border-bottom:1px solid var(--border-ghost); }
.task-sidebar__title { font-size:11px; font-weight:600; letter-spacing:0.08em; color:var(--text-tertiary); font-family:var(--font-mono); text-transform:uppercase; }
.task-sidebar__add { display:flex; align-items:center; justify-content:center; width:28px; height:28px; border-radius:var(--r-sm); background:transparent; border:1px solid var(--border-ghost); color:var(--text-tertiary); cursor:pointer; transition:all var(--t-fast) var(--ease-out); }
.task-sidebar__add:hover { background:var(--accent-glow); border-color:var(--border-accent); color:var(--accent); }
.task-sidebar__list { flex:1; overflow-y:auto; padding:8px 10px; }
.task-item { display:flex; align-items:center; gap:10px; padding:10px 12px; border-radius:var(--r-md); cursor:pointer; transition:all var(--t-fast) var(--ease-out); color:var(--text-secondary); }
.task-item:hover { background:var(--glass-sm); color:var(--text-primary); }
.task-item--active { background:var(--accent-glow); color:var(--accent); border:1px solid var(--border-accent); }
.task-item__icon { flex-shrink:0; opacity:0.4; }
.task-item--active .task-item__icon { opacity:0.8; }
.task-item__name { flex:1; min-width:0; font-size:13px; font-weight:500; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.task-item__actions { display:flex; align-items:center; gap:2px; opacity:0; transition:opacity var(--t-fast) var(--ease-out); }
.task-item:hover .task-item__actions, .task-item--active .task-item__actions { opacity:1; }
.task-item__rename { display:flex; align-items:center; justify-content:center; width:22px; height:22px; border-radius:var(--r-xs); background:transparent; border:none; color:var(--text-tertiary); cursor:pointer; transition:all var(--t-fast) var(--ease-out); flex-shrink:0; }
.task-item__rename:hover { background:var(--accent-glow); color:var(--accent)!important; }
.task-item__input { flex:1; min-width:0; font-size:13px; font-weight:500; padding:2px 0; background:transparent; border:none; border-bottom:1px solid var(--accent); color:var(--text-primary); outline:none; font-family:inherit; }
.task-item__delete { display:flex; align-items:center; justify-content:center; width:22px; height:22px; border-radius:var(--r-xs); background:transparent; border:none; color:var(--text-tertiary); cursor:pointer; transition:all var(--t-fast) var(--ease-out); flex-shrink:0; }
.task-item__delete:hover { background:rgba(240,112,112,0.12); color:var(--error)!important; }
</style>