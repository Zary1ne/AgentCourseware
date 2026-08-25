import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      // marked-katex-extension 5.x 默认导出 TypeScript 源码，在 Vite 浏览器端会触发类型剥离失败，
      // 导致整个 marked.parse 抛错并降级为纯文本。这里固定指向其预编译的 CJS 产物。
      'marked-katex-extension': path.resolve(__dirname, 'node_modules/marked-katex-extension/lib/index.cjs'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/outputs': { target: 'http://localhost:8000', changeOrigin: true }
    }
  }
})