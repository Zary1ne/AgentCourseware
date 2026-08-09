<template>
  <section id="how-it-works" class="process">
    <div class="process__inner">
      <div class="process__header" v-scroll-in>
        <span class="section-label">工作流程</span>
        <h2 class="process__title">构建 · 测试 · 部署 · 监控</h2>
        <p class="process__subtitle">从知识库构建到课件生成，全流程 AI 驱动，一站式教学准备</p>
      </div>

      <div class="process__flow">
        <div v-for="(step, i) in steps" :key="step.title" class="process-step" v-scroll-in="{ delay: i * 100 }">
          <div class="process-step__icon">
            <component :is="step.icon" />
          </div>
          <h3 class="process-step__title">{{ step.title }}</h3>
          <p class="process-step__desc">{{ step.desc }}</p>
        </div>
      </div>

      <div class="process__connector">
        <div class="process__connector-line" />
      </div>
    </div>
  </section>
</template>

<script setup>
import { h } from 'vue'

const BuildIcon = {
  render() {
    return h('svg', { width: 24, height: 24, viewBox: '0 0 24 24', fill: 'none' }, [
      h('rect', { x: 2, y: 3, width: 20, height: 18, rx: 2, stroke: 'currentColor', 'stroke-width': 1.5 }),
      h('path', { d: 'M7 8h10M7 12h8M7 16h5', stroke: 'currentColor', 'stroke-width': 1.2, 'stroke-linecap': 'round' })
    ])
  }
}

const TestIcon = {
  render() {
    return h('svg', { width: 24, height: 24, viewBox: '0 0 24 24', fill: 'none' }, [
      h('path', { d: 'M9 11l3 3L22 4', stroke: 'currentColor', 'stroke-width': 1.5, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }),
      h('path', { d: 'M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11', stroke: 'currentColor', 'stroke-width': 1.5, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
    ])
  }
}

const DeployIcon = {
  render() {
    return h('svg', { width: 24, height: 24, viewBox: '0 0 24 24', fill: 'none' }, [
      h('circle', { cx: 12, cy: 12, r: 9, stroke: 'currentColor', 'stroke-width': 1.5 }),
      h('path', { d: 'M12 2v4M12 18v4M2 12h4M18 12h4', stroke: 'currentColor', 'stroke-width': 1.5, 'stroke-linecap': 'round' }),
      h('circle', { cx: 12, cy: 12, r: 3, stroke: 'currentColor', 'stroke-width': 1.2 })
    ])
  }
}

const MonitorIcon = {
  render() {
    return h('svg', { width: 24, height: 24, viewBox: '0 0 24 24', fill: 'none' }, [
      h('path', { d: 'M3 3v13h18V3H3z', stroke: 'currentColor', 'stroke-width': 1.5, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }),
      h('path', { d: 'M8 21h8M12 16v5', stroke: 'currentColor', 'stroke-width': 1.5, 'stroke-linecap': 'round' }),
      h('path', { d: 'M7 9l2 2 3-3 5 5', stroke: 'currentColor', 'stroke-width': 1.5, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
    ])
  }
}

const steps = [
  { icon: BuildIcon, title: '构建', desc: '上传教学资料，AI 自动解析并构建知识库，理解你的教学意图' },
  { icon: TestIcon, title: '测试', desc: '多轮对话迭代，精调教学方案，确保内容准确性与完整性' },
  { icon: DeployIcon, title: '部署', desc: '一键生成 PPT 课件、Word 教案与互动测验，多种格式导出' },
  { icon: MonitorIcon, title: '监控', desc: '实时追踪教学效果，数据分析反馈，持续优化备课质量' },
]
</script>

<style scoped>
.process {
  padding: 80px 40px; background: var(--bg-surface);
}
.process__inner {
  max-width: var(--max-width); margin: 0 auto; position: relative;
}

.process__header { text-align: center; margin-bottom: 48px; }
.process__title {
  font-size: clamp(32px, 4vw, 44px); font-weight: 700;
  letter-spacing: -0.015em; color: var(--text-primary); margin-bottom: 12px;
}
.process__subtitle {
  font-size: 17px; color: var(--text-secondary); max-width: 540px; margin: 0 auto;
}

.process__flow {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 32px;
  position: relative; z-index: 1;
}
.process__connector {
  position: absolute; top: 260px; left: 60px; right: 60px;
  z-index: 0; display: block;
}
.process__connector-line {
  height: 1.5px; background: var(--border-default); position: relative;
}
.process__connector-line::after {
  content: ''; position: absolute; right: -4px; top: -3px;
  width: 8px; height: 8px; border-radius: 50%; background: var(--accent);
}

.process-step {
  position: relative; z-index: 1; text-align: center;
  display: flex; flex-direction: column; align-items: center; padding: 0 12px;
}
.process-step__icon {
  display: flex; align-items: center; justify-content: center;
  width: 64px; height: 64px; border-radius: 16px; margin-bottom: 24px;
  background: var(--bg-card); border: 1px solid var(--border-default);
  box-shadow: var(--shadow-md); color: var(--accent);
  transition: all var(--t-base) var(--ease-out);
}
.process-step:hover .process-step__icon {
  transform: translateY(-4px); box-shadow: var(--shadow-lg); border-color: var(--border-accent);
}
.process-step__title {
  font-size: 18px; font-weight: 700; letter-spacing: -0.015em;
  color: var(--text-primary); margin-bottom: 8px;
}
.process-step__desc {
  font-size: 14px; color: var(--text-secondary); line-height: 1.65; max-width: 220px;
}

@media (max-width: 900px) {
  .process__flow { grid-template-columns: repeat(2, 1fr); gap: 40px 24px; }
  .process__connector { display: none; }
}
@media (max-width: 520px) {
  .process__flow { grid-template-columns: 1fr; }
}
</style>
