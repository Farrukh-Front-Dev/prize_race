/**
 * Spinner Component
 * Modern loading indicator with smooth animation
 */

import React from 'react'

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
  variant?: 'default' | 'primary'
}

const sizeStyles = {
  sm: 'h-4 w-4',
  md: 'h-8 w-8',
  lg: 'h-12 w-12',
}

const variantStyles = {
  default: 'border-gray-300 border-t-gray-900',
  primary: 'border-blue-200 border-t-primary',
}

export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  className = '',
  variant = 'primary',
}) => {
  return (
    <div className={`animate-spin rounded-full border-2 ${sizeStyles[size]} ${variantStyles[variant]} ${className}`} />
  )
}
