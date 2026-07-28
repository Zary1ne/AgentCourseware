<template>
  <div class="knowledge-panel">
    <div class="kp-header">
      <h3 class="kp-title">知识库</h3>
      <span class="kp-count">{{ docs.length }} 份文档</span>
    </div>

    <div :class="['upload-zone', { 'upload-zone--dragging': dragging, 'upload-zone--uploading': uploading }]"
      @dragover.prevent="dragging = true" @dragleave.prevent="dragging = false" @drop.prevent="handleDrop" @click="triggerInput">
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M10 3v10M5 8l5-5 5 5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/><path d="M3 13v2a1 1 0 001 1h12a1 1 0 001-1v-2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>
      <span class="upload-zone__label">{{ uploading ? '上传中...' : '点击或拖拽上传文件' }}</span>
      <span class="upload-zone__hint">支持 PDF / Word / PPT / 图片 / 文本 — 最大 20MB</span>
      <input ref="fileInput" type="file" accept=".pdf,.docx,.doc,.pptx,.ppt,.txt,.md,.jpg,.jpeg,.png,.gif,.webp" @change="handleFileSelect" style="display:none" />
    </div>

    <!-- 上传结果提示 -->
    <div v-if="lastResult" class="parse-result" :class="{ 'parse-result--error': !lastResult.success }">
      <div class="parse-result__head">
        <span :class="['badge', lastResult.success ? 'badge-success' : 'badge-error']">{{ lastResult.success ? '已解析' : '失败' }}</span>
        <span class="parse-result__name">{{ lastResult.filename }}</span>
      </div>
      <div v-if="lastResult.success && lastResult.summary" class="parse-result__meta">
        <span class="parse-result__summary">{{ lastResult.summary }}</span>
        <div class="parse-result__badges">
          <span v-if="lastResult.difficulty" :class="['kp-diff', 'kp-diff--' + difficultyClass(lastResult.difficulty)]">{{ lastResult.difficulty }}</span>
          <div v-if="lastResult.tags && lastResult.tags.length" class="parse-result__tags">
            <span v-for="tag in lastResult.tags" :key="tag" class="kp-tag">{{ tag }}</span>
          </div>
        </div>
      </div>
      <div v-else-if="lastResult.content" class="parse-result__snippet">{{ lastResult.content?.substring(0, 180) }}...</div>
    </div>

    <!-- 文档列表 -->
    <div class="kp-list">
      <div v-if="docs.length === 0" class="kp-empty">暂无文档，上传文件来构建你的知识库。</div>
      <div v-for="doc in docs" :key="doc.filename" class="kp-doc">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="kp-doc__icon"><rect x="1" y="1" width="14" height="14" rx="3" stroke="currentColor" stroke-width="1.1"/><path d="M5 6h6M5 9h4" stroke="currentColor" stroke-width="0.7" stroke-linecap="round"/></svg>
        <div class="kp-doc__main">
          <div class="kp-doc__top">
            <span class="kp-doc__name" @click="viewDoc(doc)">{{ doc.filename }}</span>
            <span class="kp-doc__chunks">{{ doc.chunk_count }} 块</span>
          </div>
          <!-- 创新点：智能摘要 -->
          <div v-if="doc.summary" class="kp-doc__summary">{{ doc.summary }}</div>
          <div class="kp-doc__bottom">
            <!-- 创新点：难度评级 + 知识点标签 -->
            <div class="kp-doc__badges">
              <span v-if="doc.difficulty" :class="['kp-diff', 'kp-diff--' + difficultyClass(doc.difficulty)]">{{ doc.difficulty }}</span>
              <span v-for="tag in (doc.tags || [])" :key="tag" class="kp-tag">{{ tag }}</span>
            </div>
            <!-- 操作按钮 -->
            <div class="kp-doc__actions">
              <button class="kp-btn" @click.stop="viewDoc(doc)" title="查看全文"><svg width="12" height="12" viewBox="0 0 16 16" fill="none"><circle cx="7" cy="7" r="5.5" stroke="currentColor" stroke-width="1.3"/><line x1="10.9" y1="10.9" x2="14" y2="14" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg></button>
              <button class="kp-btn" @click.stop="startEdit(doc)" title="编辑内容"><svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M2 11.5V14h2.5l7.37-7.37-2.5-2.5L2 11.5z" stroke="currentColor" stroke-width="1.1"/><path d="M10.5 2.5l3 3" stroke="currentColor" stroke-width="1.1"/></svg></button>
              <button class="kp-btn kp-btn--danger" @click.stop="confirmDelete(doc)" title="删除文档"><svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M4 5h8M6 5V3a1 1 0 011-1h2a1 1 0 011 1v2M5 5v7a1 1 0 001 1h4a1 1 0 001-1V5" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 查看文档弹窗（只读） -->
    <div v-if="viewingDoc" class="kp-modal-overlay" @click.self="viewingDoc = null">
      <div class="kp-modal">
        <div class="kp-modal__head">
          <h4>{{ viewingDoc.filename }}</h4>
          <button class="kp-close" @click="viewingDoc = null">&times;</button>
        </div>
        <div class="kp-modal__body"><pre>{{ viewingContent }}</pre></div>
      </div>
    </div>

    <!-- 编辑文档弹窗 -->
    <div v-if="editingDoc" class="kp-modal-overlay" @click.self="cancelEdit">
      <div class="kp-modal kp-modal--wide">
        <div class="kp-modal__head">
          <h4>编辑：{{ editingDoc.filename }}</h4>
          <button class="kp-close" @click="cancelEdit">&times;</button>
        </div>
        <div class="kp-modal__body">
          <textarea v-model="editContent" class="kp-edit-area" placeholder="编辑文档内容..."></textarea>
        </div>
        <div class="kp-modal__foot">
          <button class="kp-btn-save" @click="saveEdit" :disabled="saving">
            {{ saving ? '保存中...' : '保存修改' }}
          </button>
          <button class="kp-btn-cancel" @click="cancelEdit">取消</button>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="deletingDoc" class="kp-modal-overlay" @click.self="deletingDoc = null">
      <div class="kp-modal kp-modal--sm">
        <div class="kp-modal__head">
          <h4>确认删除</h4>
          <button class="kp-close" @click="deletingDoc = null">&times;</button>
        </div>
        <div class="kp-modal__body">
          <p style="margin:0; color:var(--text-secondary)">确定要删除 <strong>{{ deletingDoc.filename }}</strong> 吗？此操作不可恢复。</p>
        </div>
        <div class="kp-modal__foot">
          <button class="kp-btn-save kp-btn-save--danger" @click="doDelete(deletingDoc)" :disabled="deleting">
            {{ deleting ? '删除中...' : '确认删除' }}
          </button>
          <button class="kp-btn-cancel" @click="deletingDoc = null">取消</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { getKnowledgeDocuments, getDocumentContent, updateDocumentContent, deleteKnowledgeDocument, uploadToKnowledgeBase } from '../api'

const props = defineProps({
  taskId: { type: String, default: 'default' }
})

const emit = defineEmits(['file-uploaded'])
const docs = ref([])
const uploading = ref(false)
const dragging = ref(false)
const lastResult = ref(null)
const fileInput = ref(null)

// 查看
const viewingDoc = ref(null)
const viewingContent = ref('')

// 编辑
const editingDoc = ref(null)
const editContent = ref('')
const saving = ref(false)

// 删除
const deletingDoc = ref(null)
const deleting = ref(false)

// 难度等级 → CSS 类名映射
function difficultyClass(d) {
  if (d === '基础') return 'basic'
  if (d === '进阶') return 'medium'
  if (d === '拓展') return 'advanced'
  return ''
}

async function loadDocs() {
  try { const res = await getKnowledgeDocuments(props.taskId); docs.value = res.data.documents || [] } catch {}
}
onMounted(loadDocs)
watch(() => props.taskId, () => { docs.value = []; lastResult.value = null; loadDocs() })

function triggerInput() { fileInput.value?.click() }
function handleFileSelect(e) { const file = e.target.files?.[0]; if (file) uploadFile(file); e.target.value = '' }
function handleDrop(e) { dragging.value = false; const file = e.dataTransfer?.files?.[0]; if (file) uploadFile(file) }

async function uploadFile(file) {
  if (file.size > 20 * 1024 * 1024) { lastResult.value = { success:false, filename:file.name, content:'文件超过 20MB 限制。' }; return }
  uploading.value = true
  try {
    const res = await uploadToKnowledgeBase(file, props.taskId)
    const kb = res.data.knowledge_base || {}
    lastResult.value = {
      success: true,
      filename: res.data.filename || file.name,
      content: res.data.parsed_content || '',
      summary: kb.summary || '',
      tags: kb.tags || [],
      difficulty: kb.difficulty || '',
    }
    emit('file-uploaded', res.data)
    await loadDocs()
  } catch (e) {
    lastResult.value = { success:false, filename:file.name, content:'上传失败：' + (e.response?.data?.detail || e.message) }
  } finally { uploading.value = false }
}

// 查看文档全文
async function viewDoc(doc) {
  viewingDoc.value = doc
  viewingContent.value = '加载中...'
  try {
    const res = await getDocumentContent(doc.doc_id, props.taskId)
    viewingContent.value = res.data.content || '(空内容)'
  } catch {
    viewingContent.value = doc.sample || '(无法加载内容)'
  }
}

// 编辑文档
async function startEdit(doc) {
  editingDoc.value = doc
  editContent.value = '加载中...'
  try {
    const res = await getDocumentContent(doc.doc_id, props.taskId)
    editContent.value = res.data.content || ''
  } catch {
    editContent.value = doc.sample || ''
  }
}

function cancelEdit() {
  editingDoc.value = null
  editContent.value = ''
}

async function saveEdit() {
  if (!editingDoc.value) return
  saving.value = true
  try {
    await updateDocumentContent(editingDoc.value.doc_id, editContent.value, props.taskId)
    editingDoc.value = null
    editContent.value = ''
    await loadDocs()
  } catch (e) {
    alert('保存失败：' + (e.response?.data?.detail || e.message))
  } finally { saving.value = false }
}

// 删除文档
function confirmDelete(doc) {
  deletingDoc.value = doc
}

async function doDelete(doc) {
  deleting.value = true
  try {
    await deleteKnowledgeDocument(doc.doc_id, props.taskId)
    deletingDoc.value = null
    await loadDocs()
  } catch (e) {
    alert('删除失败：' + (e.response?.data?.detail || e.message))
  } finally { deleting.value = false }
}
</script>

<style scoped>
.knowledge-panel { display:flex; flex-direction:column; height:100%; padding:24px; gap:18px; overflow-y:auto; }
.kp-header { display:flex; align-items:center; justify-content:space-between; }
.kp-title { font-size:16px; font-weight:600; color:var(--text-primary); letter-spacing:-0.015em; }
.kp-count { font-size:11px; color:var(--text-tertiary); font-weight:600; font-family:var(--font-mono); background:var(--glass-sm); padding:3px 10px; border-radius:99px; }

.upload-zone { border:1px dashed var(--border-subtle); border-radius:var(--r-lg); padding:28px 16px; text-align:center; cursor:pointer; transition:all var(--t-fast) var(--ease-out); background:var(--glass-sm); backdrop-filter:var(--blur-sm); -webkit-backdrop-filter:var(--blur-sm); display:flex; flex-direction:column; align-items:center; gap:6px; color:var(--text-tertiary); }
.upload-zone:hover,.upload-zone--dragging { border-color:var(--accent); background:var(--accent-glow); color:var(--accent); }
.upload-zone--uploading { opacity:0.5; pointer-events:none; }
.upload-zone__label { font-size:13px; font-weight:500; color:var(--text-primary); }
.upload-zone__hint { font-size:11px; color:var(--text-tertiary); }

.parse-result { padding:12px 14px; background:var(--glass-sm); border-radius:var(--r-sm); border:1px solid var(--border-ghost); display:flex; flex-direction:column; gap:8px; }
.parse-result--error { border-color:rgba(248,113,113,0.15); background:rgba(248,113,113,0.04); }
.parse-result__head { display:flex; align-items:center; gap:8px; }
.parse-result__name { flex:1; min-width:0; font-size:11px; color:var(--text-tertiary); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.parse-result__snippet { font-size:11px; color:var(--text-secondary); line-height:1.5; display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; }
.parse-result__meta { display:flex; flex-direction:column; gap:6px; }
.parse-result__summary { font-size:12px; color:var(--text-primary); line-height:1.5; font-weight:500; }
.parse-result__badges { display:flex; flex-wrap:wrap; align-items:center; gap:5px; }
.parse-result__tags { display:flex; flex-wrap:wrap; gap:4px; }

/* 文档列表 */
.kp-list { display:flex; flex-direction:column; gap:6px; }
.kp-empty { font-size:13px; color:var(--text-tertiary); padding:28px 0; text-align:center; }

.kp-doc { display:flex; align-items:flex-start; gap:10px; padding:10px 12px; border-radius:var(--r-sm); color:var(--text-secondary); border:1px solid transparent; transition:all var(--t-fast) var(--ease-out); }
.kp-doc:hover { background:var(--glass-sm); border-color:var(--border-ghost); color:var(--text-primary); }
.kp-doc__icon { flex-shrink:0; opacity:0.35; margin-top:2px; }
.kp-doc__main { flex:1; min-width:0; display:flex; flex-direction:column; gap:4px; }
.kp-doc__top { display:flex; align-items:center; gap:8px; }
.kp-doc__name { flex:1; min-width:0; font-size:13px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; cursor:pointer; }
.kp-doc__name:hover { color:var(--accent); }
.kp-doc__chunks { font-size:10px; color:var(--text-tertiary); flex-shrink:0; font-family:var(--font-mono); }
.kp-doc__summary { font-size:11px; color:var(--text-tertiary); line-height:1.5; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
.kp-doc__bottom { display:flex; align-items:center; justify-content:space-between; gap:8px; margin-top:2px; }
.kp-doc__badges { display:flex; flex-wrap:wrap; align-items:center; gap:5px; }

/* 难度徽章 */
.kp-diff {
  font-size:10px; font-weight:600; padding:2px 8px; border-radius:99px;
  white-space:nowrap; flex-shrink:0; line-height:1.4;
}
.kp-diff--basic { background:rgba(5,150,105,0.12); color:#059669; }
.kp-diff--medium { background:rgba(99,102,241,0.12); color:#6366f1; }
.kp-diff--advanced { background:rgba(147,51,234,0.12); color:#9333ea; }
.kp-doc__actions { display:flex; gap:4px; flex-shrink:0; opacity:0; transition:opacity var(--t-fast); }
.kp-doc:hover .kp-doc__actions { opacity:1; }

.kp-tag { font-size:10px; font-weight:500; padding:2px 8px; border-radius:99px; background:var(--accent-glow); color:var(--accent); border:1px solid var(--border-accent); white-space:nowrap; }

.kp-btn { width:26px; height:26px; border-radius:var(--r-sm); border:1px solid transparent; background:transparent; color:var(--text-tertiary); cursor:pointer; display:flex; align-items:center; justify-content:center; transition:all var(--t-fast); }
.kp-btn:hover { background:var(--glass-sm); border-color:var(--border-ghost); color:var(--text-primary); }
.kp-btn--danger:hover { background:rgba(240,112,112,0.08); border-color:rgba(240,112,112,0.2); color:var(--error); }

/* 弹窗 */
.kp-modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.4); backdrop-filter:blur(4px); display:flex; align-items:center; justify-content:center; z-index:1000; }
.kp-modal { background:var(--bg-primary); border-radius:var(--r-lg); border:1px solid var(--border-subtle); width:640px; max-width:90vw; max-height:80vh; display:flex; flex-direction:column; box-shadow:0 20px 60px rgba(0,0,0,0.3); }
.kp-modal--wide { width:800px; }
.kp-modal--sm { width:420px; }
.kp-modal__head { display:flex; align-items:center; justify-content:space-between; padding:16px 20px; border-bottom:1px solid var(--border-ghost); }
.kp-modal__head h4 { margin:0; font-size:14px; font-weight:600; color:var(--text-primary); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:80%; }
.kp-modal__body { padding:20px; overflow-y:auto; flex:1; }
.kp-modal__body pre { margin:0; font-size:12px; line-height:1.7; white-space:pre-wrap; word-break:break-all; color:var(--text-secondary); font-family:var(--font-mono); }
.kp-modal__foot { display:flex; gap:8px; padding:12px 20px; border-top:1px solid var(--border-ghost); justify-content:flex-end; }
.kp-close { background:none; border:none; font-size:20px; color:var(--text-tertiary); cursor:pointer; line-height:1; padding:0 4px; }
.kp-close:hover { color:var(--text-primary); }

.kp-edit-area { width:100%; min-height:280px; background:var(--glass-sm); border:1px solid var(--border-subtle); border-radius:var(--r-sm); color:var(--text-primary); font-size:13px; line-height:1.7; padding:14px; resize:vertical; font-family:var(--font-mono); }
.kp-edit-area:focus { outline:none; border-color:var(--accent); }

.kp-btn-save { padding:6px 18px; border-radius:var(--r-sm); border:1px solid var(--accent); background:var(--accent); color:#fff; font-size:12px; font-weight:600; cursor:pointer; transition:opacity var(--t-fast); }
.kp-btn-save:hover { opacity:0.9; }
.kp-btn-save:disabled { opacity:0.5; cursor:not-allowed; }
.kp-btn-save--danger { background:var(--error); border-color:var(--error); }
.kp-btn-cancel { padding:6px 18px; border-radius:var(--r-sm); border:1px solid var(--border-subtle); background:transparent; color:var(--text-secondary); font-size:12px; cursor:pointer; transition:all var(--t-fast); }
.kp-btn-cancel:hover { border-color:var(--border-ghost); color:var(--text-primary); }
</style>