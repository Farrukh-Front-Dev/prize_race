/**
 * Card Component
 * Reusable card container with glass effect and modern design
 */

import React from 'react'

interface CardProps {
  children: React.ReactNode
  className?: string
  header?: React.ReactNode
  footer?: React.ReactNode
  variant?: 'default' | 'elevated' | 'glass'
  hover?: boolean
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  header,
  footer,
  variant = 'default',
  hover = false,
}) => {
  const variantStyles = {
    default: 'bg-white border border-gray-200 shadow-md',
    elevated: 'bg-white shadow-lg-custom border border-gray-100',
    glass: 'glass-effect',
  }

  const hoverClass = hover ? 'hover:shadow-xl-custom transition-shadow duration-300' : ''

  return (
    <div className={`rounded-xl ${variantStyles[variant]} ${hoverClass} ${className}`}>
      {header && (
        <div className="border-b border-gray-200 px-4 py-4 sm:px-6">
          <div className="font-semibold text-gray-900">{header}</div>
        </div>
      )}
      <div className="p-4 sm:p-6">
        {children}
      </div>
      {footer && (
        <div className="border-t border-gray-200 px-4 py-4 sm:px-6 bg-gray-50 rounded-b-xl">
          {footer}
        </div>
      )}
    </div>
  )
}
