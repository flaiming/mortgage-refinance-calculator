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
  <div class="border border-gray-300 rounded-lg p-4 mb-4">
    <h3 class="text-lg font-semibold mb-3">Zobrazení hodnot</h3>

    <div class="flex flex-col gap-4">
      <SegmentedControl
        :modelValue="displayMode"
        @update:modelValue="emit('update:displayMode', $event)"
        :options="modeOptions"
      />

      <div data-testid="number-input" class="max-w-xs">
        <label class="block text-sm font-medium text-gray-700 mb-1">Roční inflace [%]</label>
        <input
          type="number"
          :value="inflation"
          @input="emit('update:inflation', Number(($event.target as HTMLInputElement).value))"
          :disabled="displayMode === 'nominal'"
          step="0.1"
          min="0"
          class="w-full border border-gray-300 rounded px-3 py-2 disabled:bg-gray-100 disabled:text-gray-400"
        />
      </div>

      <p class="text-sm text-gray-500">
        Reálné hodnoty zohledňují pokles kupní síly peněz v čase.
      </p>
    </div>
  </div>
</template>
