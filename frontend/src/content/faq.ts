// Single source for the FAQ: rendered on the page and injected into index.html
// as schema.org FAQPage JSON-LD at build time (see vite.config.ts).
// Keep answers as plain text so both outputs stay identical.

export interface FaqItem {
  question: string
  answer: string
}

export const SITE_URL = 'https://hypo.vojtechoram.cz/'

export const faq: FaqItem[] = [
  {
    question: 'Kdy se vyplatí refinancovat hypotéku?',
    answer:
      'Nejvhodnější chvíle je konec fixace. Tehdy můžete zbývající dluh splatit nebo převést k jiné bance bez sankce za předčasné splacení. Nabídku refixace od své banky dostanete předem, takže máte čas porovnat ji s nabídkami ostatních bank. Mimo konec fixace banka může požadovat náhradu nákladů spojených s předčasným splacením.',
  },
  {
    question: 'Je lepší zachovat délku splácení, nebo ji prodloužit?',
    answer:
      'Záleží na tom, co s nižší splátkou uděláte. Delší splatnost znamená víc zaplacených úroků. Pokud ale rozdíl ve splátce pravidelně investujete a investice vydělávají víc, než kolik vás stojí úrok hypotéky po odečtení daňové úspory, může delší varianta vyjít lépe. Kratší varianta zase po splacení hypotéky investuje celý měsíční rozpočet, tedy nejvyšší z nových splátek. Kalkulačka obě cesty porovná ve stejném horizontu a se stejnou měsíční částkou a ukáže, ve kterém měsíci by naspořené investice stačily na doplacení zbývajícího dluhu.',
  },
  {
    question: 'Podle čeho kalkulačka vybírá nejvýhodnější variantu?',
    answer:
      'Podle čistých nákladů na konci nejdelší varianty. Čisté náklady jsou zaplacené úroky minus daňová úspora a minus výnos investic, tedy to, o kolik investice vzrostly nad peníze, které jste do nich sami vložili. Všechny varianty přitom měsíčně utratí stejnou částku, nejvyšší z nových splátek, takže nejnižší čisté náklady znamenají nejvíc peněz na konci. Nejvýhodnější varianta je v tabulkách zvýrazněná zeleně.',
  },
  {
    question: 'Jak kalkulačka počítá s odpočtem úroků z daní?',
    answer:
      'Zaplacené úroky z hypotéky na bydlení si lze odečíst od základu daně. Kalkulačka počítá s 15% sazbou daně z příjmů a ročním limitem odpočtu 150 000 Kč. Skutečná úspora závisí na vašich příjmech a na tom, kdy jste úvěr sjednali.',
  },
  {
    question: 'Jaký výnos investic mám zvolit?',
    answer:
      'Konzervativní strategie počítá se 4 % ročně, vyvážená se 6 % a dynamická s 8 %. Můžete zadat i vlastní výnos. Model počítá s pevným výnosem každý rok, bez výkyvů trhu, poplatků a daně z výnosu, takže výsledky berte jako orientační. Vyzkoušejte víc strategií a uvidíte, jak citlivý je výsledek na výši výnosu.',
  },
  {
    question: 'Jaký je rozdíl mezi nominálním a reálným zobrazením?',
    answer:
      'Nominální hodnoty jsou částky tak, jak je skutečně zaplatíte. Reálné hodnoty přepočítávají každou platbu na kupní sílu v době sjednání hypotéky podle zadané inflace. Splátka 10 000 Kč za dvacet let má reálně menší váhu než dnes. Proto reálné zobrazení ukazuje i inflační úlevu na jistině: dluh splácíte penězi, které mezitím ztratily hodnotu, a u delší splatnosti je tahle úleva větší.',
  },
  {
    question: 'Můžu výpočet uložit nebo poslat dál?',
    answer:
      'Ano. Všechny zadané hodnoty se průběžně ukládají do adresy stránky. Stačí zkopírovat odkaz z prohlížeče a po otevření se zobrazí stejný výpočet.',
  },
  {
    question: 'Nahrazuje kalkulačka finančního poradce?',
    answer:
      'Ne. Jde o zjednodušený model, který pomáhá pochopit souvislosti mezi úrokem, délkou splácení a investováním. Před podpisem smlouvy si ověřte podmínky u banky a zvažte svou finanční rezervu a toleranci k riziku.',
  },
]

export function faqJsonLd() {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faq.map(item => ({
      '@type': 'Question',
      name: item.question,
      acceptedAnswer: { '@type': 'Answer', text: item.answer },
    })),
  }
}
