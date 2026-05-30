/**
 * Button Component
 * Reusable button with multiple variants and states
 * Professional design with smooth transitions
 */

import React from 'react'

export type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost' | 'outline'
export type ButtonSize = 'sm' | 'md' | 'lg'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
  isLoading?: boolean
  fullWidth?: boolean
  children: React.ReactNode
}

const variantStyles: Record<ButtonVariant, string> = {
  primary: 'gradient-primary text-white hover:shadow-lg-custom active:scale-95 disabled:opacity-60',
  secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 active:bg-gray-300 disabled:opacity-60',
  danger: 'bg-red-600 text-white hover:bg-red-700 active:scale-95 disabled:opacity-60',
  ghost: 'bg-transparent text-gray-700 hover:bg-gray-100 active:bg-gray-200 disabled:opacity-60',
  outline: 'border-2 border-primary text-primary hover:bg-blue-50 active:scale-95 disabled:opacity-60',
}

const sizeStyles: Record<ButtonSize, string> = {
  sm: 'px-3 py-1.5 text-sm font-medium',
  md: 'px-4 py-2.5 text-base font-semibold',
  lg: 'px-6 py-3 text-lg font-semibold',
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  fullWidth = false,
  disabled = false,
  children,
  className = '',
  ...props
}) => {
  return (
    <button
      disabled={disabled || isLoading}
      className={`
        rounded-lg font-semibold transition-all duration-200
        disabled:cursor-not-allowed
        ${variantStyles[variant]}
        ${sizeStyles[size]}
        ${fullWidth ? 'w-full' : ''}
        ${className}
      `}
      {...props}
    >
      {isLoading ? (
        <span className="flex items-center justify-center gap-2">
          <div className="animate-spin rounded-full h-4 w-4 border-2 border-current border-t-transparent" />
          <span>Loading...</span>
        </span>
      ) : (
        children
      )}
    </button>
  )
}
