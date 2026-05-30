/**
 * Header Component
 * Modern app header with gradient and professional design
 */

import React from 'react'

interface HeaderProps {
  title: string
  subtitle?: string
  action?: React.ReactNode
  variant?: 'default' | 'gradient'
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  action,
  variant = 'gradient',
}) => {
  const variantStyles = {
    default: 'bg-primary text-white',
    gradient: 'gradient-primary text-white',
  }

  return (
    <header className={`${variantStyles[variant]} p-4 sm:p-6 sticky top-0 z-10 shadow-lg-custom`}>
      <div className="flex justify-between items-start gap-4">
        <div className="flex-1">
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">{title}</h1>
          {subtitle && (
            <p className="text-sm sm:text-base opacity-90 mt-1">{subtitle}</p>
          )}
        </div>
        {action && <div className="flex-shrink-0">{action}</div>}
      </div>
    </header>
  )
}

