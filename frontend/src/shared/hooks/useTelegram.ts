import { useEffect, useState } from 'react'

declare global {
  interface Window {
    Telegram?: {
      WebApp: {
        initData: string
        initDataUnsafe: { user?: { id: number; first_name: string; last_name?: string; username?: string; language_code?: string; is_premium?: boolean } }
        ready: () => void
        expand: () => void
        close: () => void
        setHeaderColor: (color: string) => void
        setBackgroundColor: (color: string) => void
        showAlert: (msg: string, cb?: () => void) => void
        version: string
        platform: string
        colorScheme: 'light' | 'dark'
        isExpanded: boolean
      }
    }
  }
}

export interface TelegramState {
  isReady: boolean
  initData: string
  isMock: boolean
}

function buildMockInitData(): string {
  const user = { id: 100000001, is_bot: false, first_name: 'Dev', last_name: 'User', username: 'devuser', language_code: 'en', is_premium: false }
  return new URLSearchParams({
    user: JSON.stringify(user),
    auth_date: String(Math.floor(Date.now() / 1000)),
    hash: 'mock_hash_for_development',
  }).toString()
}

export function useTelegram(): TelegramState {
  const [state, setState] = useState<TelegramState>({ isReady: false, initData: '', isMock: false })

  useEffect(() => {
    const tg = window.Telegram?.WebApp
    // Real Telegram: WebApp object exists AND initData is non-empty
    const isRealTelegram = !!(tg && tg.initData && tg.initData.length > 0)

    if (isRealTelegram) {
      tg!.ready()
      tg!.expand()
      try { tg!.setHeaderColor('#0088cc'); tg!.setBackgroundColor('#f8fafc') } catch {}
      setState({ isReady: true, initData: tg!.initData, isMock: false })
    } else {
      // Browser mode — telegram-web-app.js may be loaded but initData is empty
      console.info('[useTelegram] Browser mode — using mock initData (backend DEBUG=true required)')
      setState({ isReady: true, initData: buildMockInitData(), isMock: true })
    }
  }, [])

  return state
}
