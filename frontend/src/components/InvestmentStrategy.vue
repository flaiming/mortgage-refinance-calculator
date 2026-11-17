<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps<{
  strategy: string
  customRate: number | null
  investAfterPayoff: boolean
}>()

const emit = defineEmits<{
  'update:strategy': [value: string]
  'update:customRate': [value: number | null]
  'update:investAfterPayoff': [value: boolean]
}>()

const isOpen = ref(false)

const strategyOptions = [
  { value: 'safe', label: 'Konzervativní (4 % ročně)' },
  { value: 'medium', label: 'Vyvážená (6 % ročně)' },
  { value: 'risky', label: 'Dynamická (8 % ročně)' },
  { value: 'custom', label: 'Vlastní' },
]

const selectedLabel = computed(() => {
  return strategyOptions.find(o => o.value === props.strategy)?.label || ''
})

const selectOption = (value: string) => {
  emit('update:strategy', value)
  isOpen.value = false
}

const dropdownRef = ref<HTMLElement | null>(null)

const handleClickOutside = (e: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', handleClickOutside))
</script>

<template>
  <div class="panel">
    <h3 class="text-lg font-semibold mb-4">Investiční strategie</h3>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div data-testid="selectbox" ref="dropdownRef" class="relative">
        <label class="field-label">Strategie</label>
        <button
          type="button"
          @click="isOpen = !isOpen"
          aria-haspopup="listbox"
          :aria-expanded="isOpen"
          class="field text-left flex justify-between items-center"
        >
          <span>{{ selectedLabel }}</span>
          <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        <ul
          v-if="isOpen"
          role="listbox"
          class="absolute z-10 w-full mt-1 bg-white border border-line rounded-md shadow-lg shadow-ink/10 max-h-60 overflow-auto py-1"
        >
          <li
            v-for="opt in strategyOptions"
            :key="opt.value"
            role="option"
            :aria-selected="strategy === opt.value"
            @click="selectOption(opt.value)"
            class="px-3 py-2 cursor-pointer hover:bg-petrol-50"
            :class="{ 'bg-petrol-50 text-petrol-700 font-medium': strategy === opt.value }"
          >
            {{ opt.label }}
          </li>
        </ul>
      </div>

      <div data-testid="number-input">
        <label class="field-label">Roční výnos [%]</label>
        <input
          type="number"
          :value="customRate ?? ''"
          @input="emit('update:customRate', Number(($event.target as HTMLInputElement).value))"
          :disabled="strategy !== 'custom'"
          step="0.1"
          class="field"
        />
      </div>
    </div>

    <div class="mt-4">
      <label class="inline-flex items-start gap-0.5 cursor-pointer">
        <input
          type="checkbox"
          :checked="investAfterPayoff"
          @change="emit('update:investAfterPayoff', ($event.target as HTMLInputElement).checked)"
          class="mr-2 size-4 accent-petrol-600"
        />
        <span class="text-sm leading-5">Po splacení kratší varianty investovat uvolněnou splátku</span>
      </label>
    </div>
  </div>
</template>
