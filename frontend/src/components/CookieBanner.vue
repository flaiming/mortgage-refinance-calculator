<script setup lang="ts">
import { useConsent } from '../composables/useConsent'

const { bannerOpen, accept, reject } = useConsent()
</script>

<template>
  <section
    v-if="bannerOpen"
    data-testid="cookie-banner"
    aria-labelledby="cookie-banner-title"
    class="fixed inset-x-0 bottom-0 z-40 p-3 sm:inset-x-auto sm:left-4 sm:bottom-4 sm:p-0 sm:max-w-md"
  >
    <div class="rounded-xl border border-line bg-white p-5 shadow-xl shadow-ink/15">
      <h2 id="cookie-banner-title" class="text-base font-semibold">Měření návštěvnosti</h2>
      <p class="mt-2 text-sm leading-relaxed text-muted">
        Rádi bychom pomocí Google Analytics zjistili, jak lidé kalkulačku používají, abychom ji mohli zlepšovat.
        Analytické cookies uložíme jen s vaším souhlasem. Kalkulačka funguje stejně i bez nich.
      </p>
      <div class="mt-4 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <button
          type="button"
          class="rounded-md border border-line px-4 py-2 text-sm font-medium text-ink hover:bg-paper"
          @click="reject"
        >
          Odmítnout
        </button>
        <button
          type="button"
          class="rounded-md bg-petrol-700 px-4 py-2 text-sm font-medium text-white hover:bg-petrol-900"
          @click="accept"
        >
          Povolit měření
        </button>
      </div>
    </div>
  </section>
</template>
