import { defineConfig, type Plugin } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { faqJsonLd } from './src/content/faq'

// Puts the FAQ structured data into the static HTML so crawlers see it without running JS.
function faqStructuredData(): Plugin {
  return {
    name: 'faq-structured-data',
    transformIndexHtml() {
      return [
        {
          tag: 'script',
          attrs: { type: 'application/ld+json' },
          children: JSON.stringify(faqJsonLd()),
          injectTo: 'head',
        },
      ]
    },
  }
}

export default defineConfig({
  plugins: [vue(), tailwindcss(), faqStructuredData()],
  server: {
    proxy: { '/api': 'http://localhost:8000' }
  }
})
