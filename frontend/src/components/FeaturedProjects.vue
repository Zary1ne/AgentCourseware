<template>
  <section id="featured" class="community">
    <div class="community__inner">
      <div class="community__header">
        <span class="section-label">开源社区</span>
        <h2 class="community__title">AI 课件开源共享平台</h2>
        <p class="community__subtitle">任何用户都可以将自己生成的课件上传到社区，按格式分类，与更多教育者共享优质教学资源</p>
      </div>

      <!-- 分类筛选 -->
      <div class="community__filters">
        <button v-for="cat in categories" :key="cat.value" :class="['filter-tag', { active: activeCategory === cat.value }]" @click="filterByCategory(cat.value)">
          {{ cat.label }}
        </button>
      </div>

      <!-- 上传按钮（仅登录用户可见） -->
      <div v-if="isLoggedIn" class="community__actions">
        <button class="btn btn-primary" @click="showUploadModal = true">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
          上传我的课件
        </button>
      </div>

      <!-- 课件列表 -->
      <div v-if="loading" class="community__loading">
        <span class="spinner"></span>
        <span class="text-tertiary">加载中...</span>
      </div>

      <div v-else-if="items.length === 0" class="community__empty">
        <p class="text-secondary">暂无课件，快来上传第一个吧！</p>
      </div>

      <div v-else class="community__grid">
        <article v-for="(item, i) in items" :key="item.id" :class="['project-card', 'card-spotlight']" v-scroll-in="{ delay: i * 80 }" @mousemove="onCardMove($event, i)" ref="cardRefs">
          <div class="project-card__top" :style="{ background: getAccent(item.category) }" />
          <div class="project-card__body">
            <div class="project-card__head">
              <span class="project-card__cat">{{ item.category }}</span>
              <span class="project-card__author">{{ item.author }}</span>
            </div>
            <h3 class="project-card__title">{{ item.title }}</h3>
            <p class="project-card__desc">{{ item.description || '暂无描述' }}</p>
            <div class="project-card__footer">
              <div class="project-card__tags">
                <span v-for="tag in (item.tags || [])" :key="tag" class="badge badge-accent">{{ tag }}</span>
              </div>
              <span class="project-card__time">{{ formatTime(item.created_at) }}</span>
            </div>
          </div>
        </article>
      </div>
    </div>

    <!-- 上传弹窗 -->
    <Teleport to="body">
      <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
        <div class="modal-content">
          <div class="modal-header">
            <h3>上传课件到开源社区</h3>
            <button class="modal-close" @click="showUploadModal = false">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M12 4L4 12M4 4l8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="field">
              <label class="field-label">课件标题 *</label>
              <input v-model="uploadForm.title" type="text" class="field-input" placeholder="请输入课件标题" />
            </div>
            <div class="field">
              <label class="field-label">课件文件 *</label>
              <div class="file-upload-area" :class="{ 'has-file': uploadForm.file }" @click="$refs.fileInput.click()">
                <div v-if="!uploadForm.file" class="file-upload-hint">
                  <svg width="28" height="28" viewBox="0 0 28 28" fill="none"><path d="M14 6v12M8 12h12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><rect x="3" y="3" width="22" height="22" rx="4" stroke="currentColor" stroke-width="1.2"/></svg>
                  <span>点击上传课件文件（PPT/Word/HTML/PDF）</span>
                </div>
                <div v-else class="file-upload-selected">
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect x="2" y="2" width="16" height="16" rx="3" stroke="currentColor" stroke-width="1.2"/><path d="M6 8h8M6 11h5" stroke="currentColor" stroke-width="1" stroke-linecap="round"/></svg>
                  <span class="file-name">{{ uploadForm.file.name }}</span>
                  <span class="file-size">{{ formatFileSize(uploadForm.file.size) }}</span>
                  <button class="file-remove" @click.stop="uploadForm.file = null; $refs.fileInput.value = ''">&times;</button>
                </div>
              </div>
              <input ref="fileInput" type="file" accept=".ppt,.pptx,.doc,.docx,.html,.pdf" class="file-input-hidden" @change="onFileSelected" />
            </div>
            <div class="field">
              <label class="field-label">分类</label>
              <select v-model="uploadForm.category" class="field-input">
                <option v-for="cat in uploadCategories" :key="cat.value" :value="cat.value">{{ cat.label }}</option>
              </select>
            </div>
            <div class="field">
              <label class="field-label">简介</label>
              <textarea v-model="uploadForm.description" class="field-input field-textarea" rows="3" placeholder="简要描述课件内容..."></textarea>
            </div>
            <div class="field">
              <label class="field-label">标签（用逗号分隔）</label>
              <input v-model="uploadForm.tagsStr" type="text" class="field-input" placeholder="如：PPT,物理,牛顿定律" />
            </div>
            <p v-if="uploadError" class="form-error">{{ uploadError }}</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showUploadModal = false">取消</button>
            <button class="btn btn-primary" @click="handleUpload" :disabled="uploadLoading">
              <span v-if="uploadLoading" class="spinner"></span>
              {{ uploadLoading ? '提交中...' : '提交审核' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getCommunityList, uploadCourseware } from '../api'

const cardRefs = ref([])
const items = ref([])
const loading = ref(true)
const activeCategory = ref('')

const categories = [
  { label: '全部', value: '' },
  { label: 'PPT课件', value: 'PPT课件' },
  { label: 'Word教案', value: 'Word教案' },
  { label: '互动课程', value: '互动课程' },
  { label: '完整课件包', value: '完整课件包' },
  { label: '其他', value: '其他' },
]

const uploadCategories = [
  { label: '请选择分类', value: '其他' },
  { label: 'PPT课件', value: 'PPT课件' },
  { label: 'Word教案', value: 'Word教案' },
  { label: '互动课程', value: '互动课程' },
  { label: '完整课件包', value: '完整课件包' },
  { label: '其他', value: '其他' },
]

// 上传弹窗
const showUploadModal = ref(false)
const uploadLoading = ref(false)
const uploadError = ref('')
const uploadForm = ref({
  title: '',
  category: '其他',
  description: '',
  tagsStr: '',
  file: null,
})

// 检查是否登录
const isLoggedIn = computed(() => {
  try {
    const info = sessionStorage.getItem('loginInfo')
    if (!info) return false
    const loginInfo = JSON.parse(info)
    return loginInfo.role === 'user'
  } catch { return false }
})

function getUserId() {
  try {
    const info = sessionStorage.getItem('loginInfo')
    return JSON.parse(info).userId
  } catch { return '' }
}

function onCardMove(e, i) {
  const card = cardRefs.value?.[i]
  if (!card) return
  const rect = card.getBoundingClientRect()
  card.style.setProperty('--mx', `${e.clientX - rect.left}px`)
  card.style.setProperty('--my', `${e.clientY - rect.top}px`)
}

function getAccent(category) {
  const map = {
    'PPT课件': 'linear-gradient(90deg, #00D4AA 0%, #00B894 100%)',
    'Word教案': 'linear-gradient(90deg, #6366f1 0%, #4f46e5 100%)',
    '互动课程': 'linear-gradient(90deg, #FBBF24 0%, #F59E0B 100%)',
    '完整课件包': 'linear-gradient(90deg, #F472B6 0%, #EC4899 100%)',
    '其他': 'linear-gradient(90deg, #A78BFA 0%, #8B5CF6 100%)',
  }
  return map[category] || map['其他']
}

function formatTime(iso) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
  } catch { return '' }
}

async function fetchItems() {
  loading.value = true
  try {
    const res = await getCommunityList(activeCategory.value || null)
    items.value = res.data.items || []
  } catch {
    items.value = []
  } finally {
    loading.value = false
  }
}

function filterByCategory(cat) {
  activeCategory.value = cat
  fetchItems()
}

function formatFileSize(bytes) {
  if (!bytes) return '0 B'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function onFileSelected(e) {
  const file = e.target.files?.[0]
  if (file) {
    uploadForm.value.file = file
  }
}

async function handleUpload() {
  uploadError.value = ''
  if (!uploadForm.value.title.trim()) { uploadError.value = '请输入课件标题'; return }
  if (!uploadForm.value.file) { uploadError.value = '请上传课件文件'; return }

  uploadLoading.value = true
  try {
    const tags = uploadForm.value.tagsStr
      .split(/[,，]/)
      .map(t => t.trim())
      .filter(Boolean)

    const fd = new FormData()
    fd.append('user_id', getUserId())
    fd.append('title', uploadForm.value.title.trim())
    fd.append('category', uploadForm.value.category)
    fd.append('description', uploadForm.value.description.trim())
    fd.append('tags_str', tags.join(','))
    fd.append('file', uploadForm.value.file)

    await fetch('/api/community/upload', { method: 'POST', body: fd })

    // 关闭弹窗，重置表单
    showUploadModal.value = false
    uploadForm.value = { title: '', category: '其他', description: '', tagsStr: '', file: null }
    // 刷新列表
    fetchItems()
  } catch (e) {
    uploadError.value = '上传失败，请稍后重试'
  } finally {
    uploadLoading.value = false
  }
}

onMounted(() => {
  fetchItems()
})
</script>

<style scoped>
.community { padding: 80px 40px; background: var(--bg-page); }
.community__inner { max-width: var(--max-width); margin: 0 auto; }

.community__header { text-align: center; margin-bottom: 36px; }
.community__title { font-size: clamp(28px, 3.5vw, 40px); font-weight: 700; letter-spacing: -0.015em; color: var(--text-primary); margin-bottom: 10px; }
.community__subtitle { font-size: 16px; color: var(--text-secondary); max-width: 620px; margin: 0 auto; }

.community__filters { display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; margin-bottom: 28px; }
.filter-tag { padding: 7px 18px; border-radius: 99px; font-size: 13px; font-weight: 600; cursor: pointer; border: 1px solid var(--border-default); background: transparent; color: var(--text-secondary); font-family: inherit; transition: all var(--t-fast) var(--ease-out); }
.filter-tag:hover { border-color: var(--border-accent); color: var(--accent); }
.filter-tag.active { background: var(--accent-light); border-color: var(--accent); color: var(--accent); }

.community__actions { display: flex; justify-content: center; margin-bottom: 32px; }

.community__loading { display: flex; align-items: center; justify-content: center; gap: 10px; padding: 60px 0; }
.community__empty { text-align: center; padding: 60px 0; }

.community__grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }

.project-card {
  background: var(--bg-card); border: 1px solid var(--border-light);
  border-radius: var(--r-lg); overflow: hidden;
  transition: all var(--t-base) var(--ease-out);
  display: flex; flex-direction: column; cursor: default;
}
.project-card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-lg); transform: translateY(-4px);
}

.project-card__top { height: 4px; flex-shrink: 0; }

.project-card__body { padding: 28px 24px 24px; display: flex; flex-direction: column; gap: 10px; flex: 1; }
.project-card__head { display: flex; justify-content: space-between; align-items: center; }
.project-card__cat { font-size: 12px; font-weight: 600; color: var(--accent); letter-spacing: 0.03em; text-transform: uppercase; }
.project-card__author { font-size: 11px; color: var(--text-tertiary); }
.project-card__title { font-size: 18px; font-weight: 700; letter-spacing: -0.015em; color: var(--text-primary); line-height: 1.3; }
.project-card__desc { font-size: 14px; color: var(--text-secondary); line-height: 1.65; flex: 1; }

.project-card__footer { display: flex; align-items: center; justify-content: space-between; margin-top: 4px; }
.project-card__tags { display: flex; gap: 6px; flex-wrap: wrap; }
.project-card__time { font-size: 12px; color: var(--text-tertiary); white-space: nowrap; }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 9999; padding: 24px; }
.modal-content { background: var(--bg-elevated); border: 1px solid var(--border-strong); border-radius: var(--r-lg); width: 100%; max-width: 520px; max-height: 90vh; overflow-y: auto; box-shadow: var(--shadow-xl); }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 24px 28px 0; }
.modal-header h3 { font-size: 18px; font-weight: 700; color: var(--text-primary); }
.modal-close { display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; border-radius: var(--r-sm); background: transparent; border: none; color: var(--text-tertiary); cursor: pointer; transition: all var(--t-fast); }
.modal-close:hover { background: rgba(255,255,255,0.06); color: var(--text-primary); }
.modal-body { padding: 24px 28px; display: flex; flex-direction: column; gap: 18px; }
.modal-footer { padding: 0 28px 24px; display: flex; justify-content: flex-end; gap: 10px; }

.field { display: flex; flex-direction: column; gap: 7px; }
.field-label { font-size: 13px; font-weight: 600; color: var(--text-secondary); }
.field-input { padding: 12px 16px; border: 1px solid var(--border-default); border-radius: var(--r-sm); font-size: 14px; font-family: inherit; background: var(--bg-surface); color: var(--text-primary); outline: none; transition: all var(--t-fast) var(--ease-out); width: 100%; }
.field-input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(0, 212, 170, 0.12); }
.field-input::placeholder { color: var(--text-tertiary); }
.field-textarea { resize: vertical; min-height: 80px; }
.form-error { font-size: 13px; color: #F87171; margin: 0; }

select.field-input { appearance: none; background-image: url("data:image/svg+xml,%3Csvg width='10' height='6' viewBox='0 0 10 6' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%238E8EA0' stroke-width='1.5' stroke-linecap='round'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 14px center; padding-right: 36px; }

.spinner { display: inline-block; width: 16px; height: 16px; border: 2px solid rgba(0,0,0,0.2); border-top-color: #0A0A12; border-radius: 50%; animation: spin 0.6s linear infinite; }

/* File upload */
.file-upload-area { border: 2px dashed var(--border-default); border-radius: var(--r-sm); padding: 24px; cursor: pointer; transition: all var(--t-fast) var(--ease-out); }
.file-upload-area:hover { border-color: var(--accent); background: rgba(0, 212, 170, 0.03); }
.file-upload-area.has-file { border-color: var(--accent); border-style: solid; background: rgba(0, 212, 170, 0.04); padding: 16px; }
.file-upload-hint { display: flex; flex-direction: column; align-items: center; gap: 10px; color: var(--text-tertiary); font-size: 13px; }
.file-upload-hint svg { opacity: 0.5; }
.file-upload-selected { display: flex; align-items: center; gap: 10px; color: var(--text-primary); font-size: 14px; }
.file-upload-selected svg { flex-shrink: 0; color: var(--accent); }
.file-name { font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.file-size { font-size: 12px; color: var(--text-tertiary); white-space: nowrap; }
.file-remove { margin-left: auto; background: none; border: none; color: var(--text-tertiary); font-size: 20px; cursor: pointer; line-height: 1; padding: 0 4px; }
.file-remove:hover { color: var(--error); }
.file-input-hidden { display: none; }

@media (max-width: 1000px) { .community__grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) { .community__grid { grid-template-columns: 1fr; } .community { padding: 60px 20px; } }

@keyframes spin { to { transform: rotate(360deg); } }
</style>
