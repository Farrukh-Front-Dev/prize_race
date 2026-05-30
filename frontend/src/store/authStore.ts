/**
 * Auth Store
 * Manages user authentication state with Zustand
 */

import { create } from 'zustand'
import { User, TelegramUser } from '../types'
import { apiService } from '../services/api'

interface AuthState {
  user: User | null
  telegramUser: TelegramUser | null
  isLoading: boolean
  error: string | null
  isDevelopment: boolean

  // Actions
  initTelegram: (initData: string) => Promise<void>
  logout: () => void
  updateUser: (data: Partial<User>) => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  telegramUser: null,
  isLoading: false,
  error: null,
  isDevelopment: false,

  initTelegram: async (initData: string) => {
    set({ isLoading: true, error: null })
    try {
      // Parse init data
      const params = new URLSearchParams(initData)
      const userStr = params.get('user')
      if (!userStr) throw new Error('No user data')

      const telegramUser = JSON.parse(decodeURIComponent(userStr)) as TelegramUser
      apiService.setInitData(initData)

      // Check if mock data (development mode)
      const isMockData = params.get('hash') === 'mock_hash_for_development'

      if (isMockData) {
        // Development mode - create mock user without backend call
        const mockUser: User = {
          id: telegramUser.id,
          telegram_id: String(telegramUser.id),
          username: telegramUser.username,
          first_name: telegramUser.first_name,
          last_name: telegramUser.last_name,
          wallet_address: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }
        set({ user: mockUser, telegramUser, isLoading: false, isDevelopment: true })
        console.log('✅ Development mode - Mock user loaded')
      } else {
        // Production mode - call backend
        const user = await apiService.registerUser(
          String(telegramUser.id),
          telegramUser.username
        )
        set({ user, telegramUser, isLoading: false, isDevelopment: false })
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Auth failed'
      set({ error: message, isLoading: false })
      throw error
    }
  },

  logout: () => {
    set({ user: null, telegramUser: null })
  },

  updateUser: async (data: Partial<User>) => {
    set({ isLoading: true })
    try {
      const state = useAuthStore.getState()
      if (!state.user) throw new Error('No user')

      const updated = await apiService.updateUser(state.user.telegram_id, data)
      set({ user: updated, isLoading: false })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Update failed'
      set({ error: message, isLoading: false })
      throw error
    }
  },
}))
