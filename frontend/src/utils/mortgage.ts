import type { VariantInput } from '../types'

// Mirrors the annuity maths in modules/loan_with_refinancing.py so the variant cards
// can show payments instantly while the API recalculates the full comparison.

export function annuityPayment(principal: number, ratePct: number, months: number): number {
  const r = ratePct / 100 / 12
  if (months <= 0) return NaN
  if (r === 0) return principal / months
  return (principal * r) / (1 - Math.pow(1 + r, -months))
}

export function balanceAfter(principal: number, ratePct: number, months: number, paid: number): number {
  const r = ratePct / 100 / 12
  const pay = annuityPayment(principal, ratePct, months)
  if (r === 0) return principal - pay * paid
  const g = Math.pow(1 + r, paid)
  return principal * g - pay * ((g - 1) / r)
}

export interface VariantPayment {
  payment: number | null
  /** Index of the variant whose payment is the baseline for investing (shortest term with the same rate). */
  referenceIndex: number
  /** Monthly amount invested by this variant (0 for the reference itself). */
  savings: number
}

export function computeVariantPayments(
  principal: number,
  ratePct: number,
  termYears: number,
  refinancingYear: number,
  variants: VariantInput[],
): { originalPayment: number | null; variants: VariantPayment[] } {
  const valid = principal > 0 && ratePct > 0 && termYears > 1 && refinancingYear > 0 && refinancingYear < termYears
  const originalPayment = valid ? annuityPayment(principal, ratePct, termYears * 12) : null
  const balance = valid ? balanceAfter(principal, ratePct, termYears * 12, refinancingYear * 12) : 0

  const payments = variants.map(v => {
    const years = termYears - refinancingYear + v.length_change
    if (!valid || years <= 0 || !(v.refinancing_interest > 0)) return null
    return annuityPayment(balance + (v.extra_principal || 0), v.refinancing_interest, years * 12)
  })

  // Same grouping as modules/comparison.py: per rate, the shortest variant is the reference.
  const referenceFor = (i: number) => {
    let ref = i
    variants.forEach((v, j) => {
      if (v.refinancing_interest !== variants[i].refinancing_interest) return
      if (v.length_change < variants[ref].length_change) ref = j
      else if (v.length_change === variants[ref].length_change && j < ref) ref = j
    })
    return ref
  }

  return {
    originalPayment,
    variants: variants.map((_, i) => {
      const ref = referenceFor(i)
      const pay = payments[i]
      const refPay = payments[ref]
      const savings = ref !== i && pay !== null && refPay !== null ? Math.max(0, refPay - pay) : 0
      return { payment: pay, referenceIndex: ref, savings }
    }),
  }
}
