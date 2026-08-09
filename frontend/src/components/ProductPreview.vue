<template>
  <section class="preview-section">
    <div class="preview-section__inner">
      <!-- Dashboard mockup that overlaps with Hero bottom -->
      <div class="preview-mockup" v-scroll-in>
        <!-- Mockup header -->
        <div class="mockup-bar">
          <div class="mockup-dots">
            <span class="mockup-dot mockup-dot--red" />
            <span class="mockup-dot mockup-dot--yellow" />
            <span class="mockup-dot mockup-dot--green" />
          </div>
          <span class="mockup-title">Teaching Agent — 工作台</span>
          <span class="mockup-badge">实时预览</span>
        </div>

        <!-- Mockup body: 3-panel layout -->
        <div class="mockup-body">
          <!-- Left: AI Chat panel -->
          <div class="mockup-panel mockup-panel--chat">
            <div class="mockup-panel__header">
              <span class="mockup-panel__dot" />
              AI 教学助手
            </div>
            <div class="mockup-chat">
              <div class="mockup-msg mockup-msg--user">帮我生成高一物理牛顿定律的课件</div>
              <div class="mockup-msg mockup-msg--ai">
                <span class="mockup-typing"><span /><span /><span /></span>
              </div>
              <div class="mockup-msg mockup-msg--ai">已为您生成课件大纲，包含 12 张幻灯片...</div>
            </div>
            <div class="mockup-input">
              <span class="mockup-input__placeholder">发消息...</span>
              <span class="mockup-input__send">→</span>
            </div>
          </div>

          <!-- Center: Slide preview -->
          <div class="mockup-panel mockup-panel--slides">
            <div class="mockup-panel__header">
              <span class="mockup-panel__dot mockup-panel__dot--accent" />
              课件预览
            </div>
            <div class="mockup-slides">
              <div v-for="(slide, i) in slides" :key="i" :class="['mockup-slide', { 'mockup-slide--active': i === 0 }]">
                <div class="mockup-slide__bar" :style="{ background: slide.color }" />
                <div class="mockup-slide__content">
                  <span class="mockup-slide__label">{{ slide.label }}</span>
                  <div class="mockup-slide__lines">
                    <div class="mockup-line" v-for="n in slide.lines" :key="n" :style="{ width: n * 30 + '%' }" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Right: Stats panel -->
          <div class="mockup-panel mockup-panel--stats">
            <div class="mockup-panel__header">
              <span class="mockup-panel__dot mockup-panel__dot--green" />
              实时数据
            </div>
            <div class="mockup-stats">
              <div class="mockup-stat">
                <span class="mockup-stat__value">142<span class="mockup-stat__unit">ms</span></span>
                <span class="mockup-stat__label">平均延迟</span>
              </div>
              <div class="mockup-stat">
                <span class="mockup-stat__value">99.7<span class="mockup-stat__unit">%</span></span>
                <span class="mockup-stat__label">成功率</span>
              </div>
              <div class="mockup-stat">
                <span class="mockup-stat__value">3.2<span class="mockup-stat__unit">k</span></span>
                <span class="mockup-stat__label">Tokens/s</span>
              </div>
            </div>
            <div class="mockup-chart">
              <svg viewBox="0 0 200 60" class="mockup-chart__svg">
                <path d="M0,45 Q25,30 50,35 T100,20 T150,25 T200,10" stroke="var(--accent)" stroke-width="1.5" fill="none" stroke-linecap="round" />
                <path d="M0,45 Q25,30 50,35 T100,20 T150,25 T200,10 L200,60 L0,60 Z" fill="url(#chartGrad)" />
                <defs>
                  <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="rgba(0,212,170,0.15)" />
                    <stop offset="100%" stop-color="rgba(0,212,170,0)" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const slides = [
  { label: '封面', lines: [3, 2], color: 'var(--accent)' },
  { label: '目录', lines: [4, 3, 2], color: 'var(--accent-secondary)' },
  { label: '正文', lines: [3, 3, 2, 1], color: 'var(--accent-tertiary)' },
  { label: '正文', lines: [3, 2, 2], color: 'var(--accent)' },
]
</script>

<style scoped>
.preview-section {
  background: var(--bg-page);
  padding: 0 40px 80px;
  margin-top: -60px;
  position: relative;
  z-index: 2;
}
.preview-section__inner {
  max-width: var(--max-width); margin: 0 auto;
}

.preview-mockup {
  background: #0E0E1E; border-radius: var(--r-xl);
  border: 1px solid var(--border-light);
  overflow: hidden; box-shadow: var(--shadow-xl);
}

.mockup-bar {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 18px; background: rgba(255,255,255,0.02);
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.mockup-dots { display: flex; gap: 7px; }
.mockup-dot { width: 11px; height: 11px; border-radius: 50%; }
.mockup-dot--red { background: #FF5F57; }
.mockup-dot--yellow { background: #FFBD2E; }
.mockup-dot--green { background: #27CA40; }
.mockup-title {
  font-size: 12px; color: rgba(255,255,255,0.4); font-weight: 500;
  font-family: var(--font-mono); margin-left: 8px;
}
.mockup-badge {
  margin-left: auto; font-size: 11px; padding: 3px 10px;
  border-radius: 99px; background: var(--accent-light);
  color: var(--accent); font-weight: 600;
}

.mockup-body {
  display: grid; grid-template-columns: 1fr 1.2fr 0.8fr; gap: 1px;
  background: rgba(255,255,255,0.04); min-height: 320px;
}

.mockup-panel {
  background: #0E0E1E; padding: 16px; display: flex; flex-direction: column; gap: 12px;
}
.mockup-panel__header {
  display: flex; align-items: center; gap: 8px;
  font-size: 12px; font-weight: 600; color: rgba(255,255,255,0.6);
}
.mockup-panel__dot { width: 7px; height: 7px; border-radius: 50%; background: var(--accent-secondary); }
.mockup-panel__dot--accent { background: var(--accent); }
.mockup-panel__dot--green { background: #34D399; }

/* Chat panel */
.mockup-chat { display: flex; flex-direction: column; gap: 8px; flex: 1; }
.mockup-msg {
  font-size: 11px; padding: 8px 12px; border-radius: 10px;
  max-width: 85%; line-height: 1.5;
}
.mockup-msg--user {
  align-self: flex-end; background: var(--accent); color: #0A0A12;
}
.mockup-msg--ai {
  align-self: flex-start; background: rgba(255,255,255,0.04);
  color: rgba(255,255,255,0.7); border: 1px solid rgba(255,255,255,0.05);
}
.mockup-typing { display: flex; gap: 3px; padding: 2px 0; }
.mockup-typing span {
  width: 5px; height: 5px; border-radius: 50%; background: var(--accent);
  animation: mockup-pulse 1.4s infinite;
}
.mockup-typing span:nth-child(2) { animation-delay: 0.2s; }
.mockup-typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes mockup-pulse { 0%,60%,100% { opacity: 0.3; transform: scale(0.8); } 30% { opacity: 1; transform: scale(1); } }

.mockup-input {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 12px; background: rgba(255,255,255,0.03);
  border-radius: 20px; border: 1px solid rgba(255,255,255,0.06);
}
.mockup-input__placeholder { font-size: 11px; color: rgba(255,255,255,0.25); }
.mockup-input__send { font-size: 14px; color: var(--accent); font-weight: 600; }

/* Slides panel */
.mockup-slides { display: flex; flex-direction: column; gap: 8px; flex: 1; }
.mockup-slide {
  display: flex; gap: 10px; padding: 10px;
  background: rgba(255,255,255,0.02); border-radius: var(--r-sm);
  border: 1px solid rgba(255,255,255,0.04);
  transition: all 0.3s var(--ease-out);
}
.mockup-slide--active { border-color: rgba(0,212,170,0.2); background: rgba(0,212,170,0.03); }
.mockup-slide__bar { width: 3px; border-radius: 2px; flex-shrink: 0; }
.mockup-slide__content { display: flex; flex-direction: column; gap: 4px; flex: 1; }
.mockup-slide__label { font-size: 10px; font-weight: 600; color: rgba(255,255,255,0.4); }
.mockup-slide__lines { display: flex; flex-direction: column; gap: 3px; }
.mockup-line { height: 3px; border-radius: 2px; background: rgba(255,255,255,0.08); }

/* Stats panel */
.mockup-stats { display: flex; flex-direction: column; gap: 10px; }
.mockup-stat { display: flex; flex-direction: column; gap: 2px; }
.mockup-stat__value {
  font-size: 18px; font-weight: 700; color: rgba(255,255,255,0.9);
  font-family: var(--font-mono); letter-spacing: -0.02em;
}
.mockup-stat__unit { font-size: 11px; color: rgba(255,255,255,0.35); margin-left: 2px; font-weight: 500; }
.mockup-stat__label { font-size: 10px; color: rgba(255,255,255,0.35); }

.mockup-chart { margin-top: auto; }
.mockup-chart__svg { width: 100%; height: 60px; }

@media (max-width: 900px) {
  .mockup-body { grid-template-columns: 1fr; }
  .preview-section { margin-top: -30px; }
}
</style>
