import React from 'react'
import { cn } from '../../utils'

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline'
export type ButtonSize = 'sm' | 'md' | 'lg'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
  isLoading?: boolean
  fullWidth?: boolean
}

const VARIANTS: Record<ButtonVariant, string> = {
  primary:   'bg-blue-600 text-white hover:bg-blue-700 active:scale-95 disabled:opacity-50',
  secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 active:bg-gray-300 disabled:opacity-50',
  ghost:     'bg-transparent text-gray-700 hover:bg-gray-100 disabled:opacity-50',
  danger:    'bg-red-600 text-white hover:bg-red-700 active:scale-95 disabled:opacity-50',
  outline:   'border-2 border-blue-600 text-blue-600 hover:bg-blue-50 active:scale-95 disabled:opacity-50',
}
const SIZES: Record<ButtonSize, string> = {
  sm: 'px-3 py-1.5 text-sm font-medium rounded-md',
  md: 'px-4 py-2.5 text-base font-semibold rounded-lg',
  lg: 'px-6 py-3 text-lg font-semibold rounded-xl',
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary', size = 'md', isLoading = false,
  fullWidth = false, disabled, children, className, ...props
}) => (
  <button
    disabled={disabled || isLoading}
    className={cn(
      'transition-all duration-200 disabled:cursor-not-allowed select-none',
      VARIANTS[variant], SIZES[size], fullWidth && 'w-full', className,
    )}
    {...props}
  >
    {isLoading ? (
      <span className="flex items-center justify-center gap-2">
        <span className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
        Loading…
      </span>
    ) : children}
  </button>
)
