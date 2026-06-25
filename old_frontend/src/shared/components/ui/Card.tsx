import React from 'react'
import { cn } from '../../utils'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'glass' | 'flat'
  padding?: 'none' | 'sm' | 'md' | 'lg'
}
const VARIANTS = {
  default:  'bg-white border border-gray-200 rounded-2xl',
  elevated: 'bg-white rounded-2xl shadow-md',
  glass:    'bg-white/80 backdrop-blur-sm border border-white/60 rounded-2xl shadow-sm',
  flat:     'bg-gray-50 rounded-2xl',
}
const PADDING = { none: '', sm: 'p-3', md: 'p-5', lg: 'p-6' }

export const Card: React.FC<CardProps> = ({
  variant = 'default', padding = 'md', children, className, ...props
}) => (
  <div className={cn(VARIANTS[variant], PADDING[padding], className)} {...props}>
    {children}
  </div>
)
