<template>
  <header class="bg-petrol-900 text-white">
    <div class="max-w-6xl mx-auto px-4 pt-10 pb-12 md:pt-14 md:pb-16 grid gap-10 md:grid-cols-[1fr_1.15fr] md:items-center">
      <div>
        <h1 class="text-4xl md:text-5xl font-bold leading-[1.05]" style="font-variation-settings: 'opsz' 96">
          Kalkulačka refinancování hypotéky
        </h1>
        <p class="mt-5 text-lg leading-relaxed text-petrol-100 max-w-[52ch]">
          Končí vám fixace a nová sazba je vyšší? Porovnejte, jestli se víc vyplatí splatit hypotéku
          v původním termínu, nebo prodloužit splatnost a ušetřený rozdíl ve splátce investovat.
        </p>
        <a
          href="#kalkulacka"
          class="mt-7 inline-flex items-center rounded-md bg-amber px-5 py-2.5 font-semibold text-petrol-900 hover:bg-[#edb459] transition-colors"
        >
          Spočítat refinancování
        </a>
      </div>

      <!-- Real output of the calculator for its default inputs (3.2M CZK, 30 years, 5-year fixation ends, 2.3 % -> 5.2 %, 6 % return).
           Regenerate the paths and numbers if the defaults in useCalculator.ts change. -->
      <figure class="hidden sm:block">
        <svg viewBox="0 0 530 300" class="w-full h-auto" fill="none" role="img" aria-labelledby="hero-graph-title">
          <title id="hero-graph-title">Graf: po konci fixace se splácení rozdělí na dvě varianty a u delší splatnosti roste investovaný rozdíl, až pokryje zbývající dluh</title>
          <g font-family="IBM Plex Sans, sans-serif" font-size="13">
            <!-- fixation period -->
            <rect x="56" y="30" width="63.400000000000006" height="232" fill="#ffffff" fill-opacity="0.05" />
            <g fill="#cfe5e8" fill-opacity="0.8" text-anchor="middle">
              <text x="88" y="236">fixace</text>
              <text x="88" y="252">2,3 %</text>
            </g>
            <text x="20" y="24" fill="#cfe5e8">zůstatek dluhu</text>
            <line x1="119.4" y1="30" x2="119.4" y2="262" stroke="#ffffff" stroke-opacity="0.45" stroke-dasharray="3 5" />
            <text x="125.4" y="24" fill="#cfe5e8">konec fixace</text>
            <text x="125.4" y="40" fill="#cfe5e8" fill-opacity="0.8">nová sazba 5,2 %</text>

            <!-- axes -->
            <line x1="56" y1="262" x2="512" y2="262" stroke="#ffffff" stroke-opacity="0.35" />
            <line x1="56" y1="44" x2="56" y2="262" stroke="#ffffff" stroke-opacity="0.35" />
            <g fill="#cfe5e8" fill-opacity="0.7" text-anchor="end">
              <text x="50" y="48">3,2 mil.</text>
              <text x="50" y="266">0 Kč</text>
            </g>
            <g fill="#cfe5e8" fill-opacity="0.7" text-anchor="middle">
              <text x="56" y="280">0</text>
              <text x="119.4" y="280">5</text>
              <text x="436.6" y="280">30</text>
              <text x="500.0" y="280">35</text>
              <text x="278" y="294">roky splácení</text>
            </g>

            <!-- balance before refinancing -->
            <path d="M56.0 44.0 L57.1 44.4 L62.3 46.5 L68.7 49.1 L75.0 51.7 L81.4 54.3 L87.7 57.0 L94.1 59.7 L100.4 62.4 L106.7 65.1 L113.1 67.9 L119.4 70.7" stroke="#cfe5e8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
            <!-- same term: higher payment, paid off sooner -->
            <path d="M119.4 70.7 L125.8 72.6 L132.1 74.6 L138.5 76.6 L144.8 78.6 L151.1 80.7 L157.5 82.9 L163.8 85.1 L170.2 87.3 L176.5 89.7 L182.9 92.0 L189.2 94.5 L195.5 97.0 L201.9 99.6 L208.2 102.2 L214.6 105.0 L220.9 107.8 L227.3 110.6 L233.6 113.6 L239.9 116.6 L246.3 119.7 L252.6 122.8 L259.0 126.1 L265.3 129.4 L271.7 132.9 L278.0 136.4 L284.3 140.0 L290.7 143.7 L297.0 147.5 L303.4 151.4 L309.7 155.5 L316.1 159.6 L322.4 163.8 L328.7 168.1 L335.1 172.6 L341.4 177.2 L347.8 181.8 L354.1 186.7 L360.5 191.6 L366.8 196.7 L373.1 201.9 L379.5 207.2 L385.8 212.7 L392.2 218.3 L398.5 224.1 L404.9 230.0 L411.2 236.1 L417.5 242.3 L423.9 248.7 L430.2 255.3 L435.5 260.9 L436.6 262.0" stroke="#f08a6e" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
            <!-- longer term: lower payment -->
            <path d="M119.4 70.7 L125.8 72.1 L132.1 73.5 L138.5 74.9 L144.8 76.3 L151.1 77.8 L157.5 79.4 L163.8 80.9 L170.2 82.5 L176.5 84.2 L182.9 85.9 L189.2 87.6 L195.5 89.4 L201.9 91.2 L208.2 93.1 L214.6 95.1 L220.9 97.0 L227.3 99.1 L233.6 101.2 L239.9 103.3 L246.3 105.5 L252.6 107.8 L259.0 110.1 L265.3 112.4 L271.7 114.9 L278.0 117.4 L284.3 120.0 L290.7 122.6 L297.0 125.3 L303.4 128.1 L309.7 130.9 L316.1 133.9 L322.4 136.9 L328.7 139.9 L335.1 143.1 L341.4 146.3 L347.8 149.7 L354.1 153.1 L360.5 156.6 L366.8 160.2 L373.1 163.9 L379.5 167.7 L385.8 171.6 L392.2 175.6 L398.5 179.7 L404.9 183.9 L411.2 188.2 L417.5 192.6 L423.9 197.2 L430.2 201.8 L436.6 206.6 L442.9 211.5 L449.3 216.6 L455.6 221.8 L461.9 227.1 L468.3 232.5 L474.6 238.1 L481.0 243.9 L487.3 249.7 L493.7 255.8 L498.9 261.0 L500.0 262.0" stroke="#6cc3cf" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
            <!-- the payment difference invested -->
            <path d="M119.4 262.0 L120.5 261.9 L125.8 261.4 L132.1 260.9 L138.5 260.3 L144.8 259.7 L151.1 259.1 L157.5 258.4 L163.8 257.8 L170.2 257.1 L176.5 256.4 L182.9 255.7 L189.2 254.9 L195.5 254.2 L201.9 253.4 L208.2 252.6 L214.6 251.7 L220.9 250.9 L227.3 250.0 L233.6 249.1 L239.9 248.1 L246.3 247.1 L252.6 246.1 L259.0 245.1 L265.3 244.0 L271.7 242.9 L278.0 241.8 L284.3 240.6 L290.7 239.4 L297.0 238.2 L303.4 236.9 L309.7 235.6 L316.1 234.3 L322.4 232.9 L328.7 231.4 L335.1 230.0 L341.4 228.4 L347.8 226.9 L354.1 225.2 L360.5 223.6 L366.8 221.9 L373.1 220.1 L379.5 218.3 L385.8 216.4 L392.2 214.4 L398.5 212.5 L404.9 210.4 L411.2 208.3 L417.5 206.1 L423.9 203.8 L430.2 201.5 L436.6 199.1 L442.9 196.7 L449.3 194.1 L455.6 191.5 L461.9 188.8 L468.3 186.1 L474.6 183.2 L481.0 180.3 L487.3 177.2 L493.7 174.1 L500.0 170.9" stroke="#e3a23b" stroke-width="3" stroke-dasharray="7 6" stroke-linecap="round" />

            <!-- direct labels -->
            <text x="300" y="186" fill="#f08a6e" text-anchor="end">30 let</text>
            <text x="300" y="120" fill="#6cc3cf">35 let</text>
            <text x="196" y="236" fill="#e3a23b">investice</text>

            <!-- investments catch up with the remaining debt -->
            <line x1="433.2" y1="194.5" x2="455.2" y2="114" stroke="#e3a23b" stroke-width="1.5" />
            <rect x="424.2" y="195.5" width="12" height="12" transform="rotate(45 430.2 201.5)" fill="#e3a23b" stroke="#0a3540" stroke-width="2" />
            <text x="447.2" y="86" fill="#ffffff" font-weight="600">
              <tspan x="447.2">investice</tspan>
              <tspan x="447.2" dy="16">pokryjí dluh</tspan>
            </text>
          </g>
        </svg>
        <figcaption class="mt-4 text-sm text-petrol-100">
          <ul class="flex flex-col gap-1.5">
            <li class="flex items-center gap-2">
              <span class="h-[3px] w-5 shrink-0 rounded bg-[#f08a6e]" aria-hidden="true"></span>
              Stejná splatnost 30 let: splátka 16&nbsp;741&nbsp;Kč
            </li>
            <li class="flex items-center gap-2">
              <span class="h-[3px] w-5 shrink-0 rounded bg-[#6cc3cf]" aria-hidden="true"></span>
              Prodloužení na 35 let: splátka 15&nbsp;416&nbsp;Kč
            </li>
            <li class="flex items-center gap-2">
              <span class="w-5 shrink-0 border-t-[3px] border-dashed border-amber" aria-hidden="true"></span>
              Rozdíl 1&nbsp;325&nbsp;Kč měsíčně investujete s výnosem 6 % ročně
            </li>
          </ul>
          <p class="mt-3 text-petrol-100/70">
            Příklad: hypotéka 3,2&nbsp;mil.&nbsp;Kč na 30 let sjednaná v roce 2021 s pětiletou fixací za 2,3&nbsp;%.
            Původní splátka byla 12&nbsp;314&nbsp;Kč. Investice pokryjí zbývající dluh po 29,5 letech.
          </p>
        </figcaption>
      </figure>
    </div>
  </header>
</template>
