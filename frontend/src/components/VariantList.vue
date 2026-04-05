<script setup lang="ts">
import type { VariantInput } from '../types'
import VariantCard from './VariantCard.vue'

const props = defineProps<{
  variants: VariantInput[]
  term: number
}>()

const emit = defineEmits<{
  'update:variants': [value: VariantInput[]]
  add: []
  remove: [index: number]
}>()

const updateVariant = (index: number, variant: VariantInput) => {
  const copy = [...props.variants]
  copy[index] = variant
  emit('update:variants', copy)
}
</script>

<template>
  <div>
    <VariantCard
      v-for="(v, i) in variants"
      :key="i"
      :variant="v"
      :index="i"
      :term="term"
      :canDelete="i >= 2"
      @update="updateVariant(i, $event)"
      @remove="emit('remove', i)"
    />
    <button
      @click="emit('add')"
      class="w-full border-2 border-dashed border-gray-300 rounded-lg p-3 text-gray-600 hover:border-blue-400 hover:text-blue-600 transition-colors"
    >
      Přidat variantu
    </button>
  </div>
</template>
