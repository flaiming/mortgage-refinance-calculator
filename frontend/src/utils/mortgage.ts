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
  /** Index of the variant with the highest payment; that payment is the common monthly budget. */
  referenceIndex: number
  /** Monthly amount this variant invests: the budget minus its own payment. */
  savings: number
}

export function computeVariantPayments(
  principal: number,
  ratePct: number,
  termYears: number,
  refinancingYear: number,
  variants: VariantInput[],
): { originalPayment: number | null; variants: VariantPayment[] } {
  // Same limits as api/models.py
  const valid = principal > 0 && ratePct >= 0.1 && ratePct <= 30 && termYears > 1 && termYears <= 50 && refinancingYear > 0 && refinancingYear < termYears
  const originalPayment = valid ? annuityPayment(principal, ratePct, termYears * 12) : null
  const balance = valid ? balanceAfter(principal, ratePct, termYears * 12, refinancingYear * 12) : 0

  const payments = variants.map(v => {
    const years = termYears - refinancingYear + v.length_change
    if (!valid || years <= 0 || years > 50 || !(v.refinancing_interest >= 0.1) || v.refinancing_interest > 30) return null
    return annuityPayment(balance + (v.extra_principal || 0), v.refinancing_interest, years * 12)
  })

  // Same as modules/comparison.py: every variant spends the highest payment as its monthly
  // budget and invests what is left after its own payment.
  let ref = -1
  payments.forEach((pay, i) => {
    if (pay !== null && (ref === -1 || pay > (payments[ref] as number))) ref = i
  })
  const budget = ref === -1 ? null : payments[ref]

  return {
    originalPayment,
    variants: payments.map(pay => {
      const leftover = pay !== null && budget !== null ? budget - pay : 0
      return { payment: pay, referenceIndex: ref, savings: Math.max(0, leftover) }
    }),
  }
}
