<script setup lang="ts">
import { useConsent } from '../composables/useConsent'

const { openSettings } = useConsent()
</script>

<template>
  <footer class="mt-20 border-t border-line bg-white">
    <div class="max-w-6xl mx-auto px-4 py-10 grid gap-6 md:grid-cols-[2fr_1fr] text-sm text-muted leading-relaxed">
      <div class="space-y-3 max-w-[70ch]">
        <p>
          Kalkulačka vznikla na hackathonu ENGETO zaměřeném na finanční gramotnost, kde tým s tímto nápadem
          <a class="text-petrol-700 underline underline-offset-2 hover:text-petrol-900" href="https://zpravy.kurzy.cz/791857-vitezem-hackathonu-se-zamerenim-na-financni-gramotnost-se-stal-tym-ktery-vytvoril-kalkulacku-pro/" rel="noopener">zvítězil</a>.
        </p>
        <p>
          Výsledky jsou orientační a nejsou finančním ani daňovým poradenstvím. Model počítá s anuitním splácením,
          pevným výnosem investic a zjednodušeným daňovým odpočtem.
        </p>
      </div>
      <ul class="flex flex-col gap-2.5 md:items-end">
        <li class="flex items-center gap-2">
          <svg class="size-4 shrink-0 text-muted" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
            <circle cx="12" cy="8" r="4" />
            <path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7" />
          </svg>
          <span>
            Vytvořil
            <a class="font-medium text-petrol-700 underline-offset-2 hover:underline hover:text-petrol-900" href="https://vojtechoram.cz/" rel="author">Vojtěch Oram</a>
          </span>
        </li>
        <li>
          <a class="flex items-center gap-2 font-medium text-petrol-700 underline-offset-2 hover:underline hover:text-petrol-900" href="https://github.com/flaiming/mortgage-refinance-calculator" rel="noopener">
            <svg class="size-4 shrink-0 text-ink" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
              <path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z" />
            </svg>
            Zdrojový kód na GitHubu
          </a>
        </li>
        <li>
          <button type="button" class="flex items-center gap-2 font-medium text-petrol-700 underline-offset-2 hover:underline hover:text-petrol-900" @click="openSettings">
            <svg class="size-4 shrink-0 text-muted" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M21 12.5A9 9 0 1 1 11.5 3a3 3 0 0 0 3.5 3.5 3 3 0 0 0 3.5 3.5 3 3 0 0 0 2.5 2.5Z" />
              <circle cx="8.5" cy="10.5" r=".5" fill="currentColor" />
              <circle cx="15.5" cy="15.5" r=".5" fill="currentColor" />
              <circle cx="10" cy="16" r=".5" fill="currentColor" />
            </svg>
            Nastavení cookies
          </button>
        </li>
      </ul>
    </div>
  </footer>
</template>
