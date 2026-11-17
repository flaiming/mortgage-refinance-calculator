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
  <div class="inline-flex self-start rounded-lg bg-paper border border-line p-1 gap-1" role="group">
    <button
      v-for="opt in options"
      :key="opt.value"
      type="button"
      :aria-pressed="modelValue === opt.value"
      :data-testid="modelValue === opt.value ? 'segmented-button-active' : 'segmented-button'"
      :class="[
        'px-4 py-1.5 rounded-md text-sm font-medium transition-colors',
        modelValue === opt.value
          ? 'bg-petrol-700 text-white shadow-sm'
          : 'text-muted hover:text-ink hover:bg-white'
      ]"
      @click="emit('update:modelValue', opt.value)"
    >
      {{ opt.label }}
    </button>
  </div>
</template>
