import React from 'react'
import { cn } from '../../utils'

interface ProgressProps {
  value: number
  variant?: 'primary' | 'success' | 'warning'
  className?: string
  showLabel?: boolean
}
const TRACK = { primary: 'bg-blue-600', success: 'bg-green-500', warning: 'bg-yellow-500' }

export const Progress: React.FC<ProgressProps> = ({
  value, variant = 'primary', className, showLabel = false,
}) => {
  const clamped = Math.min(100, Math.max(0, value))
  return (
    <div className={cn('w-full', className)}>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          role="progressbar" aria-valuenow={clamped} aria-valuemin={0} aria-valuemax={100}
          style={{ width: `${clamped}%` }}
          className={cn('h-full rounded-full transition-all duration-500', TRACK[variant])}
        />
      </div>
      {showLabel && <p className="mt-1 text-xs text-gray-500 text-right">{clamped.toFixed(0)}%</p>}
    </div>
  )
}
