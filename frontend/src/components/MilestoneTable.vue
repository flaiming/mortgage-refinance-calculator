<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string
  rows: Record<string, any>[]
}>()

const scenarios = computed(() => props.rows.map(r => r['Scénář'] || ''))

const rowKeys = computed(() => {
  if (!props.rows.length) return []
  return Object.keys(props.rows[0]).filter(k => k !== 'Scénář')
})

// Find the index of the best variant (highest "Zisk/ztráta" value)
const bestIndex = computed(() => {
  if (!props.rows.length) return -1
  let best = -1
  let bestVal = -Infinity
  for (let i = 0; i < props.rows.length; i++) {
    const raw = props.rows[i]['Zisk/ztráta']
    if (raw === undefined) continue
    const num = typeof raw === 'number' ? raw : Number(String(raw).replace(/\s/g, '').replace(/[^0-9,.-]/g, '').replace(',', '.'))
    if (!isNaN(num) && num > bestVal) {
      bestVal = num
      best = i
    }
  }
  return best
})
</script>

<template>
  <div class="mb-6">
    <h3 class="text-lg font-semibold mb-2">{{ label }}</h3>
    <div class="overflow-x-auto">
      <table data-testid="table" class="w-full border-collapse border border-gray-300 text-sm">
        <thead>
          <tr class="bg-gray-100">
            <th class="border border-gray-300 px-3 py-2 text-left"></th>
            <th
              v-for="(s, i) in scenarios"
              :key="i"
              class="border border-gray-300 px-3 py-2 text-left"
              :class="{ 'bg-green-100': i === bestIndex }"
            >
              {{ s }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(key, ri) in rowKeys"
            :key="key"
            :class="ri % 2 === 0 ? 'bg-white' : 'bg-gray-50'"
          >
            <td class="border border-gray-300 px-3 py-2 font-medium">{{ key }}</td>
            <td
              v-for="(r, si) in rows"
              :key="si"
              class="border border-gray-300 px-3 py-2"
              :class="{ 'bg-green-50': si === bestIndex }"
            >
              {{ r[key] }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
