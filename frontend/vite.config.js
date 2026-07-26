import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8010',
        changeOrigin: true,
      }
    }
  },
  preview: {
    allowedHosts: ['pure-abundance-production-0330.up.railway.app'],
    proxy: {
      '/api': {
        target: 'http://localhost:8010',
        changeOrigin: true,
      }
    }
  }
})
