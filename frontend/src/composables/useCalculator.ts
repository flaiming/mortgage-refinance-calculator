import { ref, watch } from 'vue'
import type { VariantInput, CalculateRequest, GraphResponse, SummaryResponse } from '../types'
import { useUrlSync } from './useUrlSync'

export function useCalculator() {
  const principal = ref(2500000)
  const term = ref(30)
  const rate = ref(1.69)
  const refinancing_year = ref(7)
  const strategy = ref<string>('medium')
  const custom_rate = ref<number | null>(null)
  const invest_after_payoff = ref(false)
  const display_mode = ref<string>('nominal')
  const inflation = ref(2.0)
  const variants = ref<VariantInput[]>([
    { refinancing_interest: 4.39, length_change: 0, extra_principal: 0 },
    { refinancing_interest: 4.39, length_change: 7, extra_principal: 0 },
  ])

  const graphData = ref<GraphResponse | null>(null)
  const summaryData = ref<SummaryResponse | null>(null)
  const isLoading = ref(false)

  useUrlSync({
    principal, term, rate, refinancing_year,
    strategy, custom_rate, display_mode, inflation,
    variants, invest_after_payoff,
  })

  let debounceTimer: ReturnType<typeof setTimeout> | null = null

  const fetchData = async () => {
    isLoading.value = true
    const body: CalculateRequest = {
      principal: principal.value,
      term: term.value,
      rate: rate.value,
      refinancing_year: refinancing_year.value,
      strategy: strategy.value as CalculateRequest['strategy'],
      custom_rate: strategy.value === 'custom' ? custom_rate.value : null,
      invest_after_payoff: invest_after_payoff.value,
      display_mode: display_mode.value as CalculateRequest['display_mode'],
      inflation: inflation.value,
      variants: variants.value,
    }

    try {
      const [graphRes, summaryRes] = await Promise.all([
        fetch('/api/graph', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        }),
        fetch('/api/summary', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        }),
      ])

      if (graphRes.ok) {
        graphData.value = await graphRes.json()
      }
      if (summaryRes.ok) {
        summaryData.value = await summaryRes.json()
      }
    } catch (e) {
      console.error('API fetch error:', e)
    } finally {
      isLoading.value = false
    }
  }

  const debouncedFetch = () => {
    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(fetchData, 300)
  }

  watch(
    [principal, term, rate, refinancing_year, strategy, custom_rate, invest_after_payoff, display_mode, inflation, variants],
    debouncedFetch,
    { deep: true }
  )

  // Initial fetch
  fetchData()

  const addVariant = () => {
    variants.value.push({ refinancing_interest: 4.39, length_change: 0, extra_principal: 0 })
  }

  const removeVariant = (index: number) => {
    if (index >= 2 && variants.value.length > 2) {
      variants.value.splice(index, 1)
    }
  }

  return {
    state: {
      principal, term, rate, refinancing_year,
      strategy, custom_rate, invest_after_payoff,
      display_mode, inflation, variants,
    },
    graphData,
    summaryData,
    isLoading,
    addVariant,
    removeVariant,
  }
}
