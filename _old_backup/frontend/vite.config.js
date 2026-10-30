import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/chat': 'http://127.0.0.1:8000',
      '/permissions': 'http://127.0.0.1:8000',
      '/courses': 'http://127.0.0.1:8000',
      '/assignments': 'http://127.0.0.1:8000',
      '/exams': 'http://127.0.0.1:8000',
      '/announcements': 'http://127.0.0.1:8000',
      '/emails': 'http://127.0.0.1:8000',
      '/calendar': 'http://127.0.0.1:8000',
      '/reminders': 'http://127.0.0.1:8000',
      '/documents': 'http://127.0.0.1:8000',
      '/presentations': 'http://127.0.0.1:8000',
      '/voice': 'http://127.0.0.1:8000',
      '/activity': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
      '/system': 'http://127.0.0.1:8000',
      '/generated': 'http://127.0.0.1:8000',
      '/uploads': 'http://127.0.0.1:8000'
    }
  }
})
