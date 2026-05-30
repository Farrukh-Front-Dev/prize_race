/**
 * ErrorBoundary Component
 * Catches errors and displays fallback UI
 */

import React, { ReactNode } from 'react'
import { Card } from '../common'

interface ErrorBoundaryProps {
  children: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error) {
    console.error('Error caught by boundary:', error)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <Card className="max-w-md">
            <h1 className="text-2xl font-bold text-red-600 mb-2">Something went wrong</h1>
            <p className="text-gray-700 mb-4">{this.state.error?.message}</p>
            <button
              onClick={() => window.location.reload()}
              className="w-full bg-primary text-white py-2 rounded-lg font-semibold hover:bg-blue-700"
            >
              Reload Page
            </button>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}
