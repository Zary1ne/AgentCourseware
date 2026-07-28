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

      <nav class="navbar__links">
        <a href="#" class="navbar__link">产品</a>
        <a href="#" class="navbar__link">学习</a>
        <a href="#" class="navbar__link">文档</a>
        <a href="#" class="navbar__link">公司</a>
        <a href="#" class="navbar__link">定价</a>
      </nav>

      <div class="navbar__actions">
        <router-link to="/app" class="btn btn-primary btn-sm">开始使用</router-link>
        <a href="#contact" class="btn btn-secondary btn-sm">预约演示</a>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
const scrolled = ref(false)
function onScroll() { scrolled.value = window.scrollY > 30 }
onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
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
  letter-spacing: -0.02em;
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

@media (max-width: 860px) {
  .navbar__links { display: none; }
  .navbar { padding: 0 20px; }
}
</style>
