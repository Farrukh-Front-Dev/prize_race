import React from 'react'

interface HeaderProps {
  title: string
  subtitle?: string
  action?: React.ReactNode
  onBack?: () => void
}
export const Header: React.FC<HeaderProps> = ({ title, subtitle, action, onBack }) => (
  <header className="bg-blue-600 text-white px-4 py-4 flex items-center gap-3 shadow-md">
    {onBack && (
      <button onClick={onBack} aria-label="Go back"
        className="p-1 -ml-1 rounded-lg hover:bg-blue-700 active:bg-blue-800 transition-colors">
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
    )}
    <div className="flex-1 min-w-0">
      <h1 className="text-lg font-bold truncate leading-tight">{title}</h1>
      {subtitle && <p className="text-blue-100 text-xs truncate mt-0.5">{subtitle}</p>}
    </div>
    {action && <div className="flex-shrink-0">{action}</div>}
  </header>
)
