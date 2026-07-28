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
        <div class="role-tabs">
          <button :class="['role-tab', { active: role === 'user' }]" @click="role = 'user'">用户登录</button>
          <button :class="['role-tab', { active: role === 'admin' }]" @click="role = 'admin'">管理员登录</button>
        </div>
        <div class="form-body">
          <div class="field">
            <label class="field-label">用户名</label>
            <input v-model="username" type="text" class="field-input" :placeholder="role === 'admin' ? 'admin' : '请输入用户名'" @keydown.enter="handleLogin" />
          </div>
          <div class="field">
            <label class="field-label">密码</label>
            <input v-model="password" type="password" class="field-input" placeholder="请输入密码" @keydown.enter="handleLogin" />
          </div>
          <p v-if="error" class="form-error">{{ error }}</p>
          <button class="btn-login" @click="handleLogin">
            登录
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
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
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const role = ref('user')
const username = ref('')
const password = ref('')
const error = ref('')

function handleLogin() {
  error.value = ''
  if (!username.value.trim() || !password.value.trim()) { error.value = '请输入用户名和密码'; return }
  if (role.value === 'admin') {
    if (username.value === 'admin' && password.value === 'admin') {
      sessionStorage.setItem('loginInfo', JSON.stringify({ role: 'admin', username: 'admin' }))
      router.push('/admin')
    } else { error.value = '管理员账号或密码错误' }
  } else {
    sessionStorage.setItem('loginInfo', JSON.stringify({ role: 'user', username: username.value }))
    router.push('/home')
  }
}
</script>

<style scoped>
.login-page { display: flex; height: 100vh; overflow: hidden; }
.login-left { flex: 1; display: flex; align-items: center; justify-content: center; background: var(--bg-page); padding: 48px; }
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

.btn-login { display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%; padding: 14px 24px; background: var(--accent); color: #0A0A12; border: none; border-radius: var(--r-sm); font-size: 16px; font-weight: 600; font-family: inherit; margin-top: 6px; cursor: pointer; transition: all var(--t-fast) var(--ease-out); box-shadow: 0 2px 12px rgba(0, 212, 170, 0.3); }
.btn-login:hover { background: var(--accent-hover); box-shadow: 0 4px 20px rgba(0, 212, 170, 0.4); transform: translateY(-1px); }
.btn-login:active { transform: scale(0.98); }

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
</style>
