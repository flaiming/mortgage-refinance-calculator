<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  recommendation: string | null
}>()

const htmlContent = computed(() => {
  if (!props.recommendation) return ''
  // Convert **bold** markdown to <strong> tags
  return props.recommendation.replace(/\*\*(.+?)\*\*/g, '<strong class="text-ink">$1</strong>')
})
</script>

<template>
  <div v-if="recommendation" class="mb-8 rounded-xl bg-petrol-50 border-l-4 border-amber px-5 py-4">
    <h2 class="text-xl font-bold mb-2 text-petrol-900">Doporučení</h2>
    <p v-html="htmlContent" class="text-ink/85 leading-relaxed max-w-[75ch]"></p>
  </div>
</template>
