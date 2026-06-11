import React from 'react'
import { cn } from '../../utils'

interface SpinnerProps { size?: 'sm' | 'md' | 'lg'; className?: string }
const SIZES = { sm: 'h-4 w-4', md: 'h-6 w-6', lg: 'h-10 w-10' }

export const Spinner: React.FC<SpinnerProps> = ({ size = 'md', className }) => (
  <div
    role="status" aria-label="Loading"
    className={cn('animate-spin rounded-full border-2 border-blue-200 border-t-blue-600', SIZES[size], className)}
  />
)
