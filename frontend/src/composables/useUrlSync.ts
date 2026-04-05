import { watch, type Ref } from 'vue'
import type { VariantInput } from '../types'

interface SyncState {
  principal: Ref<number>
  term: Ref<number>
  rate: Ref<number>
  refinancing_year: Ref<number>
  strategy: Ref<string>
  custom_rate: Ref<number | null>
  display_mode: Ref<string>
  inflation: Ref<number>
  variants: Ref<VariantInput[]>
  invest_after_payoff: Ref<boolean>
}

export function useUrlSync(state: SyncState) {
  // Read from URL on init
  const params = new URLSearchParams(window.location.search)

  if (params.has('principal')) state.principal.value = Number(params.get('principal'))
  if (params.has('term')) state.term.value = Number(params.get('term'))
  if (params.has('rate')) state.rate.value = Number(params.get('rate'))
  if (params.has('refi_year')) state.refinancing_year.value = Number(params.get('refi_year'))
  if (params.has('strategy')) state.strategy.value = params.get('strategy')!
  if (params.has('custom_rate')) {
    const v = params.get('custom_rate')
    state.custom_rate.value = v === 'null' ? null : Number(v)
  }
  if (params.has('mode')) state.display_mode.value = params.get('mode')!
  if (params.has('inflation')) state.inflation.value = Number(params.get('inflation'))
  if (params.has('variants')) {
    try {
      const raw = JSON.parse(params.get('variants')!) as any[]
      state.variants.value = raw.map((v: any) => ({
        refinancing_interest: v.refinancing_interest ?? v.rate ?? 4.39,
        length_change: v.length_change ?? v.years ?? 0,
        extra_principal: v.extra_principal ?? v.extra ?? 0,
      }))
    } catch {}
  }
  if (params.has('invest_after')) {
    const v = params.get('invest_after')
    state.invest_after_payoff.value = v === '1' || v === 'true'
  }

  // Write to URL on change
  const writeUrl = () => {
    const p = new URLSearchParams()
    p.set('principal', String(state.principal.value))
    p.set('term', String(state.term.value))
    p.set('rate', String(state.rate.value))
    p.set('refi_year', String(state.refinancing_year.value))
    p.set('strategy', state.strategy.value)
    p.set('custom_rate', String(state.custom_rate.value))
    p.set('mode', state.display_mode.value)
    p.set('inflation', String(state.inflation.value))
    p.set('variants', JSON.stringify(state.variants.value))
    p.set('invest_after', state.invest_after_payoff.value ? '1' : '0')

    const url = `${window.location.pathname}?${p.toString()}`
    window.history.replaceState({}, '', url)
  }

  watch(
    [
      state.principal, state.term, state.rate, state.refinancing_year,
      state.strategy, state.custom_rate, state.display_mode, state.inflation,
      state.variants, state.invest_after_payoff,
    ],
    writeUrl,
    { deep: true }
  )
}
