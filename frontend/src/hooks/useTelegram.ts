/**
 * useTelegram Hook
 * Initialize and manage Telegram Mini App
 */

import { useEffect, useState } from 'react'
import { useAuthStore } from '../store/authStore'

declare global {
  interface Window {
    Telegram?: {
      WebApp: {
        initData: string
        initDataUnsafe: Record<string, any>
        ready: () => void
        expand: () => void
        close: () => void
        setHeaderColor: (color: string) => void
        setBackgroundColor: (color: string) => void
      }
    }
  }
}

// Mock data for development
const getMockInitData = () => {
  const mockUser = {
    id: 123456789,
    is_bot: false,
    first_name: 'Test',
    last_name: 'User',
    username: 'testuser',
    language_code: 'en',
    is_premium: false,
  }

  const authDate = Math.floor(Date.now() / 1000)
  const params = new URLSearchParams({
    user: JSON.stringify(mockUser),
    auth_date: String(authDate),
    hash: 'mock_hash_for_development',
  })

  return params.toString()
}

export const useTelegram = () => {
  const [isReady, setIsReady] = useState(false)
  const initTelegram = useAuthStore((state) => state.initTelegram)

  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Check if Telegram WebApp is available
        if (window.Telegram?.WebApp) {
          const webApp = window.Telegram.WebApp

          // Initialize Telegram
          webApp.ready()
          webApp.expand()

          // Set theme colors
          webApp.setHeaderColor('#0088cc')
          webApp.setBackgroundColor('#ffffff')

          // Initialize auth with init data
          if (webApp.initData) {
            await initTelegram(webApp.initData)
          }
        } else {
          // Development mode - use mock data
          console.warn('⚠️ Telegram WebApp not available - using mock data for development')
          const mockData = getMockInitData()
          await initTelegram(mockData)
        }

        setIsReady(true)
      } catch (error) {
        console.error('Failed to initialize Telegram:', error)
        setIsReady(true)
      }
    }

    initializeApp()
  }, [initTelegram])

  return { isReady }
}
