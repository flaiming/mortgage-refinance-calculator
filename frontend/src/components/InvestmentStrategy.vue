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
  <div class="border border-gray-300 rounded-lg p-4 mb-4">
    <h3 class="text-lg font-semibold mb-3">Investiční strategie</h3>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div data-testid="selectbox" ref="dropdownRef" class="relative">
        <label class="block text-sm font-medium text-gray-700 mb-1">Strategie</label>
        <button
          type="button"
          @click="isOpen = !isOpen"
          class="w-full border border-gray-300 rounded px-3 py-2 text-left bg-white flex justify-between items-center"
        >
          <span>{{ selectedLabel }}</span>
          <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        <ul
          v-if="isOpen"
          class="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded shadow-lg max-h-60 overflow-auto"
        >
          <li
            v-for="opt in strategyOptions"
            :key="opt.value"
            role="option"
            :aria-selected="strategy === opt.value"
            @click="selectOption(opt.value)"
            class="px-3 py-2 cursor-pointer hover:bg-blue-50"
            :class="{ 'bg-blue-100': strategy === opt.value }"
          >
            {{ opt.label }}
          </li>
        </ul>
      </div>

      <div data-testid="number-input">
        <label class="block text-sm font-medium text-gray-700 mb-1">Roční výnos [%]</label>
        <input
          type="number"
          :value="customRate ?? ''"
          @input="emit('update:customRate', Number(($event.target as HTMLInputElement).value))"
          :disabled="strategy !== 'custom'"
          step="0.1"
          class="w-full border border-gray-300 rounded px-3 py-2 disabled:bg-gray-100 disabled:text-gray-400"
        />
      </div>
    </div>

    <div class="mt-3">
      <label class="inline-flex items-center cursor-pointer">
        <input
          type="checkbox"
          :checked="investAfterPayoff"
          @change="emit('update:investAfterPayoff', ($event.target as HTMLInputElement).checked)"
          class="mr-2"
        />
        <span class="text-sm">Po splacení kratší varianty investovat uvolněnou splátku</span>
      </label>
    </div>
  </div>
</template>
