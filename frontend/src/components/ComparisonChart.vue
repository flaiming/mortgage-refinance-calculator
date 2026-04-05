<script setup lang="ts">
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import type { GraphResponse } from '../types'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const props = defineProps<{
  graphData: GraphResponse | null
}>()

const COLORS = ['#1f77b4', '#d62728', '#2ca02c', '#ff7f0e', '#9467bd', '#8c564b']

const chartData = computed(() => {
  if (!props.graphData) return { labels: [], datasets: [] }

  const labels = props.graphData.months.map(m => `${m} (${Math.floor(m / 12)}. rok)`)

  // Group series by variant name (strip suffix)
  const variantNames: string[] = []
  for (const key of Object.keys(props.graphData.series)) {
    const base = key.replace(/ - zůstatek$/, '').replace(/ - investice$/, '')
    if (!variantNames.includes(base)) variantNames.push(base)
  }

  const datasets = Object.entries(props.graphData.series).map(([name, data]) => {
    const base = name.replace(/ - zůstatek$/, '').replace(/ - investice$/, '')
    const colorIndex = variantNames.indexOf(base) % COLORS.length
    const isInvestment = name.includes(' - investice')

    return {
      label: name,
      data: data.map(v => (v === null ? NaN : v)),
      borderColor: COLORS[colorIndex],
      backgroundColor: COLORS[colorIndex],
      borderDash: isInvestment ? [5, 5] : [],
      borderWidth: 2,
      pointRadius: 0,
      spanGaps: false,
      tension: 0,
    }
  })

  // Add payoff markers as separate datasets
  if (props.graphData.payoff_markers?.length) {
    for (const marker of props.graphData.payoff_markers) {
      const base = marker.variant
      const colorIndex = variantNames.indexOf(base) % COLORS.length

      // Find the label index closest to marker.x
      const labelIdx = props.graphData.months.indexOf(marker.x)
      if (labelIdx === -1) continue

      const pointData: (number | null)[] = new Array(props.graphData.months.length).fill(null)
      pointData[labelIdx] = marker.y

      datasets.push({
        label: marker.label,
        data: pointData.map(v => (v === null ? NaN : v)),
        borderColor: COLORS[colorIndex],
        backgroundColor: COLORS[colorIndex],
        borderDash: [],
        borderWidth: 0,
        pointRadius: 8,
        spanGaps: false,
        tension: 0,
        pointStyle: 'rectRot' as any,
      } as any)
    }
  }

  return { labels, datasets }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index' as const,
    intersect: false,
  },
  scales: {
    x: {
      ticks: {
        maxTicksLimit: 20,
        callback: function (_value: any, index: number) {
          if (!props.graphData) return ''
          const m = props.graphData.months[index]
          if (m % 12 === 0) return `${m} (${m / 12}. rok)`
          return ''
        },
      },
    },
    y: {
      ticks: {
        callback: function (value: any) {
          return Number(value).toLocaleString('cs-CZ') + ' Kč'
        },
      },
    },
  },
  plugins: {
    tooltip: {
      callbacks: {
        label: function (ctx: any) {
          const val = ctx.parsed.y
          if (val === null || isNaN(val)) return ''
          return `${ctx.dataset.label}: ${val.toLocaleString('cs-CZ')} Kč`
        },
      },
    },
  },
}))
</script>

<template>
  <div data-testid="chart" class="w-full" style="height: 400px;">
    <Line
      v-if="graphData"
      :data="chartData"
      :options="chartOptions"
    />
    <div v-else class="flex items-center justify-center h-full text-gray-400">
      Načítání grafu...
    </div>
  </div>
</template>
