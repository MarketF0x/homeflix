import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

// Vérifier si les certificats SSL existent
const certDir = path.resolve(__dirname, '../certs')
const certFile = path.join(certDir, 'cert.pem')
const keyFile = path.join(certDir, 'key.pem')
const hasSSL = fs.existsSync(certFile) && fs.existsSync(keyFile)

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // Configuration des assets publics
  publicDir: 'public',
  
  server: {
    // Permet l'accès depuis d'autres appareils sur le réseau local
    host: '0.0.0.0',
    // Permet d'overrider via variable d'env VITE_PORT, sinon 5173
    port: Number(process.env.VITE_PORT) || 5173,
    // Évite la bascule silencieuse sur un autre port (erreur explicite si occupé)
    strictPort: true,
    // Configuration HMR pour éviter les plantages
    hmr: {
      overlay: true,
      timeout: 30000,
    },
    // Augmente le timeout de connexion
    ws: {
      pingTimeout: 60000,
    },
    // ✅ OPTIMISATION: Watcher ignore pour éviter hot-reload loops
    watch: {
      ignored: [
        '**/node_modules/**',
        '**/.git/**',
        '**/dist/**',
        '**/.venv*/**',
        '**/server/**',
        '**/electron/**',
        '**/__pycache__/**',
        '**/*.db',
        '**/*.log',
        '**/css-backup/**',
        '**/_temp_*.css',
      ],
      usePolling: false, // Meilleure performance sur Windows
    },
    // Configuration HTTPS si certificats disponibles
    ...(hasSSL ? {
      https: {
        key: fs.readFileSync(keyFile),
        cert: fs.readFileSync(certFile),
      }
    } : {}),
    // Proxy les requêtes API vers le serveur backend
    proxy: {
      '/api': {
        target: hasSSL ? 'https://localhost:8443' : 'http://localhost:8000',
        changeOrigin: true,
        // En HTTPS, accepter les certificats auto-signés
        ...(hasSSL ? { secure: false } : {}),
      },
    },
  },
  
  // 🚀 OPTIMISATIONS BUILD PRODUCTION
  build: {
    // Cible navigateurs modernes pour bundle plus petit
    target: 'es2020',
    // Chunk size warnings à 1MB
    chunkSizeWarningLimit: 1000,
    // Source maps désactivées en production
    sourcemap: false,
    // Minification optimale avec esbuild
    minify: 'esbuild',
    // Rollup options pour code splitting intelligent
    rollupOptions: {
      output: {
        // Code splitting manuel par type de fichier
        manualChunks: (id) => {
          // Vendor chunk pour node_modules
          if (id.includes('node_modules')) {
            // Séparer React en chunk distinct
            if (id.includes('react') || id.includes('react-dom')) {
              return 'react-vendor';
            }
            // Autres dépendances
            return 'vendor';
          }
          // Composants lourds en chunks séparés
          if (id.includes('VideoPlayer')) {
            return 'video-player';
          }
          if (id.includes('WebGLBackground')) {
            return 'webgl';
          }
        },
        // Noms de fichiers optimisés avec hash
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]',
      },
    },
    // Optimisations CSS
    cssCodeSplit: true,
    // Compression du CSS
    cssMinify: true,
  },
  
  // Optimisations des dépendances
  optimizeDeps: {
    // Force l'inclusion des modules ESM
    include: ['react', 'react-dom'],
    // Exclure les modules qui causent des problèmes
    exclude: [],
  },
})


