/**
 * Container Component
 * Responsive content container
 */

import React from 'react'

interface ContainerProps {
  children: React.ReactNode
  className?: string
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl'
}

const maxWidthStyles = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
}

export const Container: React.FC<ContainerProps> = ({
  children,
  className = '',
  maxWidth = 'md',
}) => {
  return (
    <div className={`mx-auto px-4 ${maxWidthStyles[maxWidth]} ${className}`}>
      {children}
    </div>
  )
}
