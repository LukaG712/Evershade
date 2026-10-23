import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { readFileSync, writeFileSync, unlinkSync } from 'fs'
import { resolve } from 'path'

export default defineConfig({
  base: './',
  plugins: [
    react(),
    {
      name: 'rename-index',
      closeBundle() {
        const outDir = resolve(__dirname, '..')
        const indexPath = resolve(outDir, 'index.html')
        const landingPath = resolve(outDir, 'landing.html')
        try {
          const content = readFileSync(indexPath, 'utf-8')
          writeFileSync(landingPath, content, 'utf-8')
          unlinkSync(indexPath)
        } catch (e) {
          // ignore if files don't exist
        }
      },
    },
  ],
  build: {
    outDir: '../',
    emptyOutDir: false,
    rollupOptions: {
      output: {
        entryFileNames: 'landing/assets/[name].[hash].js',
        chunkFileNames: 'landing/assets/[name].[hash].js',
        assetFileNames: 'landing/assets/[name].[hash].[ext]',
      },
    },
  },
})
