export interface VariantInput {
  refinancing_interest: number
  length_change: number
  extra_principal: number
}

export interface CalculateRequest {
  principal: number
  term: number
  rate: number
  refinancing_year: number
  strategy: 'safe' | 'medium' | 'risky' | 'custom'
  custom_rate: number | null
  invest_after_payoff: boolean
  display_mode: 'nominal' | 'real'
  inflation: number
  variants: VariantInput[]
}

export interface PayoffMarker {
  x: number
  y: number
  variant: string
  label: string
}

export interface GraphResponse {
  months: number[]
  series: Record<string, (number | null)[]>
  payoff_markers: PayoffMarker[]
}

export interface MilestoneData {
  label: string
  rows: Record<string, any>[]
}

export interface SummaryResponse {
  summary: Record<string, any>[]
  milestones: MilestoneData[]
  recommendation: string | null
  ranked_variants: Record<string, any>[]
}
