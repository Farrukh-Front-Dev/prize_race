/**
 * App Component
 * Main application entry point
 */

import React from 'react'
import { useTelegram } from './hooks/useTelegram'
import { useAuthStore } from './store/authStore'
import { HomePage } from './pages'
import { ErrorBoundary, Spinner } from './components'
import './App.css'

function AppContent() {
  const user = useAuthStore((state) => state.user)
  const isLoading = useAuthStore((state) => state.isLoading)
  const error = useAuthStore((state) => state.error)

  if (error) {
    return (
      <div className="min-h-screen bg-red-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-6 max-w-md">
          <h1 className="text-2xl font-bold text-red-600 mb-2">Error</h1>
          <p className="text-gray-700 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="w-full bg-primary text-white py-2 rounded-lg font-semibold hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Spinner size="lg" />
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-6 max-w-md text-center">
          <h1 className="text-2xl font-bold mb-2">Welcome to PrizeRace</h1>
          <p className="text-gray-600 mb-4">
            Open this app in Telegram to get started
          </p>
        </div>
      </div>
    )
  }

  return <HomePage />
}

function App() {
  const { isReady } = useTelegram()

  if (!isReady) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <ErrorBoundary>
      <AppContent />
    </ErrorBoundary>
  )
}

export default App
