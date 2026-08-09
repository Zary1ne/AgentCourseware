<template>
  <section class="cta">
    <div class="cta__inner">
      <h2 class="cta__title">准备好开始了吗？</h2>
      <p class="cta__desc">
        加入 200+ 教育机构，体验 AI 驱动的智能备课平台
      </p>
      <div class="cta__actions">
        <router-link to="/app" class="btn btn-primary btn-lg">
          免费开始使用
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <path d="M4 9h10M11 5l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </router-link>
        <a href="#contact" class="btn btn-outline-light btn-lg">预约演示</a>
      </div>
      <p class="cta__note">无需信用卡 · 免费试用 · 随时取消</p>
    </div>
  </section>
</template>

<style scoped>
.cta {
  padding: 80px 40px; background: var(--bg-navy);
  position: relative; overflow: hidden;
}
.cta::before {
  content: ''; position: absolute; top: -30%; right: -10%;
  width: 500px; height: 500px; border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 212, 170, 0.06), transparent 70%);
  pointer-events: none;
}

.cta__inner {
  position: relative; z-index: 1;
  max-width: 640px; margin: 0 auto; text-align: center;
}
.cta__title {
  font-size: clamp(32px, 4vw, 44px); font-weight: 700;
  letter-spacing: -0.015em; color: var(--text-inverse); margin-bottom: 12px;
}
.cta__desc {
  font-size: 18px; color: rgba(255,255,255,0.55);
  line-height: 1.6; margin-bottom: 36px;
}
.cta__actions {
  display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; margin-bottom: 20px;
}
.cta__note { font-size: 13px; color: rgba(255,255,255,0.25); }
</style>
