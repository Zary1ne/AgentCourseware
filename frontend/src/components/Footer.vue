<template>
  <footer id="contact" class="footer">
    <div class="footer__inner">
      <div class="footer__grid">
        <div class="footer__brand">
          <div class="footer__logo">
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <rect width="28" height="28" rx="6" fill="var(--accent)"/>
              <path d="M5 10h18M5 14h14M5 18h10" stroke="#0A0A12" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </div>
          <span class="footer__name">Teaching Agent</span>
          <p class="footer__desc">AI 驱动的智能教学备课平台 — 让每一堂课都更高效。</p>
          <div class="footer__social">
            <a href="#" aria-label="GitHub">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.385-1.335-1.755-1.335-1.755-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.605-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 21.795 24 17.295 24 12c0-6.63-5.37-12-12-12z"/></svg>
            </a>
            <a href="#" aria-label="Twitter">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
            </a>
          </div>
        </div>

        <div class="footer__col">
          <h4>产品</h4>
          <router-link to="/app">工作台</router-link>
          <a href="#stats">仪表盘</a>
          <a href="#featured">开源社区</a>
          <a href="#how-it-works">工作流程</a>
        </div>
        <div class="footer__col">
          <h4>资源</h4>
          <a href="#">使用文档</a>
          <a href="#">API 参考</a>
          <a href="#">更新日志</a>
          <a href="#">帮助中心</a>
        </div>
        <div class="footer__col">
          <h4>公司</h4>
          <a href="#">关于我们</a>
          <a href="#">博客</a>
          <a href="#">加入我们</a>
          <a href="mailto:contact@teaching-agent.ai">联系我们</a>
        </div>
      </div>

      <div class="footer__bottom">
        <span class="footer__copy">&copy; {{ year }} Teaching Agent. All rights reserved.</span>
        <div class="footer__legal">
          <a href="#">隐私政策</a>
          <a href="#">服务条款</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
const year = new Date().getFullYear()
</script>

<style scoped>
.footer { padding: 80px 40px 32px; background: var(--bg-surface); border-top: 1px solid var(--border-light); }
.footer__inner { max-width: var(--max-width); margin: 0 auto; }
.footer__grid { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 56px; margin-bottom: 56px; }

.footer__brand { display: flex; flex-direction: column; gap: 14px; }
.footer__logo { margin-bottom: 4px; }
.footer__name { font-size: 18px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.01em; }
.footer__desc { font-size: 14px; color: var(--text-secondary); line-height: 1.65; max-width: 280px; }

.footer__social { display: flex; gap: 14px; margin-top: 4px; }
.footer__social a { color: var(--text-tertiary); transition: color var(--t-fast); display: flex; }
.footer__social a:hover { color: var(--text-primary); }

.footer__col { display: flex; flex-direction: column; gap: 13px; }
.footer__col h4 { font-size: 12px; font-weight: 600; color: var(--text-tertiary); letter-spacing: 0.06em; text-transform: uppercase; }
.footer__col a { font-size: 14px; color: var(--text-secondary); text-decoration: none; transition: color var(--t-fast) var(--ease-out); }
.footer__col a:hover { color: var(--accent); }

.footer__bottom { display: flex; justify-content: space-between; align-items: center; padding-top: 28px; border-top: 1px solid var(--border-light); }
.footer__copy { font-size: 13px; color: var(--text-tertiary); }
.footer__legal { display: flex; gap: 20px; }
.footer__legal a { font-size: 13px; color: var(--text-tertiary); text-decoration: none; }
.footer__legal a:hover { color: var(--text-primary); }

@media (max-width: 800px) {
  .footer__grid { grid-template-columns: repeat(2, 1fr); gap: 36px; }
}
</style>
