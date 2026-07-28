<template>
  <section class="hero">
    <div class="hero__inner">
      <div class="hero__badge animate-in">
        <span class="hero__badge-dot" />
        AI-Powered Teaching Platform
      </div>
      <h1 class="hero__title animate-in anim-d1">
        智能<span class="hero__accent">教学引擎</span>
        <br />
        重塑教育未来
      </h1>
      <p class="hero__desc animate-in anim-d2">
        上传文档、构建知识库、一键生成完整教学方案 — PPT课件、教案讲义、互动测验，
        AI 全流程驱动，为教育工作者打造新一代智能备课体验。
      </p>
      <div class="hero__cta animate-in anim-d3">
        <router-link to="/app" class="btn btn-primary btn-lg">
          免费开始使用
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <path d="M4 9h10M11 5l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </router-link>
        <a href="#how-it-works" class="btn btn-secondary btn-lg">了解更多</a>
      </div>

      <div class="hero__trust animate-in anim-d4">
        <span></span>
        <span class="hero__trust-divider">·</span>
        <span></span>
        <span class="hero__trust-divider">·</span>
        <span></span>
      </div>
    </div>

    <div class="hero__bg">
      <div class="hero__glow hero__glow--1" />
      <div class="hero__glow hero__glow--2" />
    </div>
  </section>
</template>

<style scoped>
.hero {
  position: relative; min-height: 100vh; display: flex;
  align-items: center; justify-content: center; overflow: hidden;
  background: var(--bg-page);
  padding: 100px 32px 80px;
}

.hero__bg {
  position: absolute; inset: 0; z-index: 0; pointer-events: none;
}
.hero__glow {
  position: absolute; border-radius: 50%; filter: blur(140px);
}
.hero__glow--1 {
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(0, 212, 170, 0.06), transparent 70%);
  top: -15%; left: -10%;
}
.hero__glow--2 {
  width: 450px; height: 450px;
  background: radial-gradient(circle, rgba(0, 212, 170, 0.04), transparent 70%);
  bottom: 5%; right: -8%;
}

.hero__inner {
  position: relative; z-index: 2; text-align: center;
  max-width: 780px; display: flex; flex-direction: column; align-items: center;
}

.hero__badge {
  display: inline-flex; align-items: center; gap: 8px;
  font-size: 12px; font-weight: 600; letter-spacing: 0.06em;
  color: var(--accent); font-family: var(--font-sans);
  margin-bottom: 28px; padding: 8px 20px; border-radius: 99px;
  background: var(--accent-light); border: 1px solid var(--border-accent);
}
.hero__badge-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--accent);
}

.hero__title {
  font-size: clamp(48px, 7vw, 76px); font-weight: 800;
  letter-spacing: -0.035em; line-height: 1.08;
  color: var(--text-primary); margin-bottom: 24px;
}
.hero__accent { color: var(--accent); }

.hero__desc {
  font-size: 18px; line-height: 1.75; color: var(--text-secondary);
  max-width: 580px; margin-bottom: 40px;
}

.hero__cta {
  display: flex; gap: 14px; flex-wrap: wrap; justify-content: center;
  margin-bottom: 48px;
}

.hero__trust {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; color: var(--text-tertiary); font-weight: 500;
}
.hero__trust-divider { color: var(--border-strong); }
</style>
