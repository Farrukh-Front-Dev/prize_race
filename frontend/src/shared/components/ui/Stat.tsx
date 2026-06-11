import React from 'react'
import { cn } from '../../utils'

interface StatProps {
  label: string
  value: React.ReactNode
  icon?: string
  className?: string
}
export const Stat: React.FC<StatProps> = ({ label, value, icon, className }) => (
  <div className={cn('flex flex-col gap-0.5', className)}>
    <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
      {icon && <span className="mr-1">{icon}</span>}{label}
    </p>
    <p className="text-base font-bold text-gray-900 truncate">{value}</p>
  </div>
)
