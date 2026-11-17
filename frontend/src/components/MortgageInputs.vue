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
  <div class="panel">
    <h3 class="text-lg font-semibold mb-4">Původní hypotéka</h3>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div data-testid="text-input">
        <label class="field-label">Splácená částka [Kč]</label>
        <input
          type="text"
          :value="formattedPrincipal"
          @input="formattedPrincipal = ($event.target as HTMLInputElement).value"
          class="field"
        />
      </div>

      <div data-testid="number-input">
        <label class="field-label">Délka splácení [roky]</label>
        <input
          type="number"
          :value="term"
          @input="emit('update:term', Number(($event.target as HTMLInputElement).value))"
          min="2"
          class="field"
        />
      </div>

      <div data-testid="number-input">
        <label class="field-label">Úrok [%]</label>
        <input
          type="number"
          :value="rate"
          @input="emit('update:rate', Number(($event.target as HTMLInputElement).value))"
          min="0.1"
          step="0.01"
          class="field"
        />
      </div>

      <div data-testid="number-input">
        <label class="field-label">Rok refinancování</label>
        <select
          :value="refinancingYear"
          @change="emit('update:refinancingYear', Number(($event.target as HTMLSelectElement).value))"
          class="field"
        >
          <option v-for="y in refiOptions" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
    </div>
  </div>
</template>
