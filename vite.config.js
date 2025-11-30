import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // FastAPI 的路径不需要重写，/api 会继续传递到后端
        // rewrite: (path) => path.replace(/^\/api/, '')
      },
    },
  },
})
