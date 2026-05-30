/**
 * Badge Component
 * Reusable badge for status indicators with modern design
 */

import React from 'react'

export type BadgeVariant = 'success' | 'error' | 'warning' | 'info' | 'default' | 'primary'

interface BadgeProps {
  children: React.ReactNode
  variant?: BadgeVariant
  className?: string
  size?: 'sm' | 'md'
}

const variantStyles: Record<BadgeVariant, string> = {
  success: 'bg-emerald-100 text-emerald-800 border border-emerald-200',
  error: 'bg-red-100 text-red-800 border border-red-200',
  warning: 'bg-amber-100 text-amber-800 border border-amber-200',
  info: 'bg-blue-100 text-blue-800 border border-blue-200',
  primary: 'bg-blue-100 text-blue-800 border border-blue-200',
  default: 'bg-gray-100 text-gray-800 border border-gray-200',
}

const sizeStyles = {
  sm: 'px-2 py-1 text-xs',
  md: 'px-3 py-1.5 text-sm',
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  className = '',
  size = 'md',
}) => {
  return (
    <span className={`inline-flex items-center rounded-full font-semibold ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}>
      {children}
    </span>
  )
}
