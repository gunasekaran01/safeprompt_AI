import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite configuration for SafePrompt AI frontend.
// A dev-time proxy is used so the React app can call "/api/..." without
// worrying about CORS while the FastAPI backend runs on a different port.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})
