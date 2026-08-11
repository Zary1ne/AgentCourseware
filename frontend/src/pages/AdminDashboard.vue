<template>
  <div class="admin">
    <header class="admin-header">
      <h2>管理后台</h2>
      <span class="text-tertiary">Teaching Agent 管理系统</span>
    </header>

    <!-- 标签导航 -->
    <nav class="admin-tabs">
      <button v-for="tab in tabs" :key="tab.key" :class="['admin-tab', { active: activeTab === tab.key }]" @click="activeTab = tab.key">
        <span class="tab-icon" v-html="tab.icon"></span>
        <span class="tab-label">{{ tab.label }}</span>
        <span v-if="tab.key === 'review' && pendingCoursewareCount > 0" class="tab-badge">{{ pendingCoursewareCount }}</span>
        <span v-if="tab.key === 'feedback' && pendingFeedbackCount > 0" class="tab-badge tab-badge--amber">{{ pendingFeedbackCount }}</span>
      </button>
    </nav>

    <!-- ==================== 仪表盘 ==================== -->
    <div v-if="activeTab === 'dashboard'" class="tab-content">
      <div class="dashboard-grid">
        <!-- 用户总数 -->
        <div class="dash-card">
          <div class="dash-card__body">
            <div class="dash-card__info">
              <span class="dash-card__label">注册用户</span>
              <span class="dash-card__value">{{ stats.totalUsers ?? '—' }}</span>
              <span class="dash-card__sub">其中 {{ stats.bannedUsers ?? 0 }} 人已封禁</span>
            </div>
            <div class="dash-card__visual">
              <svg width="80" height="80" viewBox="0 0 80 80">
                <circle cx="40" cy="28" r="16" fill="none" stroke="var(--accent)" stroke-width="2.5" opacity="0.7"/>
                <path d="M8 72c0-18 14-32 32-32s32 14 32 32" fill="none" stroke="var(--accent)" stroke-width="2.5" opacity="0.5"/>
                <circle cx="24" cy="38" r="4" fill="var(--accent-secondary)" opacity="0.6"/>
                <circle cx="40" cy="35" r="5" fill="var(--accent)" opacity="0.8"/>
                <circle cx="56" cy="39" r="3.5" fill="var(--accent-tertiary)" opacity="0.7"/>
              </svg>
            </div>
          </div>
        </div>

        <!-- 生成总量 -->
        <div class="dash-card">
          <div class="dash-card__body">
            <div class="dash-card__info">
              <span class="dash-card__label">系统生成量</span>
              <span class="dash-card__value">{{ stats.totalGenerations ?? '—' }}</span>
              <span class="dash-card__sub">近30天累计</span>
            </div>
            <div class="dash-card__visual">
              <svg width="80" height="80" viewBox="0 0 80 80">
                <rect x="8" y="48" width="10" height="22" rx="3" fill="var(--accent)" opacity="0.35"/>
                <rect x="22" y="32" width="10" height="38" rx="3" fill="var(--accent)" opacity="0.5"/>
                <rect x="36" y="18" width="10" height="52" rx="3" fill="var(--accent)" opacity="0.7"/>
                <rect x="50" y="28" width="10" height="42" rx="3" fill="var(--accent)" opacity="0.6"/>
                <rect x="64" y="38" width="10" height="32" rx="3" fill="var(--accent)" opacity="0.45"/>
              </svg>
            </div>
          </div>
        </div>

        <!-- 社区课件 -->
        <div class="dash-card">
          <div class="dash-card__body">
            <div class="dash-card__info">
              <span class="dash-card__label">社区课件</span>
              <span class="dash-card__value">{{ stats.totalCourseware ?? '—' }}</span>
              <span class="dash-card__sub">已上架 {{ stats.approvedCourseware ?? 0 }} 个</span>
            </div>
            <div class="dash-card__visual">
              <svg width="80" height="80" viewBox="0 0 80 80">
                <rect x="10" y="14" width="38" height="50" rx="5" fill="none" stroke="var(--accent)" stroke-width="2" opacity="0.6"/>
                <line x1="16" y1="24" x2="42" y2="24" stroke="var(--accent)" stroke-width="1.5" opacity="0.5"/>
                <line x1="16" y1="32" x2="38" y2="32" stroke="var(--accent)" stroke-width="1.5" opacity="0.4"/>
                <line x1="16" y1="40" x2="42" y2="40" stroke="var(--accent)" stroke-width="1.5" opacity="0.3"/>
                <rect x="32" y="22" width="36" height="44" rx="5" fill="none" stroke="var(--accent-secondary)" stroke-width="2" opacity="0.5"/>
                <line x1="38" y1="30" x2="62" y2="30" stroke="var(--accent-secondary)" stroke-width="1.5" opacity="0.4"/>
                <line x1="38" y1="38" x2="56" y2="38" stroke="var(--accent-secondary)" stroke-width="1.5" opacity="0.3"/>
                <line x1="38" y1="46" x2="60" y2="46" stroke="var(--accent-secondary)" stroke-width="1.5" opacity="0.25"/>
              </svg>
            </div>
          </div>
        </div>

        <!-- 待审核 -->
        <div class="dash-card dash-card--warn">
          <div class="dash-card__body">
            <div class="dash-card__info">
              <span class="dash-card__label">待审核课件</span>
              <span class="dash-card__value">{{ stats.pendingCourseware ?? '—' }}</span>
              <span class="dash-card__sub">待处理反馈 {{ stats.pendingFeedback ?? 0 }} 条</span>
            </div>
            <div class="dash-card__visual">
              <svg width="80" height="80" viewBox="0 0 80 80">
                <circle cx="40" cy="40" r="30" fill="none" stroke="var(--border-default)" stroke-width="4"/>
                <circle cx="40" cy="40" r="30" fill="none" stroke="#FBBF24" stroke-width="4"
                  :stroke-dasharray="188.5" :stroke-dashoffset="188.5 - 188.5 * pendingRatio"
                  stroke-linecap="round" transform="rotate(-90 40 40)" style="transition: stroke-dashoffset 1s var(--ease-out)"/>
                <text x="40" y="37" text-anchor="middle" fill="var(--text-primary)" font-size="16" font-weight="700">{{ stats.pendingCourseware ?? 0 }}</text>
                <text x="40" y="53" text-anchor="middle" fill="var(--text-tertiary)" font-size="9">待审核</text>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- 最近活动 -->
      <div class="dash-activity">
        <h3>最近活动</h3>
        <div v-if="stats.recentActivities?.length" class="activity-list">
          <div v-for="(act, i) in stats.recentActivities.slice(0, 8)" :key="i" class="activity-item">
            <span :class="['activity-dot', act.text === '课件生成' ? 'activity-dot--gen' : '']"></span>
            <span class="activity-text">{{ act.text }}</span>
            <span class="activity-time">{{ act.time }}</span>
          </div>
        </div>
        <p v-else class="text-tertiary" style="padding:24px 0;text-align:center">暂无活动记录</p>
      </div>
    </div>

    <!-- ==================== 用户管理 ==================== -->
    <div v-if="activeTab === 'users'" class="tab-content">
      <div class="panel-header">
        <h3>所有用户</h3>
        <span class="text-tertiary">共 {{ users.length }} 人</span>
      </div>
      <div v-if="loadingUsers" class="panel-center"><span class="spinner"></span></div>
      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr><th>用户名</th><th>角色</th><th>注册时间</th><th>生成</th><th>上传</th><th>状态</th><th>操作</th></tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id" :class="{ 'row-banned': u.banned }">
              <td class="cell-user">{{ u.username }}</td>
              <td><span :class="['badge', u.role === 'admin' ? 'badge-accent' : 'badge-default']">{{ u.role === 'admin' ? '管理员' : '用户' }}</span></td>
              <td class="text-tertiary">{{ fmtDate(u.created_at) }}</td>
              <td>{{ u.stats?.generations || 0 }}</td>
              <td>{{ u.stats?.uploads || 0 }}</td>
              <td><span :class="['badge', u.banned ? 'badge-error' : 'badge-success']">{{ u.banned ? '已封禁' : '正常' }}</span></td>
              <td class="cell-actions">
                <template v-if="u.role !== 'admin'">
                  <button class="btn-ghost-xs" @click="openEditUser(u)">编辑</button>
                  <button v-if="!u.banned" class="btn-ghost-xs btn-danger" @click="openBan(u)">封禁</button>
                  <button v-else class="btn-ghost-xs btn-success" @click="handleUnban(u.id)">解封</button>
                </template>
                <span v-else class="text-tertiary">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ==================== 社区审核 ==================== -->
    <div v-if="activeTab === 'review'" class="tab-content">
      <div class="panel-header">
        <h3>社区审核</h3>
        <div class="sub-tabs">
          <button :class="['sub-tab', { active: reviewFilter === 'pending' }]" @click="reviewFilter = 'pending'">
            待审核 ({{ pendingCoursewareCount }})
          </button>
          <button :class="['sub-tab', { active: reviewFilter === 'all' }]" @click="reviewFilter = 'all'">
            全部记录
          </button>
        </div>
      </div>

      <div v-if="loadingReview" class="panel-center"><span class="spinner"></span></div>
      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr><th>标题</th><th>上传者</th><th>分类</th><th>文件</th><th>状态</th><th>时间</th><th>操作</th></tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredReviewList" :key="item.id">
              <td class="cell-title">{{ item.title }}</td>
              <td>{{ item.author }}</td>
              <td><span class="badge badge-default">{{ item.category }}</span></td>
              <td>
                <a v-if="item.files?.filename" :href="getCoursewareFileUrl(item.id)" target="_blank" class="file-link">{{ item.files.filename }}</a>
                <span v-else class="text-tertiary">—</span>
              </td>
              <td><span :class="['badge', statusBadge(item.status)]">{{ statusLabel(item.status) }}</span></td>
              <td class="text-tertiary">{{ fmtTime(item.created_at) }}</td>
              <td class="cell-actions">
                <template v-if="item.status === 'pending'">
                  <button class="btn-ghost-xs btn-success" @click="handleReview(item.id, true)">通过</button>
                  <button class="btn-ghost-xs btn-danger" @click="openReject(item)">拒绝</button>
                </template>
                <span v-else class="text-tertiary" style="font-size:12px">
                  {{ item.review_comment ? '理由：' + item.review_comment : '—' }}
                </span>
              </td>
            </tr>
            <tr v-if="filteredReviewList.length === 0">
              <td colspan="7" class="text-tertiary" style="text-align:center;padding:32px">暂无记录</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ==================== 状态审核（反馈） ==================== -->
    <div v-if="activeTab === 'feedback'" class="tab-content">
      <div class="panel-header">
        <h3>用户反馈</h3>
        <div class="sub-tabs">
          <button :class="['sub-tab', { active: fbFilter === 'pending' }]" @click="fbFilter = 'pending'">
            待处理 ({{ pendingFeedbackCount }})
          </button>
          <button :class="['sub-tab', { active: fbFilter === 'all' }]" @click="fbFilter = 'all'">
            全部记录
          </button>
        </div>
      </div>
      <div v-if="loadingFb" class="panel-center"><span class="spinner"></span></div>
      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr><th>标题</th><th>用户</th><th>类型</th><th>内容</th><th>状态</th><th>时间</th><th>操作</th></tr>
          </thead>
          <tbody>
            <tr v-for="fb in filteredFbList" :key="fb.id">
              <td class="cell-title">{{ fb.title }}</td>
              <td>{{ fb.username }}</td>
              <td><span class="badge badge-default">{{ fbTypeLabel(fb.type) }}</span></td>
              <td class="cell-desc">{{ fb.content?.slice(0, 60) }}{{ fb.content?.length > 60 ? '...' : '' }}</td>
              <td><span :class="['badge', fbStatusBadge(fb.status)]">{{ fbStatusLabel(fb.status) }}</span></td>
              <td class="text-tertiary">{{ fmtTime(fb.created_at) }}</td>
              <td class="cell-actions">
                <template v-if="fb.status === 'pending'">
                  <button class="btn-ghost-xs" @click="openFbDetail(fb)">查看</button>
                </template>
                <span v-else class="text-tertiary" style="font-size:12px">{{ fb.admin_reply || '—' }}</span>
              </td>
            </tr>
            <tr v-if="filteredFbList.length === 0">
              <td colspan="7" class="text-tertiary" style="text-align:center;padding:32px">暂无记录</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ===== 弹窗：拒绝课件 ===== -->
    <Teleport to="body">
      <div v-if="rejectTarget" class="modal-overlay" @click.self="rejectTarget = null">
        <div class="modal-content">
          <div class="modal-header"><h3>拒绝课件</h3><button class="modal-close" @click="rejectTarget = null"><svg width="16" height="16" viewBox="0 0 16 16"><path d="M12 4L4 12M4 4l8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button></div>
          <div class="modal-body">
            <p class="text-secondary" style="margin-bottom:12px">拒绝「{{ rejectTarget.title }}」</p>
            <div class="field"><label class="field-label">拒绝理由 *</label><textarea v-model="rejectComment" class="field-input field-textarea" rows="3" placeholder="必填"></textarea></div>
            <p v-if="reviewError" class="form-error">{{ reviewError }}</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="rejectTarget = null">取消</button>
            <button class="btn btn-primary" style="background:var(--error)" @click="handleRejectConfirm">确认拒绝</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ===== 弹窗：封禁用户 ===== -->
    <Teleport to="body">
      <div v-if="banTarget" class="modal-overlay" @click.self="banTarget = null">
        <div class="modal-content">
          <div class="modal-header"><h3>封禁用户</h3><button class="modal-close" @click="banTarget = null"><svg width="16" height="16" viewBox="0 0 16 16"><path d="M12 4L4 12M4 4l8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button></div>
          <div class="modal-body">
            <p class="text-secondary" style="margin-bottom:12px">封禁「{{ banTarget.username }}」</p>
            <div class="field"><label class="field-label">封禁理由 *</label><textarea v-model="banReason" class="field-input field-textarea" rows="3" placeholder="必填"></textarea></div>
            <p v-if="banError" class="form-error">{{ banError }}</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="banTarget = null">取消</button>
            <button class="btn btn-primary" style="background:var(--error)" @click="handleBanConfirm">确认封禁</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ===== 弹窗：编辑用户 ===== -->
    <Teleport to="body">
      <div v-if="editTarget" class="modal-overlay" @click.self="editTarget = null">
        <div class="modal-content">
          <div class="modal-header"><h3>编辑用户</h3><button class="modal-close" @click="editTarget = null"><svg width="16" height="16" viewBox="0 0 16 16"><path d="M12 4L4 12M4 4l8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button></div>
          <div class="modal-body">
            <div class="field"><label class="field-label">用户名</label><input v-model="editForm.username" type="text" class="field-input" /></div>
            <div class="field"><label class="field-label">新密码（留空不修改）</label><input v-model="editForm.password" type="text" class="field-input" placeholder="至少3个字符" /></div>
            <p v-if="editError" class="form-error">{{ editError }}</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="editTarget = null">取消</button>
            <button class="btn btn-primary" @click="handleEditConfirm">保存</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ===== 弹窗：反馈详情 ===== -->
    <Teleport to="body">
      <div v-if="fbDetail" class="modal-overlay" @click.self="fbDetail = null">
        <div class="modal-content" style="max-width:560px">
          <div class="modal-header"><h3>反馈详情</h3><button class="modal-close" @click="fbDetail = null"><svg width="16" height="16" viewBox="0 0 16 16"><path d="M12 4L4 12M4 4l8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button></div>
          <div class="modal-body">
            <div style="margin-bottom:16px">
              <span class="badge badge-default" style="margin-right:8px">{{ fbTypeLabel(fbDetail.type) }}</span>
              <span class="text-tertiary" style="font-size:12px">{{ fbDetail.username }} · {{ fmtTime(fbDetail.created_at) }}</span>
            </div>
            <h3 style="font-size:17px;margin-bottom:8px">{{ fbDetail.title }}</h3>
            <p style="font-size:14px;color:var(--text-secondary);line-height:1.7;margin-bottom:20px;white-space:pre-wrap">{{ fbDetail.content }}</p>
            <div class="field"><label class="field-label">回复（可选）</label><textarea v-model="fbReply" class="field-input field-textarea" rows="3" placeholder="给用户的回复..."></textarea></div>
            <p v-if="fbError" class="form-error">{{ fbError }}</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="handleFbReview('reviewed')">标记已查看</button>
            <button class="btn btn-primary" @click="handleFbReview('closed')">处理完成</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import {
  getAdminStats, getPendingCourseware, reviewCourseware, getAllUsers,
  banUser, unbanUser, updateUser, getCoursewareFileUrl,
  getFeedbackList, getPendingFeedbackCount, reviewFeedback,
} from '../api'

// Tab 定义
const tabs = [
  { key: 'dashboard', label: '仪表盘', icon: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="1" y="1" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.2"/><rect x="9" y="1" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.2"/><rect x="1" y="9" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.2"/><rect x="9" y="9" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.2"/></svg>' },
  { key: 'users', label: '用户管理', icon: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="6" cy="5" r="3" stroke="currentColor" stroke-width="1.2"/><path d="M1 14c0-3 2.2-5 5-5s5 2 5 5" stroke="currentColor" stroke-width="1.2"/><circle cx="11" cy="5" r="2" stroke="currentColor" stroke-width="1.2"/><path d="M9 12h6" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>' },
  { key: 'review', label: '社区审核', icon: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="2" y="1.5" width="12" height="13" rx="2" stroke="currentColor" stroke-width="1.2"/><path d="M5 5.5h6M5 8.5h4" stroke="currentColor" stroke-width="1" stroke-linecap="round"/></svg>' },
  { key: 'feedback', label: '状态审核', icon: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 2.5h12v9H5.5L3 14V2.5z" stroke="currentColor" stroke-width="1.2"/></svg>' },
]
const activeTab = ref('dashboard')

// 仪表盘数据
const stats = ref({})

// 审核数据
const reviewFilter = ref('pending')
const pendingList = ref([])
const allReviewList = ref([])
const loadingReview = ref(false)
const rejectTarget = ref(null)
const rejectComment = ref('')
const reviewError = ref('')

// 用户管理
const users = ref([])
const loadingUsers = ref(false)
const banTarget = ref(null)
const banReason = ref('')
const banError = ref('')
const editTarget = ref(null)
const editForm = ref({ username: '', password: '' })
const editError = ref('')

// 反馈
const fbFilter = ref('pending')
const fbList = ref([])
const loadingFb = ref(false)
const fbDetail = ref(null)
const fbReply = ref('')
const fbError = ref('')

// 计算属性
const pendingCoursewareCount = computed(() => stats.value.pendingCourseware ?? 0)
const pendingFeedbackCount = computed(() => stats.value.pendingFeedback ?? 0)
const pendingRatio = computed(() => {
  const total = stats.value.totalCourseware || 1
  return Math.min((stats.value.pendingCourseware || 0) / total, 1)
})

const filteredReviewList = computed(() => {
  if (reviewFilter.value === 'pending') return pendingList.value
  return allReviewList.value
})

const filteredFbList = computed(() => {
  if (fbFilter.value === 'pending') return fbList.value.filter(f => f.status === 'pending')
  return fbList.value
})

// 格式化
const fmtTime = (iso) => { try { const d = new Date(iso); return `${d.getMonth()+1}-${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}` } catch { return '' } }
const fmtDate = (iso) => { try { return new Date(iso).toLocaleDateString('zh-CN') } catch { return '—' } }

const statusBadge = (s) => ({ pending: 'badge-warning', approved: 'badge-success', rejected: 'badge-error' }[s] || 'badge-default')
const statusLabel = (s) => ({ pending: '待审核', approved: '已通过', rejected: '已拒绝' }[s] || s)
const fbTypeLabel = (t) => ({ bug: 'Bug', feature: '功能建议', improvement: '改进', other: '其他' }[t] || t)
const fbStatusBadge = (s) => ({ pending: 'badge-warning', reviewed: 'badge-default', closed: 'badge-success' }[s] || 'badge-default')
const fbStatusLabel = (s) => ({ pending: '待处理', reviewed: '已查看', closed: '已处理' }[s] || s)

// ===== 数据加载 =====
async function fetchStats() {
  try { const r = await getAdminStats(); stats.value = r.data } catch { stats.value = {} }
}
async function fetchPending() {
  loadingReview.value = true
  try { const r = await getPendingCourseware(); pendingList.value = r.data.items || [] } catch { pendingList.value = [] }
  finally { loadingReview.value = false }
}
async function fetchAllReviews() {
  try { const r = await getPendingCourseware('all'); allReviewList.value = r.data.items || [] } catch { allReviewList.value = [] }
}
async function fetchUsers() {
  loadingUsers.value = true
  try { const r = await getAllUsers(); users.value = r.data.users || [] } catch { users.value = [] }
  finally { loadingUsers.value = false }
}
async function fetchFeedback() {
  loadingFb.value = true
  try { const r = await getFeedbackList(); fbList.value = r.data.items || [] } catch { fbList.value = [] }
  finally { loadingFb.value = false }
}

// 切换 tab 时加载
watch(activeTab, (v) => {
  if (v === 'users') fetchUsers()
  if (v === 'review') { fetchPending(); fetchAllReviews() }
  if (v === 'feedback') fetchFeedback()
})

// ===== 审核操作 =====
function openReject(item) { rejectTarget.value = item; rejectComment.value = ''; reviewError.value = '' }
async function handleRejectConfirm() {
  if (!rejectComment.value.trim()) { reviewError.value = '请输入拒绝理由'; return }
  try { await reviewCourseware(rejectTarget.value.id, false, rejectComment.value.trim()); rejectTarget.value = null; fetchPending(); fetchStats() }
  catch (e) { reviewError.value = e.response?.data?.detail || '操作失败' }
}
async function handleReview(cwId, approved) {
  try { await reviewCourseware(cwId, approved, ''); fetchPending(); fetchStats() } catch {}
}

// ===== 用户操作 =====
function openBan(user) { banTarget.value = user; banReason.value = ''; banError.value = '' }
async function handleBanConfirm() {
  if (!banReason.value.trim()) { banError.value = '请输入封禁理由'; return }
  try { await banUser(banTarget.value.id, banReason.value.trim()); banTarget.value = null; fetchUsers(); fetchStats() }
  catch (e) { banError.value = e.response?.data?.detail || '操作失败' }
}
async function handleUnban(uid) { try { await unbanUser(uid); fetchUsers(); fetchStats() } catch {} }

function openEditUser(u) { editTarget.value = u; editForm.value = { username: u.username, password: '' }; editError.value = '' }
async function handleEditConfirm() {
  if (!editForm.value.username.trim()) { editError.value = '用户名不能为空'; return }
  if (editForm.value.password && editForm.value.password.length < 3) { editError.value = '密码至少3个字符'; return }
  try { await updateUser(editTarget.value.id, editForm.value.username.trim(), editForm.value.password); editTarget.value = null; fetchUsers() }
  catch (e) { editError.value = e.response?.data?.detail || '操作失败' }
}

// ===== 反馈操作 =====
function openFbDetail(fb) { fbDetail.value = fb; fbReply.value = ''; fbError.value = '' }
async function handleFbReview(status) {
  try { await reviewFeedback(fbDetail.value.id, status, fbReply.value); fbDetail.value = null; fetchFeedback(); fetchStats() }
  catch (e) { fbError.value = e.response?.data?.detail || '操作失败' }
}

onMounted(() => {
  fetchStats()
  fetchPending()
})
</script>

<style scoped>
.admin { padding: 40px; max-width: var(--max-width); margin: 0 auto; min-height: 100vh; }
.admin-header { margin-bottom: 32px; }
.admin-header h2 { font-size: 28px; font-weight: 700; letter-spacing: -0.025em; color: var(--text-primary); margin-bottom: 6px; }

/* ===== Tabs ===== */
.admin-tabs { display: flex; gap: 4px; margin-bottom: 32px; background: var(--bg-surface); border: 1px solid var(--border-light); border-radius: var(--r-md); padding: 4px; }
.admin-tab { display: flex; align-items: center; gap: 8px; padding: 10px 20px; border-radius: var(--r-sm); font-size: 14px; font-weight: 600; color: var(--text-secondary); background: transparent; border: none; cursor: pointer; font-family: inherit; transition: all var(--t-fast) var(--ease-out); position: relative; }
.admin-tab:hover { color: var(--text-primary); }
.admin-tab.active { background: var(--bg-card); color: var(--text-primary); border: 1px solid var(--border-default); }
.tab-icon { display: flex; align-items: center; }
.tab-badge { min-width: 20px; height: 20px; border-radius: 99px; background: #F87171; color: #fff; font-size: 11px; font-weight: 700; display: flex; align-items: center; justify-content: center; padding: 0 6px; }
.tab-badge--amber { background: #FBBF24; color: #0A0A12; }

.tab-content { animation: fade-up-sm 0.25s var(--ease-out); }

/* ===== Dashboard Cards ===== */
.dashboard-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 28px; }
.dash-card { background: var(--bg-card); border: 1px solid var(--border-light); border-radius: var(--r-lg); padding: 28px; transition: all var(--t-base) var(--ease-out); }
.dash-card:hover { border-color: var(--border-strong); box-shadow: var(--shadow-md); transform: translateY(-2px); }
.dash-card--warn { border-color: rgba(251,191,36,0.15); }
.dash-card__body { display: flex; justify-content: space-between; align-items: center; }
.dash-card__info { display: flex; flex-direction: column; gap: 4px; }
.dash-card__label { font-size: 13px; font-weight: 500; color: var(--text-secondary); letter-spacing: 0.03em; }
.dash-card__value { font-size: 36px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.03em; line-height: 1; }
.dash-card__sub { font-size: 12px; color: var(--text-tertiary); }
.dash-card__visual { flex-shrink: 0; }

.dash-activity { background: var(--bg-card); border: 1px solid var(--border-light); border-radius: var(--r-lg); padding: 24px 28px; }
.dash-activity h3 { font-size: 16px; font-weight: 700; color: var(--text-primary); margin-bottom: 16px; }
.activity-list { display: flex; flex-direction: column; gap: 2px; }
.activity-item { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid var(--border-light); font-size: 13px; }
.activity-item:last-child { border-bottom: none; }
.activity-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent); flex-shrink: 0; }
.activity-dot--gen { background: var(--accent-secondary); }
.activity-text { flex: 1; color: var(--text-secondary); }
.activity-time { color: var(--text-tertiary); font-family: var(--font-mono); font-size: 12px; }

/* ===== Panel ===== */
.panel-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.panel-header h3 { font-size: 18px; font-weight: 700; color: var(--text-primary); }
.panel-center { display: flex; justify-content: center; padding: 48px 0; }

.sub-tabs { display: flex; gap: 4px; background: var(--bg-surface); border: 1px solid var(--border-light); border-radius: var(--r-sm); padding: 3px; }
.sub-tab { padding: 7px 16px; border-radius: var(--r-xs); font-size: 13px; font-weight: 600; color: var(--text-secondary); background: transparent; border: none; cursor: pointer; font-family: inherit; transition: all var(--t-fast); }
.sub-tab.active { background: var(--bg-card); color: var(--text-primary); border: 1px solid var(--border-default); }

/* ===== Table ===== */
.table-wrap { background: var(--bg-card); border: 1px solid var(--border-light); border-radius: var(--r-lg); overflow: hidden; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { text-align: left; padding: 14px 20px; font-size: 11px; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.06em; border-bottom: 1px solid var(--border-light); background: var(--bg-surface); }
.data-table td { padding: 16px 20px; font-size: 13px; color: var(--text-primary); border-bottom: 1px solid var(--border-light); }
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background: rgba(255,255,255,0.015); }
.row-banned td { background: rgba(248,113,113,0.03); }
.cell-user { font-weight: 600; }
.cell-title { font-weight: 600; max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cell-desc { max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--text-secondary); }
.cell-actions { display: flex; gap: 6px; white-space: nowrap; }
.file-link { font-size: 12px; color: var(--accent-secondary); text-decoration: underline; }
.file-link:hover { color: var(--accent-secondary-hover); }

/* Ghost buttons */
.btn-ghost-xs { padding: 5px 12px; border-radius: var(--r-xs); font-size: 12px; font-weight: 600; cursor: pointer; border: 1px solid var(--border-default); background: transparent; color: var(--text-secondary); font-family: inherit; transition: all var(--t-fast); }
.btn-ghost-xs:hover { background: rgba(255,255,255,0.04); color: var(--text-primary); }
.btn-danger { color: #F87171; border-color: rgba(248,113,113,0.25); }
.btn-danger:hover { background: rgba(248,113,113,0.08); color: #F87171; }
.btn-success { color: #34D399; border-color: rgba(52,211,153,0.25); }
.btn-success:hover { background: rgba(52,211,153,0.08); color: #34D399; }

/* ===== Modal ===== */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 9999; padding: 24px; }
.modal-content { background: var(--bg-elevated); border: 1px solid var(--border-strong); border-radius: var(--r-lg); width: 100%; max-width: 480px; max-height: 85vh; overflow-y: auto; box-shadow: var(--shadow-xl); }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 24px 28px 0; }
.modal-header h3 { font-size: 18px; font-weight: 700; color: var(--text-primary); }
.modal-close { display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; border-radius: var(--r-sm); background: transparent; border: none; color: var(--text-tertiary); cursor: pointer; transition: all var(--t-fast); }
.modal-close:hover { background: rgba(255,255,255,0.06); color: var(--text-primary); }
.modal-body { padding: 20px 28px; }
.modal-footer { padding: 0 28px 24px; display: flex; justify-content: flex-end; gap: 10px; }
.field { display: flex; flex-direction: column; gap: 7px; }
.field-label { font-size: 13px; font-weight: 600; color: var(--text-secondary); }
.field-input { padding: 12px 16px; border: 1px solid var(--border-default); border-radius: var(--r-sm); font-size: 14px; font-family: inherit; background: var(--bg-surface); color: var(--text-primary); outline: none; transition: all var(--t-fast); width: 100%; }
.field-input:focus { border-color: var(--accent); }
.field-textarea { resize: vertical; min-height: 80px; }
.form-error { font-size: 13px; color: #F87171; margin: 8px 0 0; }
.spinner { display: inline-block; width: 18px; height: 18px; border: 2px solid rgba(255,255,255,0.1); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.6s linear infinite; }

@media (max-width: 1100px) { .dashboard-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 700px) { .dashboard-grid { grid-template-columns: 1fr; } .admin-tabs { overflow-x: auto; } .admin { padding: 24px 16px; } }

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fade-up-sm { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
</style>
