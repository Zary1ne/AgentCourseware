<template>
  <section id="featured" class="featured">
    <div class="featured__inner">
      <div class="featured__header">
        <span class="section-label">精选案例</span>
        <h2 class="featured__title">AI 平台生成的优质教学材料</h2>
        <p class="featured__subtitle">来自真实教学场景，覆盖多学科、多课型的课件案例展示</p>
      </div>

      <div class="featured__grid">
        <article v-for="(p, i) in projects" :key="p.id" :class="['project-card', 'animate-in', i > 0 ? 'anim-d' + i : '']">
          <div class="project-card__top" :style="{ background: p.accent }" />
          <div class="project-card__body">
            <span class="project-card__cat">{{ p.category }}</span>
            <h3 class="project-card__title">{{ p.title }}</h3>
            <p class="project-card__desc">{{ p.description }}</p>
            <div class="project-card__footer">
              <div class="project-card__tags">
                <span v-for="tag in p.tags" :key="tag" class="badge badge-accent">{{ tag }}</span>
              </div>
              <span class="project-card__arrow">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </span>
            </div>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup>
const projects = [
  { id:1, title:'物理 · 牛顿第一定律', category:'完整课件包', accent:'linear-gradient(90deg, #00D4AA 0%, #00B894 100%)', description:'从教学意图出发，一键生成互动 PPT、讲义和随堂测验，含实验演示与课堂互动设计。', tags:['PPT课件','讲义','测验'] },
  { id:2, title:'数据结构 · 二叉树遍历', category:'讲义课件', accent:'linear-gradient(90deg, #00D4AA 0%, #00856A 100%)', description:'基于上传教材自动生成的课堂讲义，通过 RAG 增强内容，包含代码示例与可视化图解。', tags:['讲义','图解','示例代码'] },
  { id:3, title:'英语 · 议论文写作工坊', category:'互动课程', accent:'linear-gradient(90deg, #00D4AA 0%, #00E8BA 100%)', description:'结构化写作引导课程，包含范文分析、结构模板和同学互评评分表，全流程 AI 辅助。', tags:['写作引导','模板','评分表'] },
]
</script>

<style scoped>
.featured { padding: 100px 40px 120px; background: var(--bg-page); }
.featured__inner { max-width: var(--max-width); margin: 0 auto; }

.featured__header { text-align: center; margin-bottom: 56px; }
.featured__title { font-size: clamp(28px, 3.5vw, 40px); font-weight: 700; letter-spacing: -0.025em; color: var(--text-primary); margin-bottom: 10px; }
.featured__subtitle { font-size: 16px; color: var(--text-secondary); }

.featured__grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }

.project-card {
  background: var(--bg-card); border: 1px solid var(--border-light);
  border-radius: var(--r-lg); overflow: hidden;
  transition: all var(--t-base) var(--ease-out);
  display: flex; flex-direction: column;
}
.project-card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-lg); transform: translateY(-4px);
}

.project-card__top { height: 4px; flex-shrink: 0; }

.project-card__body { padding: 28px 24px 24px; display: flex; flex-direction: column; gap: 12px; flex: 1; }
.project-card__cat { font-size: 12px; font-weight: 600; color: var(--accent); letter-spacing: 0.03em; text-transform: uppercase; }
.project-card__title { font-size: 18px; font-weight: 700; letter-spacing: -0.015em; color: var(--text-primary); line-height: 1.3; }
.project-card__desc { font-size: 14px; color: var(--text-secondary); line-height: 1.7; flex: 1; }

.project-card__footer { display: flex; align-items: center; justify-content: space-between; margin-top: 4px; }
.project-card__tags { display: flex; gap: 6px; flex-wrap: wrap; }
.project-card__arrow { color: var(--text-tertiary); transition: all var(--t-fast) var(--ease-out); display: flex; }
.project-card:hover .project-card__arrow { color: var(--accent); transform: translateX(3px); }

@media (max-width: 1000px) { .featured__grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) { .featured__grid { grid-template-columns: 1fr; } }
</style>
