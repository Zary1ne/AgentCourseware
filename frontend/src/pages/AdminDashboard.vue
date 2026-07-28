<template>
  <div class="admin">
    <header class="admin-header">
      <h2>管理后台</h2>
      <span class="text-tertiary">系统状态概览</span>
    </header>
    <div class="admin-grid">
      <div class="admin-card"><span class="admin-card__label">API 状态</span><span class="admin-card__value">{{ loading ? '—' : '在线' }}</span></div>
      <div class="admin-card"><span class="admin-card__label">活跃会话</span><span class="admin-card__value">{{ loading ? '—' : stats?.active_sessions ?? stats?.task_count ?? '—' }}</span></div>
      <div class="admin-card"><span class="admin-card__label">知识文档</span><span class="admin-card__value">{{ loading ? '—' : stats?.document_count ?? '—' }}</span></div>
      <div class="admin-card"><span class="admin-card__label">LLM 模型</span><span class="admin-card__value">{{ loading ? '—' : stats?.model ?? 'DeepSeek' }}</span></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAdminStats } from '../api'
const stats = ref(null)
const loading = ref(true)
onMounted(async () => { try { stats.value = (await getAdminStats()).data } catch {}; loading.value = false })
</script>

<style scoped>
.admin { padding:40px; max-width:var(--max-width); margin:0 auto; min-height:100vh; }
.admin-header { margin-bottom:40px; }
.admin-header h2 { font-size:28px; font-weight:700; letter-spacing:-0.025em; color:var(--text-primary); margin-bottom:6px; }
.admin-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:14px; }
.admin-card { background:var(--glass-sm); border:1px solid var(--border-ghost); border-radius:var(--r-lg); backdrop-filter:var(--blur-md); -webkit-backdrop-filter:var(--blur-md); padding:28px 24px; display:flex; flex-direction:column; gap:8px; transition:all var(--t-fast) var(--ease-out); }
.admin-card:hover { background:var(--glass-md); border-color:var(--border-subtle); }
.admin-card__label { font-size:13px; font-weight:500; color:var(--text-secondary); letter-spacing:0.03em; }
.admin-card__value { font-size:32px; font-weight:700; color:var(--text-primary); letter-spacing:-0.03em; }
</style>