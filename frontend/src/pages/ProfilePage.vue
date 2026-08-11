<template>
  <div class="profile-page">
    <header class="profile-header">
      <div class="profile-header__inner">
        <div class="profile-avatar">{{ userInitial }}</div>
        <div class="profile-info">
          <h2>{{ userInfo.username }}</h2>
          <p class="text-secondary">注册时间：{{ formatDate(userInfo.created_at) }}</p>
        </div>
        <div class="profile-stats">
          <div class="stat-item">
            <span class="stat-value">{{ userInfo.stats?.generations || 0 }}</span>
            <span class="stat-label">生成课件</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ userInfo.stats?.uploads || 0 }}</span>
            <span class="stat-label">社区上传</span>
          </div>
        </div>
      </div>
    </header>

    <div class="profile-content">
      <!-- 左侧：消息中心 -->
      <section class="profile-section messages-section">
        <div class="section-head">
          <h3>消息中心</h3>
          <div class="section-head__actions">
            <span v-if="unreadCount > 0" class="badge badge-error">{{ unreadCount }} 条未读</span>
            <button v-if="unreadCount > 0" class="btn btn-ghost btn-sm" @click="markAllRead">全部已读</button>
            <label class="filter-check">
              <input type="checkbox" v-model="unreadOnly" @change="fetchNotifications" />
              <span>仅未读</span>
            </label>
          </div>
        </div>

        <div v-if="loadingMsg" class="msg-loading">
          <span class="spinner"></span>
          <span class="text-tertiary">加载中...</span>
        </div>

        <div v-else-if="notifications.length === 0" class="msg-empty">
          <svg width="40" height="40" viewBox="0 0 40 40" fill="none" class="msg-empty-icon">
            <rect x="4" y="6" width="32" height="28" rx="4" stroke="currentColor" stroke-width="1.2"/>
            <path d="M12 16h16M12 22h12" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
          </svg>
          <p class="text-tertiary">暂无消息</p>
        </div>

        <div v-else class="msg-list">
          <div v-for="msg in notifications" :key="msg.id" :class="['msg-item', { 'msg-item--unread': !msg.read }]" @click="openMsg(msg)">
            <div class="msg-item__dot" v-if="!msg.read"></div>
            <div class="msg-item__content">
              <div class="msg-item__head">
                <span class="msg-item__title">{{ msg.title }}</span>
                <span class="msg-item__time">{{ formatTime(msg.created_at) }}</span>
              </div>
              <p class="msg-item__body">{{ msg.content }}</p>
              <span :class="['badge', getMsgBadgeClass(msg.type)]">{{ getMsgTypeLabel(msg.type) }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 右侧：我的上传 -->
      <section class="profile-section uploads-section">
        <div class="section-head">
          <h3>我的上传</h3>
        </div>

        <div v-if="loadingUploads" class="msg-loading">
          <span class="spinner"></span>
          <span class="text-tertiary">加载中...</span>
        </div>

        <div v-else-if="myUploads.length === 0" class="msg-empty">
          <svg width="40" height="40" viewBox="0 0 40 40" fill="none" class="msg-empty-icon">
            <path d="M20 12v16M12 20h16" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            <rect x="4" y="4" width="32" height="32" rx="6" stroke="currentColor" stroke-width="1.2"/>
          </svg>
          <p class="text-tertiary">暂无上传</p>
        </div>

        <div v-else class="upload-list">
          <div v-for="item in myUploads" :key="item.id" class="upload-item">
            <div class="upload-item__info">
              <span class="upload-item__title">{{ item.title }}</span>
              <span class="upload-item__cat">{{ item.category }}</span>
            </div>
            <span :class="['badge', getStatusBadge(item.status)]">{{ getStatusLabel(item.status) }}</span>
          </div>
        </div>
      </section>
    </div>

    <!-- 消息详情弹窗 -->
    <Teleport to="body">
      <div v-if="selectedMsg" class="modal-overlay" @click.self="selectedMsg = null">
        <div class="modal-content modal-msg">
          <div class="modal-header">
            <h3>{{ selectedMsg.title }}</h3>
            <button class="modal-close" @click="selectedMsg = null">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M12 4L4 12M4 4l8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
            </button>
          </div>
          <div class="modal-body">
            <p class="modal-msg-time">{{ formatTime(selectedMsg.created_at) }}</p>
            <p class="modal-msg-content">{{ selectedMsg.content }}</p>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 浮动反馈按钮 -->
    <button class="fab-feedback" @click="showFeedback = true" title="提交反馈">
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path d="M3 4h14v10H7.5L4 17V4z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
        <path d="M6.5 8h7M6.5 11h5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
      </svg>
    </button>

    <!-- 反馈弹窗 -->
    <Teleport to="body">
      <div v-if="showFeedback" class="modal-overlay" @click.self="showFeedback = false">
        <div class="modal-content" style="max-width:500px">
          <div class="modal-header">
            <h3>提交反馈</h3>
            <button class="modal-close" @click="showFeedback = false">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M12 4L4 12M4 4l8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="field">
              <label class="field-label">反馈类型</label>
              <select v-model="fbForm.type" class="field-input field-select">
                <option value="bug">Bug 报告</option>
                <option value="feature">功能建议</option>
                <option value="improvement">改进意见</option>
                <option value="other">其他</option>
              </select>
            </div>
            <div class="field">
              <label class="field-label">标题</label>
              <input v-model="fbForm.title" class="field-input" placeholder="请简要描述" maxlength="100" />
            </div>
            <div class="field">
              <label class="field-label">详细描述</label>
              <textarea v-model="fbForm.content" class="field-input field-textarea" rows="4" placeholder="请详细描述您遇到的问题或建议..."></textarea>
            </div>
            <p v-if="fbSuccess" class="fb-success">✅ 反馈已提交，感谢您的建议！</p>
            <p v-if="fbError" class="fb-error">{{ fbError }}</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showFeedback = false">{{ fbSuccess ? '关闭' : '取消' }}</button>
            <button v-if="!fbSuccess" class="btn btn-primary" @click="handleSubmitFeedback" :disabled="fbSubmitting">
              {{ fbSubmitting ? '提交中...' : '提交反馈' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getNotifications, markAllNotificationsRead, markNotificationRead, getMyCourseware, getUserInfo, submitFeedback } from '../api'

const router = useRouter()

const userInfo = ref({ username: '用户', stats: {}, created_at: '' })
const notifications = ref([])
const myUploads = ref([])
const loadingMsg = ref(true)
const loadingUploads = ref(true)
const unreadOnly = ref(false)
const selectedMsg = ref(null)
const showFeedback = ref(false)
const fbSubmitting = ref(false)
const fbSuccess = ref(false)
const fbError = ref('')
const fbForm = ref({ type: 'bug', title: '', content: '' })

const userInitial = computed(() => (userInfo.value.username || 'U')[0].toUpperCase())

const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)

function getUserId() {
  try {
    const info = sessionStorage.getItem('loginInfo')
    if (!info) { router.push('/login'); return '' }
    return JSON.parse(info).userId || ''
  } catch { return '' }
}

function formatDate(iso) {
  if (!iso) return '—'
  try { return new Date(iso).toLocaleDateString('zh-CN') } catch { return iso }
}

function formatTime(iso) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    return `${d.getMonth()+1}-${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
  } catch { return '' }
}

function getMsgBadgeClass(type) {
  const map = { review_result: 'badge-accent', new_courseware: 'badge-warning', system: 'badge-default' }
  return map[type] || 'badge-default'
}

function getMsgTypeLabel(type) {
  const map = { review_result: '审核结果', new_courseware: '新上传', system: '系统通知' }
  return map[type] || '通知'
}

function getStatusBadge(status) {
  const map = { pending: 'badge-warning', approved: 'badge-success', rejected: 'badge-error' }
  return map[status] || 'badge-default'
}

function getStatusLabel(status) {
  const map = { pending: '审核中', approved: '已上架', rejected: '未通过' }
  return map[status] || status
}

async function fetchUserInfo() {
  const uid = getUserId()
  if (!uid) return
  try {
    const res = await getUserInfo(uid)
    userInfo.value = res.data.user
  } catch {}
}

async function fetchNotifications() {
  const uid = getUserId()
  if (!uid) return
  loadingMsg.value = true
  try {
    const res = await getNotifications(uid, unreadOnly.value)
    notifications.value = res.data.notifications || []
  } catch { notifications.value = [] }
  finally { loadingMsg.value = false }
}

async function fetchMyUploads() {
  const uid = getUserId()
  if (!uid) return
  loadingUploads.value = true
  try {
    const res = await getMyCourseware(uid)
    myUploads.value = res.data.items || []
  } catch { myUploads.value = [] }
  finally { loadingUploads.value = false }
}

async function openMsg(msg) {
  selectedMsg.value = msg
  if (!msg.read) {
    try {
      await markNotificationRead(msg.id)
      msg.read = true
    } catch {}
  }
}

async function handleSubmitFeedback() {
  fbError.value = ''
  fbSuccess.value = false
  if (!fbForm.value.title.trim()) { fbError.value = '请输入标题'; return }
  if (!fbForm.value.content.trim()) { fbError.value = '请输入详细描述'; return }
  fbSubmitting.value = true
  try {
    const uid = getUserId()
    await submitFeedback({ user_id: uid, type: fbForm.value.type, title: fbForm.value.title.trim(), content: fbForm.value.content.trim() })
    fbSuccess.value = true
    fbForm.value = { type: 'bug', title: '', content: '' }
  } catch (e) { fbError.value = e.response?.data?.detail || '提交失败，请重试' }
  finally { fbSubmitting.value = false }
}

async function markAllRead() {
  const uid = getUserId()
  if (!uid) return
  try {
    await markAllNotificationsRead(uid)
    notifications.value.forEach(n => n.read = true)
  } catch {}
}

onMounted(() => {
  fetchUserInfo()
  fetchNotifications()
  fetchMyUploads()
})
</script>

<style scoped>
.profile-page { min-height: 100vh; background: var(--bg-page); }
.profile-header { background: var(--bg-navy); border-bottom: 1px solid var(--border-light); }
.profile-header__inner { max-width: var(--max-width); margin: 0 auto; padding: 40px; display: flex; align-items: center; gap: 24px; }
.profile-avatar { width: 64px; height: 64px; border-radius: 50%; background: var(--accent-gradient); display: flex; align-items: center; justify-content: center; font-size: 28px; font-weight: 700; color: #0A0A12; flex-shrink: 0; }
.profile-info { flex: 1; min-width: 0; }
.profile-info h2 { font-size: 24px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.profile-stats { display: flex; gap: 32px; }
.stat-item { text-align: center; }
.stat-value { display: block; font-size: 28px; font-weight: 700; color: var(--accent); }
.stat-label { font-size: 12px; color: var(--text-tertiary); }

.profile-content { max-width: var(--max-width); margin: 0 auto; padding: 32px 40px 60px; display: grid; grid-template-columns: 1.5fr 1fr; gap: 32px; align-items: start; }

.profile-section { background: var(--bg-card); border: 1px solid var(--border-light); border-radius: var(--r-lg); overflow: hidden; }

.section-head { display: flex; align-items: center; justify-content: space-between; padding: 24px 28px 16px; border-bottom: 1px solid var(--border-light); }
.section-head h3 { font-size: 17px; font-weight: 700; color: var(--text-primary); }
.section-head__actions { display: flex; align-items: center; gap: 10px; }

.filter-check { display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--text-secondary); cursor: pointer; }
.filter-check input { accent-color: var(--accent); }

.msg-loading { display: flex; align-items: center; justify-content: center; gap: 10px; padding: 48px 0; }
.msg-empty { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 48px 0; }
.msg-empty-icon { color: var(--text-tertiary); opacity: 0.4; }

.msg-list { padding: 8px 0; }
.msg-item { display: flex; gap: 14px; padding: 18px 28px; cursor: pointer; transition: background var(--t-fast); border-bottom: 1px solid var(--border-light); }
.msg-item:last-child { border-bottom: none; }
.msg-item:hover { background: rgba(255,255,255,0.02); }
.msg-item--unread { background: rgba(0, 212, 170, 0.03); }
.msg-item__dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent); margin-top: 6px; flex-shrink: 0; }
.msg-item__content { flex: 1; min-width: 0; }
.msg-item__head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 6px; }
.msg-item__title { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.msg-item__time { font-size: 12px; color: var(--text-tertiary); white-space: nowrap; }
.msg-item__body { font-size: 13px; color: var(--text-secondary); line-height: 1.5; margin-bottom: 8px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

.upload-list { padding: 8px 0; }
.upload-item { display: flex; align-items: center; justify-content: space-between; padding: 16px 28px; border-bottom: 1px solid var(--border-light); }
.upload-item:last-child { border-bottom: none; }
.upload-item__info { display: flex; flex-direction: column; gap: 4px; min-width: 0; flex: 1; }
.upload-item__title { font-size: 14px; font-weight: 500; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.upload-item__cat { font-size: 12px; color: var(--text-tertiary); }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 9999; padding: 24px; }
.modal-content { background: var(--bg-elevated); border: 1px solid var(--border-strong); border-radius: var(--r-lg); width: 100%; max-width: 480px; max-height: 80vh; overflow-y: auto; box-shadow: var(--shadow-xl); }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 24px 28px 0; }
.modal-header h3 { font-size: 18px; font-weight: 700; color: var(--text-primary); }
.modal-close { display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; border-radius: var(--r-sm); background: transparent; border: none; color: var(--text-tertiary); cursor: pointer; transition: all var(--t-fast); }
.modal-close:hover { background: rgba(255,255,255,0.06); color: var(--text-primary); }
.modal-body { padding: 20px 28px 28px; }
.modal-msg-time { font-size: 12px; color: var(--text-tertiary); margin-bottom: 16px; }
.modal-msg-content { font-size: 14px; color: var(--text-primary); line-height: 1.7; }

.spinner { display: inline-block; width: 16px; height: 16px; border: 2px solid rgba(255,255,255,0.1); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.6s linear infinite; }

@media (max-width: 900px) {
  .profile-content { grid-template-columns: 1fr; padding: 24px 20px 40px; }
  .profile-header__inner { flex-direction: column; text-align: center; padding: 32px 20px; }
  .profile-stats { gap: 24px; }
}

/* Floating feedback button */
.fab-feedback { position: fixed; bottom: 32px; right: 32px; width: 52px; height: 52px; border-radius: 50%; background: var(--accent-gradient); border: none; color: #0A0A12; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: var(--shadow-lg); z-index: 100; transition: all var(--t-base) var(--ease-out); }
.fab-feedback:hover { transform: scale(1.08); box-shadow: var(--shadow-xl); }

/* Form fields for feedback modal */
.field { display: flex; flex-direction: column; gap: 7px; margin-bottom: 16px; }
.field-label { font-size: 13px; font-weight: 600; color: var(--text-secondary); }
.field-input { padding: 12px 16px; border: 1px solid var(--border-default); border-radius: var(--r-sm); font-size: 14px; font-family: inherit; background: var(--bg-surface); color: var(--text-primary); outline: none; transition: border-color var(--t-fast); width: 100%; }
.field-input:focus { border-color: var(--accent); }
.field-select { cursor: pointer; }
.field-textarea { resize: vertical; min-height: 80px; }

.fb-success { font-size: 14px; color: #34D399; margin-top: 8px; }
.fb-error { font-size: 13px; color: #F87171; margin-top: 8px; }

@keyframes spin { to { transform: rotate(360deg); } }
</style>
