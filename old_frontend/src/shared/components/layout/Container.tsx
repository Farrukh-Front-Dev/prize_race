import React from 'react'
import { cn } from '../../utils'

interface ContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  maxWidth?: 'sm' | 'md' | 'lg'
}
const MAX = { sm: 'max-w-sm', md: 'max-w-2xl', lg: 'max-w-4xl' }

export const Container: React.FC<ContainerProps> = ({
  maxWidth = 'md', className, children, ...props
}) => (
  <div className={cn('mx-auto px-4 w-full', MAX[maxWidth], className)} {...props}>
    {children}
  </div>
)
