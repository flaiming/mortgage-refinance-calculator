<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  principal: number
  term: number
  rate: number
  refinancingYear: number
}>()

const emit = defineEmits<{
  'update:principal': [value: number]
  'update:term': [value: number]
  'update:rate': [value: number]
  'update:refinancingYear': [value: number]
}>()

const formattedPrincipal = computed({
  get() {
    return String(props.principal).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  },
  set(val: string) {
    const num = Number(val.replace(/\s/g, '').replace(/\u00a0/g, ''))
    if (!isNaN(num)) emit('update:principal', num)
  }
})

const refiOptions = computed(() => {
  const opts = []
  for (let i = 1; i < props.term; i++) {
    opts.push(i)
  }
  return opts
})
</script>

<template>
  <div class="border border-gray-300 rounded-lg p-4 mb-4">
    <h3 class="text-lg font-semibold mb-3">Původní hypotéka</h3>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div data-testid="text-input">
        <label class="block text-sm font-medium text-gray-700 mb-1">Splácená částka [Kč]</label>
        <input
          type="text"
          :value="formattedPrincipal"
          @input="formattedPrincipal = ($event.target as HTMLInputElement).value"
          class="w-full border border-gray-300 rounded px-3 py-2"
        />
      </div>

      <div data-testid="number-input">
        <label class="block text-sm font-medium text-gray-700 mb-1">Délka splácení [roky]</label>
        <input
          type="number"
          :value="term"
          @input="emit('update:term', Number(($event.target as HTMLInputElement).value))"
          min="2"
          class="w-full border border-gray-300 rounded px-3 py-2"
        />
      </div>

      <div data-testid="number-input">
        <label class="block text-sm font-medium text-gray-700 mb-1">Úrok [%]</label>
        <input
          type="number"
          :value="rate"
          @input="emit('update:rate', Number(($event.target as HTMLInputElement).value))"
          min="0.1"
          step="0.01"
          class="w-full border border-gray-300 rounded px-3 py-2"
        />
      </div>

      <div data-testid="number-input">
        <label class="block text-sm font-medium text-gray-700 mb-1">Rok refinancování</label>
        <select
          :value="refinancingYear"
          @change="emit('update:refinancingYear', Number(($event.target as HTMLSelectElement).value))"
          class="w-full border border-gray-300 rounded px-3 py-2"
        >
          <option v-for="y in refiOptions" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
    </div>
  </div>
</template>
