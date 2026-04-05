<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  summary: Record<string, any>[]
}>()

const scenarios = computed(() => props.summary.map(s => s['Scénář'] || ''))

const rowKeys = computed(() => {
  if (!props.summary.length) return []
  return Object.keys(props.summary[0]).filter(k => k !== 'Scénář')
})
</script>

<template>
  <div class="overflow-x-auto">
    <table data-testid="table" class="w-full border-collapse border border-gray-300 text-sm">
      <thead>
        <tr class="bg-gray-100">
          <th class="border border-gray-300 px-3 py-2 text-left"></th>
          <th
            v-for="(s, i) in scenarios"
            :key="i"
            class="border border-gray-300 px-3 py-2 text-left"
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
            v-for="(s, si) in summary"
            :key="si"
            class="border border-gray-300 px-3 py-2"
          >
            {{ s[key] }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
