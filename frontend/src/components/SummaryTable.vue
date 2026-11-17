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
    <table data-testid="table" class="data-table">
      <thead>
        <tr>
          <th></th>
          <th
            v-for="(s, i) in scenarios"
            :key="i"
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
            v-for="(s, si) in summary"
            :key="si"
          >
            {{ s[key] }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
