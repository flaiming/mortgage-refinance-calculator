<script setup lang="ts">
import { faq } from '../content/faq'

const steps = [
  'Sestaví splátkový kalendář původní hypotéky s anuitní splátkou až do roku, kdy končí fixace.',
  'Zbývající dluh přepočítá s novou sazbou a zvolenou splatností pro každou variantu, případně navýšený o další půjčenou částku.',
  'Nejvyšší z nových splátek bere jako měsíční rozpočet, který utratí každá varianta. Kdo splácí méně, rozdíl každý měsíc investuje se zvoleným ročním výnosem. Kdo splatí dřív, investuje pak celý rozpočet až do konce nejdelší varianty.',
  'Pro každou variantu spočítá čisté náklady: zaplacené úroky minus daňová úspora z odpočtu úroků a minus výnos investic. Protože všechny varianty utratí stejně, nejnižší čisté náklady znamenají, že vám na konci zůstane nejvíc peněz.',
]
</script>

<template>
  <section class="max-w-6xl mx-auto px-4 mt-16 md:mt-20" aria-labelledby="jak-pocita">
    <div class="grid gap-12 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] lg:gap-16">
      <div class="prose-block">
        <h2 id="jak-pocita" class="text-2xl md:text-3xl font-bold mb-5">Jak kalkulačka počítá</h2>
        <ol class="space-y-4">
          <li v-for="(step, i) in steps" :key="i" class="grid grid-cols-[2rem_1fr] gap-3">
            <span
              class="flex size-8 items-center justify-center rounded-full bg-petrol-100 text-petrol-900 font-semibold text-sm"
              aria-hidden="true"
            >{{ i + 1 }}</span>
            <span class="pt-0.5">{{ step }}</span>
          </li>
        </ol>
      </div>

      <div class="prose-block">
        <h2 class="text-2xl md:text-3xl font-bold mb-5">Refixace, nebo refinancování?</h2>
        <p>
          <strong>Refixace</strong> znamená, že u své banky zůstanete a jen si sjednáte novou úrokovou sazbu
          na další fixační období. <strong>Refinancování</strong> je převedení hypotéky do jiné banky,
          která nabízí lepší podmínky. Obojí se nejčastěji řeší ke konci fixace, kdy lze dluh splatit
          bez sankce.
        </p>
        <p>
          Pro kalkulačku je to jedno: zadáte novou sazbu, kterou máte v nabídce, a uvidíte, co udělá
          se splátkou a s celkovými náklady. Přidejte víc variant a porovnejte nabídky několika bank vedle sebe.
        </p>
      </div>
    </div>

    <div class="prose-block mt-14 max-w-[70ch]">
      <h2 class="text-2xl md:text-3xl font-bold mb-5">Splácet rychleji, nebo investovat rozdíl?</h2>
      <p>
        Když po fixaci vzroste úrok a délka splácení zůstane stejná, vyskočí měsíční splátka.
        Druhou cestou je prodloužit splatnost: splátka bude nižší, na úrocích ale zaplatíte víc.
      </p>
      <p>
        Kalkulačka předpokládá, že si na nejvyšší ze splátek můžete dovolit, a se stejnou částkou počítá
        u všech variant. Kdo zvolí delší splatnost, rozdíl každý měsíc investuje. Kdo splatí dřív, začne
        pak investovat celý měsíční rozpočet, takže se všechny cesty porovnávají férově ve stejném horizontu.
        Pokud investice vynášejí víc, než stojí úrok hypotéky po odečtení daňové úspory, delší splatnost
        se vyplatí. Graf ukazuje, kdy investice dorovnají zbývající
        dluh, a tabulky porovnávají všechny varianty ve stejném časovém horizontu.
      </p>
    </div>
  </section>

  <section class="max-w-6xl mx-auto px-4 mt-16 md:mt-20" aria-labelledby="caste-otazky">
    <h2 id="caste-otazky" class="text-2xl md:text-3xl font-bold mb-6">Časté otázky</h2>
    <div class="max-w-[75ch] border-t border-line">
      <details v-for="item in faq" :key="item.question" class="group border-b border-line">
        <summary
          class="flex cursor-pointer list-none items-center justify-between gap-4 py-4 text-lg font-medium hover:text-petrol-700 [&::-webkit-details-marker]:hidden"
        >
          <h3 class="font-sans font-medium tracking-normal">{{ item.question }}</h3>
          <svg class="size-5 shrink-0 text-muted transition-transform group-open:rotate-45" viewBox="0 0 20 20" fill="none" aria-hidden="true">
            <path d="M10 4v12M4 10h12" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" />
          </svg>
        </summary>
        <p class="pb-5 pr-9 leading-relaxed text-ink/85">{{ item.answer }}</p>
      </details>
    </div>
  </section>
</template>
