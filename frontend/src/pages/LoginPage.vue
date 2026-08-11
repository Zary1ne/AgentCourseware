<template>
  <div class="login-page">
    <div class="login-left">
      <div class="login-form-wrap">
        <div class="form-header">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <rect width="28" height="28" rx="6" fill="var(--accent)"/>
            <path d="M5 10h18M5 14h14M5 18h10" stroke="#0A0A12" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          <h1>Teaching Agent</h1>
        </div>

        <!-- 登录 / 注册 切换 -->
        <div class="role-tabs">
          <button :class="['role-tab', { active: mode === 'login' }]" @click="switchMode('login')">登录</button>
          <button :class="['role-tab', { active: mode === 'register' }]" @click="switchMode('register')">注册</button>
        </div>

        <div class="form-body">
          <!-- 用户名 -->
          <div class="field">
            <label class="field-label">用户名</label>
            <input v-model="username" type="text" class="field-input" placeholder="请输入用户名（2-20个字符）" @keydown.enter="handleSubmit" />
          </div>

          <!-- 密码 -->
          <div class="field">
            <label class="field-label">密码</label>
            <input v-model="password" type="password" class="field-input" placeholder="请输入密码（至少3个字符）" @keydown.enter="handleSubmit" />
          </div>

          <!-- 注册模式下的确认密码 -->
          <div v-if="mode === 'register'" class="field">
            <label class="field-label">确认密码</label>
            <input v-model="confirmPassword" type="password" class="field-input" placeholder="请再次输入密码" @keydown.enter="handleSubmit" />
          </div>

          <p v-if="error" class="form-error">{{ error }}</p>
          <p v-if="successMsg" class="form-success">{{ successMsg }}</p>

          <button class="btn-login" @click="handleSubmit" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            {{ mode === 'login' ? '登录' : '注册' }}
            <svg v-if="!loading" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>

          <!-- 管理员入口 -->
          <button class="btn-admin-link" @click="showAdminLogin = !showAdminLogin">
            {{ showAdminLogin ? '返回用户登录' : '管理员入口' }}
          </button>

          <!-- 管理员登录（折叠） -->
          <div v-if="showAdminLogin" class="admin-login-section">
            <div class="admin-divider"><span>管理员登录</span></div>
            <div class="field">
              <label class="field-label">管理员密码</label>
              <input v-model="adminPwd" type="password" class="field-input" placeholder="请输入管理员密码" @keydown.enter="handleAdminLogin" />
            </div>
            <p v-if="adminError" class="form-error">{{ adminError }}</p>
            <button class="btn-login btn-admin" @click="handleAdminLogin">管理员登录</button>
          </div>
        </div>
      </div>
    </div>

    <div class="login-right">
      <div class="brand-content">
        <p class="brand-tag">AI · 多模态 · 课件共创</p>
        <h2>以教学思路为核心<br />打造智能备课体验</h2>
        <p class="brand-desc">多轮对话理解教学意图，融合参考资料与知识库，<br />一键生成 PPT 课件、Word 教案和互动问答。</p>
        <div class="brand-features">
          <div class="feature-item"><span class="feature-num">01</span><span>智能对话 · 意图理解</span></div>
          <div class="feature-item"><span class="feature-num">02</span><span>知识库 RAG · 文件解析</span></div>
          <div class="feature-item"><span class="feature-num">03</span><span>课件生成 · 一键导出</span></div>
          <div class="feature-item"><span class="feature-num">04</span><span>开源社区 · 课件共享</span></div>
        </div>
      </div>
    </div>
  <!-- 账户封禁全屏覆盖层 -->
    <div v-if="bannedInfo" class="banned-overlay">
      <div class="banned-card">
        <div class="banned-icon">
          <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
            <circle cx="28" cy="28" r="26" stroke="#F87171" stroke-width="2.5"/>
            <path d="M28 16v16M28 36v2" stroke="#F87171" stroke-width="2.5" stroke-linecap="round"/>
          </svg>
        </div>
        <h2 class="banned-title">账户已被封禁</h2>
        <p class="banned-username">用户名：<strong>{{ bannedInfo.username }}</strong></p>
        <div class="banned-divider"></div>
        <div class="banned-reason-section">
          <span class="banned-reason-label">封禁理由</span>
          <p class="banned-reason-text">{{ bannedInfo.ban_reason }}</p>
        </div>
        <div class="banned-info-row">
          <span class="banned-info-label">封禁时间</span>
          <span class="banned-info-value">{{ formatBanTime(bannedInfo.banned_at) }}</span>
        </div>
        <div class="banned-divider"></div>
        <p class="banned-contact">如有疑问，请联系管理员：<a :href="'mailto:' + bannedInfo.admin_email">{{ bannedInfo.admin_email }}</a></p>
        <button class="btn btn-secondary" @click="bannedInfo = null; username = ''; password = ''">返回登录页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login, register } from '../api'

const router = useRouter()
const mode = ref('login')  // 'login' | 'register'
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const successMsg = ref('')
const loading = ref(false)

// 管理员登录
const showAdminLogin = ref(false)
const adminPwd = ref('')
const adminError = ref('')

// 账户封禁状态
const bannedInfo = ref(null)

function formatBanTime(iso) {
  if (!iso) return '—'
  try { return new Date(iso).toLocaleString('zh-CN') } catch { return iso }
}

function switchMode(m) {
  mode.value = m
  error.value = ''
  successMsg.value = ''
  confirmPassword.value = ''
}

async function handleSubmit() {
  error.value = ''
  successMsg.value = ''

  // 基本验证
  if (!username.value.trim()) { error.value = '请输入用户名'; return }
  if (username.value.trim().length < 2) { error.value = '用户名至少需要2个字符'; return }
  if (!password.value) { error.value = '请输入密码'; return }
  if (password.value.length < 3) { error.value = '密码至少需要3个字符'; return }

  if (mode.value === 'register') {
    if (password.value !== confirmPassword.value) { error.value = '两次输入的密码不一致'; return }

    loading.value = true
    try {
      const res = await register(username.value.trim(), password.value)
      const user = res.data.user
      // 注册成功后自动登录
      sessionStorage.setItem('loginInfo', JSON.stringify({ role: user.role, username: user.username, userId: user.id }))
      successMsg.value = '注册成功，正在跳转...'
      setTimeout(() => router.push('/home'), 800)
    } catch (e) {
      error.value = e.response?.data?.detail || '注册失败，请稍后重试'
    } finally {
      loading.value = false
    }
  } else {
    // 登录
    loading.value = true
    try {
      const res = await login(username.value.trim(), password.value)
      const user = res.data.user
      sessionStorage.setItem('loginInfo', JSON.stringify({ role: user.role, username: user.username, userId: user.id }))
      router.push('/home')
    } catch (e) {
      // 检查是否是因为账户被封禁
      if (e.response?.status === 403) {
        const detail = e.response?.data?.detail
        if (typeof detail === 'object' && detail.reason === 'account_banned') {
          bannedInfo.value = {
            username: username.value.trim(),
            ban_reason: detail.ban_reason || '您的账户已被管理员封禁',
            banned_at: detail.banned_at || '',
            admin_email: detail.admin_email || 'admin@teaching-agent.ai',
          }
          return
        }
      }
      error.value = typeof e.response?.data?.detail === 'string' ? e.response.data.detail : '登录失败，请稍后重试'
    } finally {
      loading.value = false
    }
  }
}

function handleAdminLogin() {
  adminError.value = ''
  if (!adminPwd.value) { adminError.value = '请输入管理员密码'; return }

  // 管理员登录使用专门的 auth API
  login('admin', adminPwd.value).then(res => {
    const user = res.data.user
    if (user.role === 'admin') {
      sessionStorage.setItem('loginInfo', JSON.stringify({ role: 'admin', username: 'admin', userId: user.id }))
      router.push('/admin')
    } else {
      adminError.value = '无管理员权限'
    }
  }).catch(e => {
    adminError.value = e.response?.data?.detail || '管理员登录失败'
  })
}
</script>

<style scoped>
.login-page { display: flex; height: 100vh; overflow: hidden; }
.login-left { flex: 1; display: flex; align-items: center; justify-content: center; background: var(--bg-page); padding: 48px; overflow-y: auto; }
.login-form-wrap { width: 100%; max-width: 400px; }
.form-header { display: flex; align-items: center; gap: 12px; margin-bottom: 36px; }
.form-header h1 { font-size: 22px; font-weight: 700; letter-spacing: -0.02em; color: var(--text-primary); }

.role-tabs { display: flex; border-radius: var(--r-sm); background: var(--bg-surface); border: 1px solid var(--border-light); padding: 4px; margin-bottom: 32px; }
.role-tab { flex: 1; padding: 10px 18px; border-radius: var(--r-xs); font-size: 14px; font-weight: 600; color: var(--text-secondary); background: transparent; border: none; cursor: pointer; font-family: inherit; transition: all var(--t-fast) var(--ease-out); }
.role-tab.active { background: var(--bg-card); color: var(--text-primary); border: 1px solid var(--border-default); }

.form-body { display: flex; flex-direction: column; gap: 20px; }
.field { display: flex; flex-direction: column; gap: 7px; }
.field-label { font-size: 13px; font-weight: 600; color: var(--text-secondary); }
.field-input { padding: 13px 16px; border: 1px solid var(--border-default); border-radius: var(--r-sm); font-size: 15px; font-family: inherit; background: var(--bg-surface); color: var(--text-primary); outline: none; transition: all var(--t-fast) var(--ease-out); }
.field-input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(0, 212, 170, 0.12); }
.field-input::placeholder { color: var(--text-tertiary); }
.form-error { font-size: 13px; color: #F87171; margin: 0; }
.form-success { font-size: 13px; color: #34D399; margin: 0; }

.spinner { display: inline-block; width: 16px; height: 16px; border: 2px solid rgba(0,0,0,0.2); border-top-color: #0A0A12; border-radius: 50%; animation: spin 0.6s linear infinite; }

.btn-login { display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%; padding: 14px 24px; background: var(--accent); color: #0A0A12; border: none; border-radius: var(--r-sm); font-size: 16px; font-weight: 600; font-family: inherit; margin-top: 6px; cursor: pointer; transition: all var(--t-fast) var(--ease-out); box-shadow: 0 2px 12px rgba(0, 212, 170, 0.3); }
.btn-login:hover { background: var(--accent-hover); box-shadow: 0 4px 20px rgba(0, 212, 170, 0.4); transform: translateY(-1px); }
.btn-login:active { transform: scale(0.98); }
.btn-login:disabled { opacity: 0.7; cursor: not-allowed; transform: none; }

.btn-admin-link { display: block; width: 100%; padding: 8px; background: transparent; border: none; color: var(--text-tertiary); font-size: 13px; font-family: inherit; cursor: pointer; transition: color var(--t-fast); }
.btn-admin-link:hover { color: var(--text-secondary); }

.admin-login-section { display: flex; flex-direction: column; gap: 16px; }
.admin-divider { display: flex; align-items: center; gap: 12px; }
.admin-divider::before, .admin-divider::after { content: ''; flex: 1; height: 1px; background: var(--border-default); }
.admin-divider span { font-size: 12px; color: var(--text-tertiary); white-space: nowrap; }
.btn-admin { background: var(--accent-secondary); box-shadow: 0 2px 12px rgba(99, 102, 241, 0.3); }
.btn-admin:hover { background: var(--accent-secondary-hover); box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4); }

.login-right { flex: 1; background: var(--bg-navy); display: flex; align-items: center; justify-content: center; padding: 64px; position: relative; overflow: hidden; }
.login-right::before { content:""; position: absolute; top: -25%; right: -15%; width: 600px; height: 600px; border-radius: 50%; background: radial-gradient(circle, rgba(0, 212, 170, 0.06), transparent 70%); }
.login-right::after { content:""; position: absolute; bottom: -10%; left: -10%; width: 400px; height: 400px; border-radius: 50%; background: radial-gradient(circle, rgba(0, 212, 170, 0.03), transparent 70%); }

.brand-content { position: relative; z-index: 1; max-width: 440px; }
.brand-tag { font-size: 12px; font-weight: 600; letter-spacing: 0.08em; color: var(--accent); margin-bottom: 24px; }
.brand-content h2 { font-size: 38px; font-weight: 700; letter-spacing: -0.03em; line-height: 1.2; color: var(--text-inverse); margin-bottom: 18px; }
.brand-desc { font-size: 15px; line-height: 1.8; color: rgba(255,255,255,0.5); margin-bottom: 48px; }
.brand-features { display: flex; flex-direction: column; gap: 14px; }
.feature-item { display: flex; align-items: center; gap: 16px; font-size: 14px; color: rgba(255,255,255,0.6); }
.feature-num { font-size: 11px; font-weight: 700; color: var(--accent); width: 28px; }

@media (max-width: 768px) {
  .login-right { display: none; }
  .login-left { padding: 32px 24px; }
}

/* Banned overlay - full screen */
.banned-overlay {
  position: fixed; inset: 0; z-index: 99999;
  background: rgba(10, 10, 18, 0.96);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  display: flex; align-items: center; justify-content: center;
  padding: 24px;
  animation: fade-in 0.3s var(--ease-out);
}

.banned-card {
  background: var(--bg-elevated);
  border: 1px solid rgba(248, 113, 113, 0.25);
  border-radius: var(--r-xl);
  padding: 48px 40px;
  max-width: 500px; width: 100%;
  text-align: center;
  box-shadow: 0 0 80px rgba(248, 113, 113, 0.08);
}

.banned-icon { margin-bottom: 24px; display: flex; justify-content: center; }

.banned-title {
  font-size: 24px; font-weight: 700; color: #F87171;
  letter-spacing: -0.025em; margin-bottom: 8px;
}

.banned-username {
  font-size: 15px; color: var(--text-secondary); margin-bottom: 24px;
}
.banned-username strong { color: var(--text-primary); }

.banned-divider {
  height: 1px; background: var(--border-light);
  margin: 20px 0;
}

.banned-reason-section {
  background: rgba(248, 113, 113, 0.06);
  border: 1px solid rgba(248, 113, 113, 0.12);
  border-radius: var(--r-md);
  padding: 20px;
  text-align: left;
  margin-bottom: 12px;
}

.banned-reason-label {
  display: block; font-size: 12px; font-weight: 600;
  color: var(--error); text-transform: uppercase;
  letter-spacing: 0.05em; margin-bottom: 8px;
}

.banned-reason-text {
  font-size: 15px; color: var(--text-primary);
  line-height: 1.6; white-space: pre-wrap;
}

.banned-info-row {
  display: flex; justify-content: space-between;
  align-items: center; font-size: 13px;
  padding: 0 4px;
}

.banned-info-label { color: var(--text-tertiary); }
.banned-info-value { color: var(--text-secondary); }

.banned-contact {
  font-size: 14px; color: var(--text-secondary);
  line-height: 1.6; margin-bottom: 28px;
}
.banned-contact a { color: var(--accent); font-weight: 600; }
.banned-contact a:hover { color: var(--accent-hover); }

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
</style>
