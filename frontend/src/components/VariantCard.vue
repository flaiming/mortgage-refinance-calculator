<script setup lang="ts">
import { computed } from 'vue'
import type { VariantInput } from '../types'
import type { VariantPayment } from '../utils/mortgage'

const props = defineProps<{
  variant: VariantInput
  index: number
  term: number
  refinancingYear: number
  canDelete: boolean
  payment: VariantPayment | null
  referencePayment: number | null
  originalPayment: number | null
  expectedReturn: number | null
  /** The variant is paid off before the longest one and then invests the whole budget. */
  investsAfterPayoff: boolean
}>()

const emit = defineEmits<{
  update: [value: VariantInput]
  remove: []
}>()

const minLengthChange = computed(() => -(props.term - props.refinancingYear - 1))
const totalYears = computed(() => props.term + (props.variant.length_change || 0))

const kc = (v: number) => Math.round(v).toLocaleString('cs-CZ') + ' Kč'

const isReference = computed(() => props.payment?.referenceIndex === props.index)
// Under half a crown the card would read "0 Kč less"; it still counts as the same payment here
const savings = computed(() => props.payment?.savings ?? 0)

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

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 items-start">
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
        <label class="field-label" title="Záporné číslo splatnost zkrátí">Prodloužit o [roky]</label>
        <input
          type="number"
          :value="variant.length_change"
          @input="updateField('length_change', Number(($event.target as HTMLInputElement).value))"
          :min="minLengthChange"
          :max="50"
          class="field"
        />
        <p class="mt-1 text-xs text-muted">Splatnost celkem {{ totalYears }} let</p>
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

    <!-- What this variant means for the monthly budget -->
    <div v-if="payment?.payment == null" class="mt-4 text-sm text-red-700">
      Splátku nejde spočítat. Zkontrolujte délku splatnosti a úrok.
    </div>

    <div
      v-else-if="savings >= 0.5"
      data-testid="variant-savings"
      class="mt-4 rounded-md border-l-4 border-amber bg-[#fdf3e1] px-4 py-3 text-sm leading-relaxed"
    >
      <p>
        Splátka <strong>{{ kc(payment.payment) }}</strong>, tedy o
        <strong class="text-petrol-900">{{ kc(savings) }} měsíčně méně</strong>
        než u varianty {{ payment.referenceIndex + 1 }}.
      </p>
      <p class="mt-1 text-ink/80">
        Ušetřenou částku kalkulačka každý měsíc investuje
        <template v-if="expectedReturn != null">s výnosem {{ expectedReturn.toLocaleString('cs-CZ') }}&nbsp;% ročně</template>
        <template v-else>se zvoleným výnosem</template>.
        <template v-if="investsAfterPayoff && referencePayment != null">
          Po splacení v {{ totalYears }}. roce investuje celých {{ kc(referencePayment) }} měsíčně.
        </template>
        Ve výsledcích uvidíte, jestli to vynese víc než rychlejší splácení.
      </p>
    </div>

    <p v-else-if="isReference" class="mt-4 text-sm leading-relaxed">
      Nová splátka <strong>{{ kc(payment.payment) }}</strong> měsíčně<template v-if="originalPayment != null"
      ><span class="text-muted"> (dosud {{ kc(originalPayment) }})</span></template>.
      Je nejvyšší, takže s ní kalkulačka počítá jako s měsíčním rozpočtem pro všechny varianty.
      <template v-if="investsAfterPayoff">
        Po splacení v {{ totalYears }}. roce investuje celou splátku.
      </template>
    </p>

    <p v-else class="mt-4 text-sm leading-relaxed">
      Splátka <strong>{{ kc(payment.payment) }}</strong>, stejná jako u varianty {{ payment.referenceIndex + 1 }}.
      <template v-if="investsAfterPayoff">
        Po splacení v {{ totalYears }}. roce investuje celou splátku.
      </template>
    </p>
  </div>
</template>
