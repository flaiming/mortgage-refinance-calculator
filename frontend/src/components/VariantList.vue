<script setup lang="ts">
import { computed } from 'vue'
import type { VariantInput } from '../types'
import { computeVariantPayments } from '../utils/mortgage'
import VariantCard from './VariantCard.vue'

const props = defineProps<{
  variants: VariantInput[]
  principal: number
  rate: number
  term: number
  refinancingYear: number
  expectedReturn: number | null
}>()

const emit = defineEmits<{
  'update:variants': [value: VariantInput[]]
  add: []
  remove: [index: number]
}>()

const payments = computed(() =>
  computeVariantPayments(props.principal, props.rate, props.term, props.refinancingYear, props.variants),
)

const updateVariant = (index: number, variant: VariantInput) => {
  const copy = [...props.variants]
  copy[index] = variant
  emit('update:variants', copy)
}
</script>

<template>
  <section class="panel">
    <h3 class="text-lg font-semibold mb-2">Varianty refinancování</h3>
    <div class="text-sm leading-relaxed text-ink/85 mb-4 space-y-2">
      <p>
        Když si při refinancování prodloužíte splatnost, splátka klesne. Ušetřené peníze pak můžete
        každý měsíc investovat. Kalkulačka spočítá, jestli vás to nakonec vyjde lépe než splácet rychleji.
      </p>
      <p class="text-muted">
        Varianta 1 zachová původní délku splácení. V dalších variantách splatnost prodlužte, případně si půjčte víc.
      </p>
    </div>
    <div class="flex flex-col gap-3 mb-3">
      <VariantCard
        v-for="(v, i) in variants"
        :key="i"
        :variant="v"
        :index="i"
        :term="term"
        :refinancingYear="refinancingYear"
        :canDelete="i >= 2"
        :payment="payments.variants[i] ?? null"
        :referencePayment="payments.variants[payments.variants[i]?.referenceIndex ?? i]?.payment ?? null"
        :originalPayment="payments.originalPayment"
        :expectedReturn="expectedReturn"
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
