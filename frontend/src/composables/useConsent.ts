import { ref } from 'vue'

// Stored choice; the inline script in index.html reads the same key before the Google tag loads.
const STORAGE_KEY = 'cookie-consent'
const MAX_AGE_MS = 365 * 24 * 60 * 60 * 1000

interface StoredConsent {
  analytics: boolean
  ts: number
}

declare global {
  interface Window {
    dataLayer: unknown[]
    gtag?: (...args: unknown[]) => void
  }
}

function readStored(): StoredConsent | null {
  try {
    const c = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null') as StoredConsent | null
    if (c && typeof c.analytics === 'boolean' && Date.now() - c.ts < MAX_AGE_MS) return c
  } catch {
    // storage blocked or corrupted: treat as no choice
  }
  return null
}

function gtag(...args: unknown[]) {
  if (typeof window.gtag === 'function') window.gtag(...args)
  else (window.dataLayer = window.dataLayer || []).push(args)
}

function deleteAnalyticsCookies() {
  const host = location.hostname
  const domains = ['', host, '.' + host, '.' + host.split('.').slice(-2).join('.')]
  for (const cookie of document.cookie.split(';')) {
    const name = cookie.split('=')[0].trim()
    if (!name.startsWith('_ga')) continue
    for (const d of domains) {
      document.cookie = `${name}=; Max-Age=0; path=/${d ? '; domain=' + d : ''}`
    }
  }
}

// Module-level state so the banner and the footer link share it.
const bannerOpen = ref(readStored() === null)

export function useConsent() {
  const choose = (analytics: boolean) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ analytics, ts: Date.now() }))
    } catch {
      // without storage the banner will simply ask again next visit
    }
    gtag('consent', 'update', { analytics_storage: analytics ? 'granted' : 'denied' })
    if (!analytics) deleteAnalyticsCookies()
    bannerOpen.value = false
  }

  return {
    bannerOpen,
    accept: () => choose(true),
    reject: () => choose(false),
    openSettings: () => { bannerOpen.value = true },
  }
}
