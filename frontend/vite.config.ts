import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],

  server: {
    port: 3000,
    proxy: {
      // Proxy all /api/* requests to the FastAPI backend in dev
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },

  build: {
    outDir: 'dist',
    sourcemap: false,
    // Warn only if a chunk exceeds 1 MB (TON Connect is inherently large)
    chunkSizeWarningLimit: 1024,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-react':  ['react', 'react-dom'],
          'vendor-query':  ['@tanstack/react-query', 'zustand', 'axios'],
          'vendor-ton':    ['@tonconnect/ui-react'],
          'vendor-window': ['react-window'],
          'vendor-dates':  ['date-fns'],
        },
      },
    },
  },
})
