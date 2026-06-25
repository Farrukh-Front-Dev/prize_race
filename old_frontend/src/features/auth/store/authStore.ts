/**
 * features/auth/store/authStore.ts
 * ──────────────────────────────────
 * Auth state — handles Telegram init (real + mock browser mode).
 */
import { create } from 'zustand'
import { User, TelegramUser } from '../../../shared/types'
import { setInitData } from '../../../shared/api'
import { authApi } from '../api/authApi'

interface AuthState {
  user: User | null
  telegramUser: TelegramUser | null
  isLoading: boolean
  error: string | null
  isMockMode: boolean
  initTelegram: (initData: string, isMock: boolean) => Promise<void>
  clearError: () => void
  setUser: (user: User) => void
}

/**
 * Safely parse the "user" field from initData.
 * URLSearchParams.get() automatically URL-decodes the value.
 */
function parseUserFromInitData(initData: string): TelegramUser {
  const params = new URLSearchParams(initData)
  const userStr = params.get('user')
  if (!userStr) throw new Error('No user data in initData')
  return JSON.parse(userStr) as TelegramUser
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  telegramUser: null,
  isLoading: false,
  error: null,
  isMockMode: false,

  initTelegram: async (initData: string, isMock: boolean) => {
    set({ isLoading: true, error: null, isMockMode: isMock })

    // Store initData in axios client so every request carries the header
    setInitData(initData)

    try {
      const telegramUser = parseUserFromInitData(initData)
      set({ telegramUser })

      // Call backend register in both real and mock modes
      const user = await authApi.register({
        telegram_id: String(telegramUser.id),
        username:    telegramUser.username,
        first_name:  telegramUser.first_name,
        last_name:   telegramUser.last_name,
      })
      set({ user, isLoading: false })

      if (isMock) {
        console.info('[Auth] Mock user registered id=%d (browser dev mode)', telegramUser.id)
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Auth failed'
      console.error('[Auth] initTelegram error:', err)
      set({ error: msg, isLoading: false })
    }
  },

  clearError: () => set({ error: null }),
  setUser: (user) => set({ user }),
}))
