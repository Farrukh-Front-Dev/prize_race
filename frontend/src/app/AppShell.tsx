/**
 * app/AppShell.tsx
 * ─────────────────
 * Handles Telegram init flow and renders the router once ready.
 *
 * Flow:
 *   1. useTelegram() waits for WebApp SDK (or creates mock)
 *   2. Once ready → calls initTelegram(initData, isMock)
 *   3. initTelegram registers/fetches user from backend
 *   4. Once user is set → render AppRouter
 *
 * The "Open in Telegram" screen is NEVER shown in dev mode because
 * useTelegram always resolves (with mock data in a browser).
 */
import React, { useEffect, useRef } from 'react'
import { useTelegram }  from '../shared/hooks/useTelegram'
import { useAuthStore } from '../features/auth'
import { Spinner }      from '../shared/components/ui'
import { AppRouter }    from './router'

export const AppShell: React.FC = () => {
  const { isReady, initData, isMock } = useTelegram()
  const { initTelegram, isLoading, error, user } = useAuthStore()
  const initCalled = useRef(false)

  // Call initTelegram exactly once when the hook reports ready
  useEffect(() => {
    if (isReady && initData && !initCalled.current) {
      initCalled.current = true
      initTelegram(initData, isMock)
    }
  }, [isReady, initData, isMock, initTelegram])

  // ── Still loading ───────────────────────────────────────────────────────
  if (!isReady || isLoading || (!user && !error)) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="flex flex-col items-center gap-3">
          <Spinner size="lg" />
          <p className="text-sm text-gray-500">Starting PrizeRace…</p>
        </div>
      </div>
    )
  }

  // ── Auth error ──────────────────────────────────────────────────────────
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen p-4 bg-red-50">
        <div className="bg-white rounded-2xl shadow-lg p-6 max-w-sm w-full text-center">
          <p className="text-3xl mb-3">⚠️</p>
          <h1 className="text-lg font-bold text-gray-900 mb-2">Unable to start</h1>
          <p className="text-sm text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="w-full bg-blue-600 text-white py-2.5 rounded-xl font-semibold"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  // ── Authenticated — render the app ──────────────────────────────────────
  return <AppRouter />
}
