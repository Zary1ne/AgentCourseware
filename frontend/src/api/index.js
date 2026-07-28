import axios from 'axios'

const api = axios.create({ baseURL: '/api', timeout: 120000 })

export function sendMessage(messages, stream = true, signal = null) {
  if (stream) {
    return fetch('/api/chat/message', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages, stream: true }), signal,
    })
  }
  return api.post('/chat/message', { messages, stream: false })
}

export function extractIntent(messages) { return api.post('/chat/extract-intent', { messages }) }

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
