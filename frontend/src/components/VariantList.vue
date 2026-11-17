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
  <section class="panel">
    <h3 class="text-lg font-semibold mb-1">Varianty refinancování</h3>
    <p class="text-sm text-muted mb-4">
      Nová úroková sazba po skončení fixace. U dalších variant můžete splatnost prodloužit či zkrátit nebo si půjčit víc.
    </p>
    <div class="flex flex-col gap-3 mb-3">
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
    </div>
    <button
      type="button"
      @click="emit('add')"
      class="w-full border border-dashed border-slate-400 rounded-lg p-2.5 text-sm font-medium text-petrol-700 hover:border-petrol-600 hover:bg-petrol-50 transition-colors"
    >
      Přidat variantu
    </button>
  </section>
</template>
