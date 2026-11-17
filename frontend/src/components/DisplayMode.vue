<script setup lang="ts">
import SegmentedControl from './SegmentedControl.vue'

defineProps<{
  displayMode: string
  inflation: number
}>()

const emit = defineEmits<{
  'update:displayMode': [value: string]
  'update:inflation': [value: number]
}>()

const modeOptions = [
  { value: 'nominal', label: 'Nominálně' },
  { value: 'real', label: 'Reálně' },
]
</script>

<template>
  <div class="panel">
    <h3 class="text-lg font-semibold mb-4">Zobrazení hodnot</h3>

    <div class="flex flex-col gap-4">
      <SegmentedControl
        :modelValue="displayMode"
        @update:modelValue="emit('update:displayMode', $event)"
        :options="modeOptions"
      />

      <div data-testid="number-input" class="max-w-xs">
        <label class="field-label">Roční inflace [%]</label>
        <input
          type="number"
          :value="inflation"
          @input="emit('update:inflation', Number(($event.target as HTMLInputElement).value))"
          :disabled="displayMode === 'nominal'"
          step="0.1"
          min="0"
          class="field"
        />
      </div>

      <p class="text-sm text-muted">
        Reálné hodnoty zohledňují pokles kupní síly peněz v čase.
      </p>
    </div>
  </div>
</template>
