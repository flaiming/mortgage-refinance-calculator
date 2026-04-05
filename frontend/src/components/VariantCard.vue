<script setup lang="ts">
import { computed } from 'vue'
import type { VariantInput } from '../types'

const props = defineProps<{
  variant: VariantInput
  index: number
  term: number
  canDelete: boolean
}>()

const emit = defineEmits<{
  update: [value: VariantInput]
  remove: []
}>()

const minLengthChange = computed(() => -(props.term - 1))

const updateField = (field: keyof VariantInput, value: number) => {
  emit('update', { ...props.variant, [field]: value })
}
</script>

<template>
  <div data-testid="variant-card" class="border border-gray-300 rounded-lg p-4 mb-4">
    <div class="flex justify-between items-center mb-3">
      <h4 class="font-semibold">Varianta {{ index + 1 }}</h4>
      <button
        v-if="canDelete"
        @click="emit('remove')"
        class="text-red-600 hover:text-red-800 text-sm font-medium"
      >
        Smazat
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div data-testid="number-input">
        <label class="block text-sm font-medium text-gray-700 mb-1">Nový úrok [%]</label>
        <input
          type="number"
          :value="variant.refinancing_interest"
          @input="updateField('refinancing_interest', Number(($event.target as HTMLInputElement).value))"
          min="0.1"
          step="0.01"
          class="w-full border border-gray-300 rounded px-3 py-2"
        />
      </div>

      <div v-if="index >= 1" data-testid="number-input">
        <label class="block text-sm font-medium text-gray-700 mb-1">Přidání/odebrání let k původní délce</label>
        <input
          type="number"
          :value="variant.length_change"
          @input="updateField('length_change', Number(($event.target as HTMLInputElement).value))"
          :min="minLengthChange"
          :max="50"
          class="w-full border border-gray-300 rounded px-3 py-2"
        />
      </div>

      <div v-if="index >= 1" data-testid="number-input">
        <label class="block text-sm font-medium text-gray-700 mb-1">Navýšení hypotéky [Kč]</label>
        <input
          type="number"
          :value="variant.extra_principal"
          @input="updateField('extra_principal', Number(($event.target as HTMLInputElement).value))"
          min="0"
          step="50000"
          class="w-full border border-gray-300 rounded px-3 py-2"
        />
      </div>
    </div>
  </div>
</template>
