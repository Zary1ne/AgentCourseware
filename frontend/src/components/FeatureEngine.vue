<template>
  <section class="engine">
    <div class="engine__inner">
      <div class="engine__text" v-scroll-in>
        <span class="section-label">核心引擎</span>
        <h2 class="engine__title">
          Teaching Agent Engine
          <span class="engine__title-accent">知识驱动</span>
          的智能教学平台
        </h2>
        <p class="engine__desc">
          基于 RAG 增强检索技术，融合大语言模型能力，实现从教学意图理解到课件自动生成的全链路闭环。支持多格式文档解析、知识图谱构建、智能对话迭代，让每一次备课都高效精准。
        </p>
        <div class="engine__features">
          <div v-for="f in features" :key="f.title" class="engine-feat">
            <div class="engine-feat__icon">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M4 9.5l3 3 7-7" stroke="var(--accent)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div>
              <h4 class="engine-feat__title">{{ f.title }}</h4>
              <p class="engine-feat__desc">{{ f.desc }}</p>
            </div>
          </div>
        </div>
        <a href="#" class="engine__link">
          了解更多
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </a>
      </div>

      <!-- Dark data panel -->
      <div class="engine__panel animate-in anim-d1">
        <div class="engine-card">
          <div class="engine-card__header">
            <div class="engine-card__title-row">
              <span class="engine-card__dot engine-card__dot--green" />
              <span class="engine-card__title">Agent Loop Monitor</span>
            </div>
            <span class="badge badge-success">Active</span>
          </div>

          <div class="engine-card__metrics">
            <div class="eng-metric">
              <span class="eng-metric__label">Avg Latency</span>
              <span class="eng-metric__value">142<span class="eng-metric__unit">ms</span></span>
            </div>
            <div class="eng-metric">
              <span class="eng-metric__label">Success Rate</span>
              <span class="eng-metric__value">99.7<span class="eng-metric__unit">%</span></span>
            </div>
            <div class="eng-metric">
              <span class="eng-metric__label">Tokens/s</span>
              <span class="eng-metric__value">3.2<span class="eng-metric__unit">k</span></span>
            </div>
          </div>

          <div class="engine-card__traces">
            <div class="eng-trace">
              <span class="eng-trace__status eng-trace__status--ok" />
              <span class="eng-trace__op">document.parse</span>
              <span class="eng-trace__dur">34ms</span>
            </div>
            <div class="eng-trace">
              <span class="eng-trace__status eng-trace__status--ok" />
              <span class="eng-trace__op">rag.retrieve</span>
              <span class="eng-trace__dur">56ms</span>
            </div>
            <div class="eng-trace">
              <span class="eng-trace__status eng-trace__status--warn" />
              <span class="eng-trace__op">llm.generate</span>
              <span class="eng-trace__dur">128ms</span>
            </div>
            <div class="eng-trace">
              <span class="eng-trace__status eng-trace__status--ok" />
              <span class="eng-trace__op">ppt.compose</span>
              <span class="eng-trace__dur">210ms</span>
            </div>
            <div class="eng-trace">
              <span class="eng-trace__status eng-trace__status--error" />
              <span class="eng-trace__op">export.render</span>
              <span class="eng-trace__dur">—</span>
              <span class="eng-trace__badge">Retrying...</span>
            </div>
          </div>

          <div class="engine-card__code">
            <div class="eng-code__header">
              <span class="eng-code__dot eng-code__dot--red" />
              <span class="eng-code__dot eng-code__dot--yellow" />
              <span class="eng-code__dot eng-code__dot--green" />
              <span class="eng-code__label">fix.py</span>
            </div>
            <pre class="eng-code__body"><code><span class="c-keyword">async def</span> <span class="c-func">handle_export_error</span>(trace):
    <span class="c-comment"># Auto-retry on render failure</span>
    <span class="c-keyword">if</span> trace.status == <span class="c-str">"error"</span>:
        <span class="c-keyword">await</span> retry(trace, max_attempts=<span class="c-num">3</span>)
        log.info(<span class="c-str">f"Recovered trace </span><span class="c-var">{trace.id}</span><span class="c-str">"</span>)</code></pre>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const features = [
  { title: 'RAG 增强检索', desc: '向量化知识库，精准匹配教学内容' },
  { title: '多格式解析', desc: '支持 PDF、Word、PPT、图片等多种文件格式' },
  { title: '智能对话迭代', desc: '多轮对话理解意图，动态调整教学方案' },
  { title: '一键课件生成', desc: 'PPT、教案、互动测验同步输出' },
]
</script>

<style scoped>
.engine {
  padding: 80px 40px; background: var(--bg-page);
}
.engine__inner {
  max-width: var(--max-width); margin: 0 auto;
  display: grid; grid-template-columns: 1fr 1fr; gap: 80px; align-items: center;
}

.engine__text { display: flex; flex-direction: column; }

.engine__title {
  font-size: clamp(28px, 3.5vw, 42px); font-weight: 700;
  letter-spacing: -0.015em; line-height: 1.18;
  color: var(--text-primary); margin-bottom: 20px;
}
.engine__title-accent { color: var(--accent); }

.engine__desc {
  font-size: 16px; color: var(--text-secondary); line-height: 1.65;
  margin-bottom: 36px;
}

.engine__features {
  display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 36px;
}
.engine-feat { display: flex; gap: 12px; align-items: flex-start; }
.engine-feat__icon { flex-shrink: 0; margin-top: 1px; }
.engine-feat__title {
  font-size: 14px; font-weight: 600; color: var(--text-primary);
  margin-bottom: 2px; letter-spacing: -0.01em;
}
.engine-feat__desc {
  font-size: 13px; color: var(--text-secondary); line-height: 1.5;
}

.engine__link {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 15px; font-weight: 600; color: var(--accent);
  text-decoration: none; transition: all var(--t-fast) var(--ease-out);
}
.engine__link:hover { gap: 10px; color: var(--accent-hover); }

/* Dark panel */
.engine__panel { display: flex; justify-content: center; }
.engine-card {
  width: 100%; max-width: 480px;
  background: #0E0E1E; border-radius: var(--r-lg);
  padding: 28px; display: flex; flex-direction: column; gap: 20px;
  box-shadow: var(--shadow-xl); border: 1px solid rgba(255,255,255,0.05);
}

.engine-card__header {
  display: flex; align-items: center; justify-content: space-between;
}
.engine-card__title-row { display: flex; align-items: center; gap: 10px; }
.engine-card__dot {
  width: 8px; height: 8px; border-radius: 50%;
}
.engine-card__dot--green {
  background: #34D399; box-shadow: 0 0 8px rgba(52, 211, 153, 0.4);
}
.engine-card__title {
  font-size: 14px; font-weight: 600; color: rgba(255,255,255,0.85);
  letter-spacing: -0.01em;
}

.engine-card__metrics {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;
}
.eng-metric {
  background: rgba(255,255,255,0.03); border-radius: var(--r-sm);
  padding: 14px; display: flex; flex-direction: column; gap: 4px;
  border: 1px solid rgba(255,255,255,0.05);
}
.eng-metric__label {
  font-size: 11px; color: rgba(255,255,255,0.35);
  font-weight: 500; letter-spacing: 0.02em;
}
.eng-metric__value {
  font-size: 22px; font-weight: 700; color: var(--text-inverse);
  letter-spacing: -0.02em; font-family: var(--font-mono);
}
.eng-metric__unit {
  font-size: 13px; font-weight: 500; color: rgba(255,255,255,0.45); margin-left: 2px;
}

.engine-card__traces { display: flex; flex-direction: column; gap: 6px; }
.eng-trace {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 12px; border-radius: var(--r-xs);
  background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);
}
.eng-trace__status { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.eng-trace__status--ok { background: #34D399; }
.eng-trace__status--warn { background: #FBBF24; }
.eng-trace__status--error { background: #F87171; }
.eng-trace__op {
  flex: 1; font-size: 12.5px; color: rgba(255,255,255,0.7);
  font-family: var(--font-mono);
}
.eng-trace__dur {
  font-size: 12px; color: rgba(255,255,255,0.35); font-family: var(--font-mono);
}
.eng-trace__badge {
  font-size: 10px; font-weight: 600; color: #FBBF24;
  background: rgba(251, 191, 36, 0.1); padding: 2px 8px;
  border-radius: 99px; font-family: var(--font-sans);
}

.engine-card__code {
  background: #060610; border-radius: var(--r-sm);
  overflow: hidden; border: 1px solid rgba(255,255,255,0.04);
}
.eng-code__header {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px; border-bottom: 1px solid rgba(255,255,255,0.04);
}
.eng-code__dot { width: 10px; height: 10px; border-radius: 50%; }
.eng-code__dot--red { background: #FF5F57; }
.eng-code__dot--yellow { background: #FFBD2E; }
.eng-code__dot--green { background: #27CA40; }
.eng-code__label {
  font-size: 11px; color: rgba(255,255,255,0.3);
  font-family: var(--font-mono); margin-left: 8px;
}
.eng-code__body {
  padding: 16px; margin: 0; overflow-x: auto;
  font-family: var(--font-mono); font-size: 12.5px;
  line-height: 1.7; color: rgba(255,255,255,0.75);
}
.eng-code__body code { font-family: inherit; background: none; padding: 0; }
.c-keyword { color: #C792EA; }
.c-func { color: #82AAFF; }
.c-comment { color: #546E7A; font-style: italic; }
.c-str { color: #C3E88D; }
.c-num { color: #F78C6C; }
.c-var { color: #EEFFFF; }

@media (max-width: 960px) {
  .engine__inner { grid-template-columns: 1fr; gap: 48px; }
  .engine__features { grid-template-columns: 1fr; }
}
</style>
