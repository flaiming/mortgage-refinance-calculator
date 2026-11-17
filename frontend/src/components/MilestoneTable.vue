<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string
  rows: Record<string, any>[]
  best: string | null
}>()

const scenarios = computed(() => props.rows.map(r => r['Scénář'] || ''))

const rowKeys = computed(() => {
  if (!props.rows.length) return []
  return Object.keys(props.rows[0]).filter(k => k !== 'Scénář')
})

// Lowest "Čisté náklady"; the API compares unrounded numbers, the cells are already formatted
const bestIndex = computed(() => scenarios.value.indexOf(props.best ?? ''))
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
