<script setup lang="ts">
import { useCalculator } from '../composables/useCalculator'
import SiteHeader from '../components/SiteHeader.vue'
import SiteFooter from '../components/SiteFooter.vue'
import GuideContent from '../components/GuideContent.vue'
import MortgageInputs from '../components/MortgageInputs.vue'
import InvestmentStrategy from '../components/InvestmentStrategy.vue'
import DisplayMode from '../components/DisplayMode.vue'
import VariantList from '../components/VariantList.vue'
import ComparisonChart from '../components/ComparisonChart.vue'
import SummaryTable from '../components/SummaryTable.vue'
import MilestoneTable from '../components/MilestoneTable.vue'
import Recommendation from '../components/Recommendation.vue'

const { state, graphData, summaryData, isLoading, addVariant, removeVariant } = useCalculator()

const updateVariants = (newVariants: any[]) => {
  state.variants.value = newVariants
}
</script>

<template>
  <SiteHeader />

  <main>
    <section id="kalkulacka" class="max-w-6xl mx-auto px-4 -mt-6 scroll-mt-4" aria-label="Zadání výpočtu">
      <div class="grid gap-4 lg:grid-cols-2 lg:items-start">
        <div class="flex flex-col gap-4">
          <MortgageInputs
            :principal="state.principal.value"
            @update:principal="state.principal.value = $event"
            :term="state.term.value"
            @update:term="state.term.value = $event"
            :rate="state.rate.value"
            @update:rate="state.rate.value = $event"
            :refinancingYear="state.refinancing_year.value"
            @update:refinancingYear="state.refinancing_year.value = $event"
          />

          <VariantList
            :variants="state.variants.value"
            @update:variants="updateVariants"
            :term="state.term.value"
            @add="addVariant"
            @remove="removeVariant"
          />
        </div>

        <div class="flex flex-col gap-4">
          <InvestmentStrategy
            :strategy="state.strategy.value"
            @update:strategy="state.strategy.value = $event"
            :customRate="state.custom_rate.value"
            @update:customRate="state.custom_rate.value = $event"
            :investAfterPayoff="state.invest_after_payoff.value"
            @update:investAfterPayoff="state.invest_after_payoff.value = $event"
          />

          <DisplayMode
            :displayMode="state.display_mode.value"
            @update:displayMode="state.display_mode.value = $event"
            :inflation="state.inflation.value"
            @update:inflation="state.inflation.value = $event"
          />
        </div>
      </div>
    </section>

    <section class="max-w-6xl mx-auto px-4 mt-4" aria-labelledby="porovnani">
      <div class="panel md:p-7">
        <h2 id="porovnani" class="text-2xl font-bold mb-1">Porovnání scénářů</h2>
        <p class="text-sm text-muted mb-5">
          Plná čára je zbývající dluh, přerušovaná hodnota investic. Kosočtverec značí měsíc, kdy investice stačí na doplacení hypotéky.
        </p>
        <ComparisonChart :graphData="graphData" />

        <div class="mt-10" v-if="summaryData">
          <Recommendation :recommendation="summaryData.recommendation" />

          <h2 class="text-xl font-bold mb-3">Souhrn variant</h2>
          <SummaryTable
            v-if="summaryData.summary.length"
            :summary="summaryData.summary"
          />

          <div class="mt-10" v-if="summaryData.milestones.length">
            <h2 class="text-xl font-bold mb-1">Stav v klíčových okamžicích</h2>
            <p class="text-sm text-muted mb-5">Nejvýhodnější varianta v daném okamžiku je zvýrazněná zeleně.</p>
            <MilestoneTable
              v-for="(ms, i) in summaryData.milestones"
              :key="i"
              :label="ms.label"
              :rows="ms.rows"
            />
          </div>
        </div>
      </div>
    </section>

    <GuideContent />
  </main>

  <SiteFooter />

  <!-- Loading indicator: small pill so the page doesn't flash on every keystroke -->
  <div
    v-if="isLoading"
    data-testid="loading-indicator"
    role="status"
    class="fixed bottom-4 right-4 z-50 flex items-center gap-2 rounded-full bg-ink text-white px-4 py-2 text-sm shadow-lg"
  >
    <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    <span>Přepočítávám…</span>
  </div>
</template>
