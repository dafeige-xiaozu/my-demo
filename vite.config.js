import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
        // 如果需要重写路径，可以取消下面的注释
        // rewrite: (path) => path.replace(/^\/api/, '')
      },
    },
  },
})
