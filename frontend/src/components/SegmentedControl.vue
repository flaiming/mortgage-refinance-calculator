<script setup lang="ts">
defineProps<{
  modelValue: string
  options: { value: string; label: string }[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <div class="inline-flex rounded-lg border border-gray-300 overflow-hidden">
    <button
      v-for="opt in options"
      :key="opt.value"
      :data-testid="modelValue === opt.value ? 'segmented-button-active' : 'segmented-button'"
      :class="[
        'px-4 py-2 text-sm font-medium transition-colors',
        modelValue === opt.value
          ? 'bg-blue-600 text-white'
          : 'bg-white text-gray-700 hover:bg-gray-100'
      ]"
      @click="emit('update:modelValue', opt.value)"
    >
      {{ opt.label }}
    </button>
  </div>
</template>
