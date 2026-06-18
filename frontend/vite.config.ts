import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  optimizeDeps: {
    include: ['plotly.js/dist/plotly.min.js'],
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'https://data-insight-zdro.onrender.com',
        changeOrigin: true,
      },
    },
  },
})
