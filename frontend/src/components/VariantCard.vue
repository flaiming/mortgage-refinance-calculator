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
  <div data-testid="variant-card" class="rounded-lg border border-line bg-paper/60 p-4">
    <div class="flex justify-between items-center mb-3">
      <h4 class="font-semibold">
        Varianta {{ index + 1 }}
        <span v-if="index === 0" class="ml-1 text-sm font-normal text-muted">(původní délka splácení)</span>
      </h4>
      <button
        v-if="canDelete"
        @click="emit('remove')"
        type="button"
        class="text-sm font-medium text-muted hover:text-red-700 underline-offset-2 hover:underline"
      >
        Smazat
      </button>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 items-end">
      <div data-testid="number-input">
        <label class="field-label">Nový úrok [%]</label>
        <input
          type="number"
          :value="variant.refinancing_interest"
          @input="updateField('refinancing_interest', Number(($event.target as HTMLInputElement).value))"
          min="0.1"
          step="0.01"
          class="field"
        />
      </div>

      <div v-if="index >= 1" data-testid="number-input">
        <label class="field-label">Změna splatnosti [roky]</label>
        <input
          type="number"
          :value="variant.length_change"
          @input="updateField('length_change', Number(($event.target as HTMLInputElement).value))"
          :min="minLengthChange"
          :max="50"
          class="field"
        />
      </div>

      <div v-if="index >= 1" data-testid="number-input">
        <label class="field-label">Navýšení úvěru [Kč]</label>
        <input
          type="number"
          :value="variant.extra_principal"
          @input="updateField('extra_principal', Number(($event.target as HTMLInputElement).value))"
          min="0"
          step="50000"
          class="field"
        />
      </div>
    </div>
  </div>
</template>
