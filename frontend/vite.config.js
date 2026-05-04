import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// dev port 5173; the FastAPI backend runs on 8000 with CORS wide open
// so we don't need a proxy. swap to one before deploying for real.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { port: 5173 },
})
