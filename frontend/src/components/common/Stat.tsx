/**
 * Stat Component
 * Display statistics with icon and label
 */

import React from 'react'

interface StatProps {
  label: string
  value: string | number
  icon?: React.ReactNode
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  className?: string
}

export const Stat: React.FC<StatProps> = ({
  label,
  value,
  icon,
  trend,
  trendValue,
  className = '',
}) => {
  const trendColor = {
    up: 'text-emerald-600',
    down: 'text-red-600',
    neutral: 'text-gray-600',
  }

  return (
    <div className={`flex items-start gap-3 ${className}`}>
      {icon && (
        <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center text-primary">
          {icon}
        </div>
      )}
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-600 font-medium">{label}</p>
        <div className="flex items-baseline gap-2 mt-1">
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {trend && trendValue && (
            <span className={`text-xs font-semibold ${trendColor[trend]}`}>
              {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'} {trendValue}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
