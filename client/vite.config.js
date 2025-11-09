import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Permet d'overrider via variable d'env VITE_PORT, sinon 5173
    port: Number(process.env.VITE_PORT) || 5173,
    // Évite la bascule silencieuse sur un autre port (erreur explicite si occupé)
    strictPort: true,
  },
})
