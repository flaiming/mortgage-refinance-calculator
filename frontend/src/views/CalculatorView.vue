<script setup lang="ts">
import { useCalculator } from '../composables/useCalculator'
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
  <div class="max-w-5xl mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold text-center mb-6">Kalkulačka refinancování hypotéky</h1>

    <div class="mb-6 text-gray-700 space-y-2">
      <p>
        Tato kalkulačka vám pomůže porovnat různé scénáře refinancování hypotéky.
        Zadejte parametry vaší současné hypotéky, zvolte investiční strategii
        a porovnejte různé varianty refinancování.
      </p>
      <p>
        Kalkulačka počítá s anuitním splácením a umožňuje porovnat, zda je výhodnější
        zkrátit dobu splácení, nebo investovat rozdíl ve splátkách.
      </p>
    </div>

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

    <VariantList
      :variants="state.variants.value"
      @update:variants="updateVariants"
      :term="state.term.value"
      @add="addVariant"
      @remove="removeVariant"
    />

    <div class="mt-8">
      <h2 class="text-xl font-bold mb-4">Porovnání scénářů</h2>
      <ComparisonChart :graphData="graphData" />
    </div>

    <div class="mt-8" v-if="summaryData">
      <Recommendation :recommendation="summaryData.recommendation" />

      <h2 class="text-xl font-bold mb-4">Souhrn variant</h2>
      <SummaryTable
        v-if="summaryData.summary.length"
        :summary="summaryData.summary"
      />

      <div class="mt-8" v-if="summaryData.milestones.length">
        <MilestoneTable
          v-for="(ms, i) in summaryData.milestones"
          :key="i"
          :label="ms.label"
          :rows="ms.rows"
        />
      </div>
    </div>

    <!-- Loading indicator -->
    <div
      v-if="isLoading"
      data-testid="loading-indicator"
      class="fixed inset-0 bg-black/20 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 shadow-xl flex items-center gap-3">
        <svg class="animate-spin h-6 w-6 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span>Načítání...</span>
      </div>
    </div>
  </div>
</template>
