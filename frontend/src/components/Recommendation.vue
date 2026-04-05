<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  recommendation: string | null
}>()

const htmlContent = computed(() => {
  if (!props.recommendation) return ''
  // Convert **bold** markdown to <strong> tags
  return props.recommendation.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
})
</script>

<template>
  <div v-if="recommendation" class="mb-6">
    <h2 class="text-xl font-bold mb-3">Doporučení</h2>
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <p v-html="htmlContent" class="text-gray-800"></p>
    </div>
  </div>
</template>
