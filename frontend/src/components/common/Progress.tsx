/**
 * Progress Component
 * Modern progress bar with smooth animation
 */

import React from 'react'

interface ProgressProps {
  value: number
  max?: number
  variant?: 'primary' | 'success' | 'warning' | 'danger'
  showLabel?: boolean
  animated?: boolean
  className?: string
}

const variantStyles = {
  primary: 'bg-gradient-to-r from-blue-500 to-blue-600',
  success: 'bg-gradient-to-r from-emerald-500 to-emerald-600',
  warning: 'bg-gradient-to-r from-amber-500 to-amber-600',
  danger: 'bg-gradient-to-r from-red-500 to-red-600',
}

export const Progress: React.FC<ProgressProps> = ({
  value,
  max = 100,
  variant = 'primary',
  showLabel = false,
  animated = true,
  className = '',
}) => {
  const percentage = Math.min((value / max) * 100, 100)

  return (
    <div className={className}>
      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden shadow-sm">
        <div
          className={`h-full rounded-full transition-all duration-500 ${variantStyles[variant]} ${
            animated ? 'animate-pulse-glow' : ''
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <p className="text-xs text-gray-600 mt-1 font-medium">{Math.round(percentage)}%</p>
      )}
    </div>
  )
}
