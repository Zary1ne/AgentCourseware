import axios from 'axios'

const api = axios.create({ baseURL: '/api', timeout: 120000 })

export function sendMessage(messages, stream = true, signal = null, promptType = '') {
  const body = { messages, stream }
  if (promptType) body.prompt_type = promptType
  if (stream) {
    return fetch('/api/chat/message', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body), signal,
    })
  }
  return api.post('/chat/message', body)
}

export function extractIntent(messages) { return api.post('/chat/extract-intent', { messages }) }

// 直接把对话内容导出为 docx / pptx 下载（来自 AITEACH 原型 /api/chat/export/{format}）
export async function exportDocument(format, content, title = '教学文档') {
  const resp = await api.post(`/chat/export/${format}`, { content, title }, { responseType: 'blob' })
  return resp.data
}

// 结构化 slides 导出：直接发送 slides JSON + 模板风格，后端按结构生成文件
export async function exportSlides(format, slides, title = '教学文档', template = 'academic') {
  const resp = await api.post(`/chat/export-slides/${format}`, { slides, title, template }, { responseType: 'blob' })
  return resp.data
}

export function uploadToKnowledgeBase(file, taskId = 'default') {
  const fd = new FormData(); fd.append('file', file); fd.append('task_id', taskId)
  return api.post('/knowledge/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
}

export function parseFile(file) {
  const fd = new FormData(); fd.append('file', file)
  return api.post('/knowledge/parse-file', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
}

export function searchKnowledge(query, topK = 5, taskId = null) {
  return api.post('/knowledge/search', { query, top_k: topK, task_id: taskId })
}

export function getKnowledgeDocuments(taskId = null) {
  const params = taskId ? { task_id: taskId } : {}
  return api.get('/knowledge/documents', { params })
}

export function getDocumentContent(docId, taskId = null) {
  const params = taskId ? { task_id: taskId } : {}
  return api.get(`/knowledge/documents/${docId}`, { params })
}

export function updateDocumentContent(docId, content, taskId = null) {
  const params = taskId ? { task_id: taskId } : {}
  return api.put(`/knowledge/documents/${docId}`, { content }, { params })
}

export function deleteKnowledgeDocument(docId, taskId = null) {
  const params = taskId ? { task_id: taskId } : {}
  return api.delete(`/knowledge/documents/${docId}`, { params })
}

export function generateAll(intent) { return api.post('/generate/all', { intent, style: 'professional', include_quiz: true }) }
export function generatePPT(intent) { return api.post('/generate/ppt', { intent, style: 'professional' }) }
export function generateDoc(intent) { return api.post('/generate/doc', { intent, style: 'professional' }) }
export function reviseFile(fileType, filePath, instruction) { return api.post('/generate/revise', { file_type: fileType, file_path: filePath, instruction }) }
export function getDownloadUrl(filename) { return `/api/generate/download/${filename}` }

export function getAdminStats() { return api.get('/admin/stats') }

// ===== 认证相关 =====
export function register(username, password) { return api.post('/auth/register', { username, password }) }
export function login(username, password) { return api.post('/auth/login', { username, password }) }
export function getUserInfo(userId) { return api.get(`/auth/user/${userId}`) }

// ===== 开源社区 =====
export function uploadCourseware(data) { return api.post('/community/upload', data) }
export function getCommunityList(category = null) {
  const params = category ? { category } : {}
  return api.get('/community/list', { params })
}
export function getMyCourseware(userId) { return api.get(`/community/my/${userId}`) }

// ===== 管理员审核 =====
export function getPendingCourseware(status = 'pending') {
  return api.get('/community/pending', { params: { status } })
}
export function reviewCourseware(cwId, approved, comment = '') {
  return api.post('/community/review', { cw_id: cwId, approved, comment })
}

// ===== 通知系统 =====
export function getNotifications(userId, unreadOnly = false) {
  return api.get(`/notifications/${userId}`, { params: { unread_only: unreadOnly } })
}
export function markNotificationRead(nid) { return api.post(`/notifications/read/${nid}`) }
export function markAllNotificationsRead(userId) { return api.post(`/notifications/read-all/${userId}`) }
export function getUnreadCount(userId) { return api.get(`/notifications/unread-count/${userId}`) }

// ===== 管理员用户管理 =====
export function getAllUsers() { return api.get('/admin/users') }
export function banUser(userId, reason) { return api.post('/admin/ban-user', { user_id: userId, reason }) }
export function unbanUser(userId) { return api.post(`/admin/unban-user/${userId}`) }
export function updateUser(userId, username, password) { return api.post('/admin/update-user', { user_id: userId, username, password }) }

// ===== 课件文件 =====
export function getCoursewareFileUrl(cwId) { return `/api/community/file/${cwId}` }

// ===== 反馈系统 =====
export function submitFeedback(data) { return api.post('/feedback/submit', data) }
export function getFeedbackList(status = null) {
  const params = status ? { status } : {}
  return api.get('/feedback/list', { params })
}
export function getPendingFeedbackCount() { return api.get('/feedback/pending-count') }
export function reviewFeedback(fbId, status, reply = '') { return api.post('/feedback/review', { fb_id: fbId, status, reply }) }
