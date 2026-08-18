// AI 回复的 Markdown 渲染器：marked + highlight.js 代码高亮 + KaTeX 数学公式 + DOMPurify 防注入
import { marked } from 'marked'
import { markedHighlight } from 'marked-highlight'
import markedKatex from 'marked-katex-extension'
import hljs from 'highlight.js/lib/common'
import DOMPurify from 'dompurify'

// KaTeX 公式扩展：支持 $...$、$$...$$、\(...\)、\[...\]
marked.use(
  markedKatex({
    throwOnError: false,
    nonStandard: true,
    output: 'html',
  })
)

// 代码高亮扩展：未标注语言的代码块按 plaintext 处理
marked.use(
  markedHighlight({
    emptyLangClass: 'hljs',
    langPrefix: 'hljs language-',
    highlight(code, lang) {
      const language = hljs.getLanguage(lang) ? lang : 'plaintext'
      return hljs.highlight(code, { language }).value
    },
  })
)

marked.setOptions({
  gfm: true,
  breaks: true,
})

// 简单缓存：流式输出时同一条消息反复渲染，命中缓存避免重复解析（限制条数防膨胀）
const cache = new Map()
const CACHE_LIMIT = 200

export function renderMarkdown(text) {
  if (!text) return ''
  const hit = cache.get(text)
  if (hit !== undefined) return hit
  let html
  try {
    html = DOMPurify.sanitize(marked.parse(text))
  } catch {
    html = DOMPurify.sanitize(text)
  }
  if (cache.size >= CACHE_LIMIT) {
    const firstKey = cache.keys().next().value
    cache.delete(firstKey)
  }
  cache.set(text, html)
  return html
}
