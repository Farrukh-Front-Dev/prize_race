import React from 'react'
import { cn } from '../../utils'
import { EventStatus } from '../../types'

export type BadgeVariant = 'default' | 'success' | 'warning' | 'danger' | 'info' | 'primary'

interface BadgeProps {
  variant?: BadgeVariant
  size?: 'sm' | 'md'
  children: React.ReactNode
  className?: string
}
const VARIANTS: Record<BadgeVariant, string> = {
  default: 'bg-gray-100 text-gray-700',
  success: 'bg-green-100 text-green-800',
  warning: 'bg-yellow-100 text-yellow-800',
  danger:  'bg-red-100 text-red-800',
  info:    'bg-blue-100 text-blue-800',
  primary: 'bg-blue-600 text-white',
}
const SIZES = { sm: 'px-2 py-0.5 text-xs', md: 'px-3 py-1 text-sm' }

export const Badge: React.FC<BadgeProps> = ({
  variant = 'default', size = 'sm', children, className,
}) => (
  <span className={cn('inline-flex items-center font-semibold rounded-full', VARIANTS[variant], SIZES[size], className)}>
    {children}
  </span>
)

export const statusVariant = (status: EventStatus): BadgeVariant => {
  const map: Record<EventStatus, BadgeVariant> = {
    DRAFT: 'default', PENDING_PAYMENT: 'warning', ACTIVE: 'success', FINISHED: 'info',
  }
  return map[status] ?? 'default'
}
