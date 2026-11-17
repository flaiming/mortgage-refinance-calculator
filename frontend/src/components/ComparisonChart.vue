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

// First series is always the "no refinancing" baseline, so it gets the neutral slate.
const COLORS = ['#7b8798', '#0e6a78', '#d4553a', '#c98a1c', '#5b5fa8', '#2f8a57']

ChartJS.defaults.font.family = '"IBM Plex Sans", ui-sans-serif, system-ui, sans-serif'
ChartJS.defaults.color = '#566273'

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
      pointStyle: 'line' as any,
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
      // One tick per month; label and grid line only every 5 (mobile: 10) years to keep the axis readable
      grid: {
        color: (ctx: any) => (ctx.tick?.label ? '#e6eaef' : 'transparent'),
      },
      ticks: {
        autoSkip: false,
        maxRotation: 0,
        callback: function (_value: any, index: number) {
          if (!props.graphData) return ''
          const m = props.graphData.months[index]
          // Evaluated on every redraw, so it follows window resizes
          const stepMonths = window.innerWidth < 640 ? 120 : 60
          return m % stepMonths === 0 ? `${m / 12}. rok` : ''
        },
      },
    },
    y: {
      grid: { color: '#e6eaef' },
      border: { display: false },
      ticks: {
        callback: function (value: any) {
          return Number(value).toLocaleString('cs-CZ') + ' Kč'
        },
      },
    },
  },
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: { usePointStyle: true, boxWidth: 28, boxHeight: 10, padding: 14 },
    },
    tooltip: {
      backgroundColor: '#16212e',
      padding: 10,
      bodySpacing: 4,
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
  <div data-testid="chart" class="w-full h-[360px] md:h-[440px]">
    <Line
      v-if="graphData"
      :data="chartData"
      :options="chartOptions"
    />
    <div v-else class="flex items-center justify-center h-full text-muted">
      Načítání grafu...
    </div>
  </div>
</template>
