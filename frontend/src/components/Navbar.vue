<template>
  <header :class="['navbar', { 'navbar--scrolled': scrolled }]">
    <div class="navbar__inner">
      <router-link to="/" class="navbar__brand">
        <div class="navbar__logo">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <rect width="28" height="28" rx="6" fill="var(--accent)"/>
            <path d="M5 10h18M5 14h14M5 18h10" stroke="#0A0A12" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </div>
        <span class="navbar__name">Teaching Agent</span>
      </router-link>

      <nav :class="['navbar__links', { 'navbar__links--open': mobileMenuOpen }]">
        <a href="#featured" class="navbar__link" @click="closeMobile">开源社区</a>
        <a href="#" class="navbar__link">学习</a>
        <a href="#" class="navbar__link">文档</a>
        <a href="#" class="navbar__link">公司</a>
        <a href="#" class="navbar__link">定价</a>
      </nav>

      <div class="navbar__actions">
        <!-- 未登录 -->
        <template v-if="!isLoggedIn">
          <router-link to="/login" class="btn btn-primary btn-sm navbar__action-desktop">登录 / 注册</router-link>
        </template>
        <!-- 已登录用户 -->
        <template v-else-if="isUser">
          <a href="#featured" class="navbar__link navbar__action-desktop">开源社区</a>
          <router-link to="/app" class="btn btn-primary btn-sm navbar__action-desktop">工作台</router-link>
          <router-link to="/profile" class="navbar__avatar navbar__action-desktop" title="个人中心">
            <span class="avatar-circle">{{ userInitial }}</span>
          </router-link>
        </template>
        <!-- 管理员 -->
        <template v-else-if="isAdmin">
          <router-link to="/admin" class="btn btn-primary btn-sm navbar__action-desktop">管理后台</router-link>
          <button class="btn btn-ghost btn-sm navbar__action-desktop" @click="logout">退出</button>
        </template>
      </div>

      <button class="navbar__hamburger" @click="mobileMenuOpen = !mobileMenuOpen" aria-label="菜单">
        <span :class="{ 'open': mobileMenuOpen }" />
        <span :class="{ 'open': mobileMenuOpen }" />
        <span :class="{ 'open': mobileMenuOpen }" />
      </button>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const scrolled = ref(false)
const mobileMenuOpen = ref(false)

function onScroll() { scrolled.value = window.scrollY > 30 }
onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))

const loginInfo = computed(() => {
  try {
    const info = sessionStorage.getItem('loginInfo')
    return info ? JSON.parse(info) : null
  } catch { return null }
})

const isLoggedIn = computed(() => !!loginInfo.value)
const isUser = computed(() => loginInfo.value?.role === 'user')
const isAdmin = computed(() => loginInfo.value?.role === 'admin')
const userInitial = computed(() => (loginInfo.value?.username || 'U')[0].toUpperCase())

function closeMobile() { mobileMenuOpen.value = false }

function logout() {
  sessionStorage.removeItem('loginInfo')
  router.push('/')
  if (route.path === '/admin') router.go(0)
}
</script>

<style scoped>
.navbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
  padding: 0 40px; transition: all var(--t-base) var(--ease-out);
  background: transparent;
  border-bottom: 1px solid transparent;
}
.navbar--scrolled {
  background: rgba(10, 10, 18, 0.88);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom-color: var(--border-light);
}
.navbar__inner {
  max-width: var(--max-width); margin: 0 auto;
  display: flex; align-items: center; justify-content: space-between;
  height: var(--navbar-height);
}
.navbar__brand {
  display: flex; align-items: center; gap: 10px;
  text-decoration: none; color: inherit;
}
.navbar__logo { display: flex; align-items: center; }
.navbar__name {
  font-size: 17px; font-weight: 700; color: var(--text-primary);
  letter-spacing: -0.01em;
}
.navbar__links { display: flex; gap: 4px; }
.navbar__link {
  padding: 8px 16px; border-radius: var(--r-sm);
  font-size: 14px; font-weight: 500; color: var(--text-secondary);
  text-decoration: none; transition: all var(--t-fast) var(--ease-out);
}
.navbar__link:hover {
  color: var(--text-primary); background: rgba(255,255,255,0.04);
}
.navbar__actions { display: flex; align-items: center; gap: 10px; }

.navbar__avatar { display: flex; align-items: center; text-decoration: none; }
.avatar-circle {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--accent-gradient);
  display: flex; align-items: center; justify-content: center;
  font-size: 15px; font-weight: 700; color: #0A0A12;
  cursor: pointer; transition: all var(--t-fast) var(--ease-out);
}
.avatar-circle:hover {
  box-shadow: 0 0 0 2px rgba(0, 212, 170, 0.3);
  transform: scale(1.05);
}

/* Hamburger button */
.navbar__hamburger {
  display: none; flex-direction: column; gap: 5px;
  background: none; border: none; cursor: pointer; padding: 8px;
}
.navbar__hamburger span {
  width: 22px; height: 2px; border-radius: 2px;
  background: var(--text-primary);
  transition: all 0.3s var(--ease-out);
}
.navbar__hamburger span.open:nth-child(1) { transform: translateY(7px) rotate(45deg); }
.navbar__hamburger span.open:nth-child(2) { opacity: 0; }
.navbar__hamburger span.open:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }

@media (max-width: 860px) {
  .navbar { padding: 0 20px; }
  .navbar__links {
    position: absolute; top: var(--navbar-height); left: 0; right: 0;
    flex-direction: column; gap: 0;
    background: rgba(10, 10, 18, 0.95);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border-light);
    max-height: 0; overflow: hidden;
    transition: max-height 0.3s var(--ease-out);
  }
  .navbar__links--open { max-height: 320px; }
  .navbar__links .navbar__link {
    padding: 14px 24px; border-radius: 0;
    border-bottom: 1px solid var(--border-light);
  }
  .navbar__action-desktop { display: none; }
  .navbar__hamburger { display: flex; }
}
</style>
