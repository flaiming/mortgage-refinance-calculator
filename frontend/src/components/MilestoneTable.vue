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
  <div class="mb-8">
    <h3 class="text-base font-semibold mb-2">{{ label }}</h3>
    <div class="overflow-x-auto">
      <table data-testid="table" class="data-table">
        <thead>
          <tr>
            <th></th>
            <th
              v-for="(s, i) in scenarios"
              :key="i"
              :class="{ '!bg-gain-50 !text-gain': i === bestIndex }"
            >
              {{ s }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(key, ri) in rowKeys"
            :key="key"
          >
            <td>{{ key }}</td>
            <td
              v-for="(r, si) in rows"
              :key="si"
              :class="{ 'bg-gain-50/60 font-medium': si === bestIndex }"
            >
              {{ r[key] }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
