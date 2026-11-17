import { ref, watch } from 'vue'
import type { VariantInput, CalculateRequest, GraphResponse, SummaryResponse } from '../types'
import { useUrlSync } from './useUrlSync'

// Defaults describe a typical mortgage refinanced in late 2026: a 5-year fixation signed in 2021
// (avg. loan ~3.2M CZK, avg. rate 2.33 % per ČBA Hypomonitor) facing ~5.2 % today.
export const DEFAULT_NEW_RATE = 5.2
// Same limit as CalculateRequest.variants in api/models.py
export const MAX_VARIANTS = 10

export function useCalculator() {
  const principal = ref(3200000)
  const term = ref(30)
  const rate = ref(2.3)
  const refinancing_year = ref(5)
  const strategy = ref<string>('medium')
  const custom_rate = ref<number | null>(null)
  // On by default so both variants are compared fairly over the same horizon
  const invest_after_payoff = ref(true)
  const display_mode = ref<string>('nominal')
  const inflation = ref(2.0)
  const variants = ref<VariantInput[]>([
    { refinancing_interest: DEFAULT_NEW_RATE, length_change: 0, extra_principal: 0 },
    { refinancing_interest: DEFAULT_NEW_RATE, length_change: 5, extra_principal: 0 },
  ])

  const graphData = ref<GraphResponse | null>(null)
  const summaryData = ref<SummaryResponse | null>(null)
  const isLoading = ref(false)
  const errorMessage = ref<string | null>(null)

  useUrlSync({
    principal, term, rate, refinancing_year,
    strategy, custom_rate, display_mode, inflation,
    variants, invest_after_payoff,
  })

  let debounceTimer: ReturnType<typeof setTimeout> | null = null
  let latestRequest = 0

  const fetchData = async () => {
    const requestId = ++latestRequest
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

      // A newer request was sent meanwhile; its response wins
      if (requestId !== latestRequest) return

      if (graphRes.ok && summaryRes.ok) {
        graphData.value = await graphRes.json()
        summaryData.value = await summaryRes.json()
        errorMessage.value = null
      } else {
        // Don't leave results of the previous inputs on screen
        graphData.value = null
        summaryData.value = null
        const failed = graphRes.ok ? summaryRes : graphRes
        errorMessage.value = failed.status === 422
          ? validationMessage(await failed.json().catch(() => null))
          : 'Výpočet se nepodařil. Zkuste to prosím znovu.'
      }
    } catch (e) {
      console.error('API fetch error:', e)
      if (requestId === latestRequest) errorMessage.value = 'Výpočet se nepodařil. Zkontrolujte připojení a zkuste to znovu.'
    } finally {
      if (requestId === latestRequest) isLoading.value = false
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
    if (variants.value.length >= MAX_VARIANTS) return
    variants.value.push({ refinancing_interest: DEFAULT_NEW_RATE, length_change: 0, extra_principal: 0 })
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
    errorMessage,
    addVariant,
    removeVariant,
  }
}

const FIELD_LABELS: Record<string, string> = {
  principal: 'Splácená částka',
  term: 'Délka splácení',
  rate: 'Úrok',
  refinancing_year: 'Rok refinancování',
  custom_rate: 'Roční výnos',
  inflation: 'Roční inflace',
  refinancing_interest: 'Nový úrok',
  length_change: 'Prodloužit o',
  extra_principal: 'Navýšení úvěru',
}

/** Turns FastAPI's 422 body into one Czech sentence. */
function validationMessage(body: any): string {
  const first = Array.isArray(body?.detail) ? body.detail[0] : null
  if (!first) return 'Zadané hodnoty nejde spočítat. Zkontrolujte je prosím.'
  // Cross-field checks in api/models.py already carry a Czech message
  if (typeof first.msg === 'string' && first.msg.startsWith('Value error, ')) return first.msg.slice('Value error, '.length)
  const loc: (string | number)[] = first.loc ?? []
  const field = [...loc].reverse().find(part => typeof part === 'string' && part in FIELD_LABELS) as string | undefined
  const variant = loc.includes('variants') ? loc.find(part => typeof part === 'number') : undefined
  const where = variant !== undefined ? ` u varianty ${Number(variant) + 1}` : ''
  return field
    ? `Hodnota „${FIELD_LABELS[field]}“${where} je mimo povolený rozsah.`
    : 'Zadané hodnoty nejde spočítat. Zkontrolujte je prosím.'
}
