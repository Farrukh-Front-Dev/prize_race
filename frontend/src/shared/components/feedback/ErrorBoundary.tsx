import { Component, ErrorInfo, ReactNode } from 'react'

interface Props { children: ReactNode }
interface State { error: Error | null }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null }
  static getDerivedStateFromError(error: Error): State { return { error } }
  componentDidCatch(error: Error, info: ErrorInfo) { console.error('[ErrorBoundary]', error, info) }
  render() {
    if (this.state.error) return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-red-50">
        <div className="bg-white rounded-2xl shadow-lg p-6 max-w-sm w-full text-center">
          <p className="text-3xl mb-3">💥</p>
          <h2 className="text-lg font-bold text-gray-900 mb-2">Something went wrong</h2>
          <p className="text-sm text-gray-600 mb-4 break-words">{this.state.error.message}</p>
          <button onClick={() => this.setState({ error: null })}
            className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-semibold hover:bg-blue-700">
            Try again
          </button>
        </div>
      </div>
    )
    return this.props.children
  }
}
