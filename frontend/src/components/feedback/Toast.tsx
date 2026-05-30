/**
 * Toast Component
 * Modern notification with smooth animations
 */

import React, { useEffect } from 'react'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

interface ToastProps {
  message: string
  type?: ToastType
  duration?: number
  onClose?: () => void
}

const typeStyles: Record<ToastType, string> = {
  success: 'bg-gradient-to-r from-emerald-500 to-emerald-600 text-white shadow-lg',
  error: 'bg-gradient-to-r from-red-500 to-red-600 text-white shadow-lg',
  warning: 'bg-gradient-to-r from-amber-500 to-amber-600 text-white shadow-lg',
  info: 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg',
}

const typeIcons: Record<ToastType, string> = {
  success: '✓',
  error: '✕',
  warning: '⚠',
  info: 'ℹ',
}

export const Toast: React.FC<ToastProps> = ({
  message,
  type = 'info',
  duration = 3000,
  onClose,
}) => {
  useEffect(() => {
    if (duration > 0 && onClose) {
      const timer = setTimeout(onClose, duration)
      return () => clearTimeout(timer)
    }
  }, [duration, onClose])

  return (
    <div
      className={`fixed bottom-4 left-4 right-4 sm:left-auto sm:right-4 sm:max-w-sm px-4 py-3 rounded-lg ${typeStyles[type]} animate-slide-in flex items-center gap-3`}
      role="alert"
    >
      <span className="text-lg font-bold flex-shrink-0">{typeIcons[type]}</span>
      <p className="text-sm font-medium flex-1">{message}</p>
    </div>
  )
}
