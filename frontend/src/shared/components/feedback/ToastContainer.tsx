import React, { useEffect } from 'react'
import { cn } from '../../utils'
import { useToastStore } from '../../../features/notifications/store'
import { ToastType } from '../../types'
import { TOAST_DURATION_MS } from '../../constants'

const TYPE_STYLES: Record<ToastType, string> = {
  success: 'bg-emerald-600 text-white',
  error:   'bg-red-600 text-white',
  warning: 'bg-amber-500 text-white',
  info:    'bg-blue-600 text-white',
}
const TYPE_ICON: Record<ToastType, string> = {
  success: '✓', error: '✕', warning: '⚠', info: 'ℹ',
}

const ToastItem: React.FC<{ id: string; message: string; type: ToastType }> = ({ id, message, type }) => {
  const dismiss = useToastStore((s) => s.dismiss)
  useEffect(() => {
    const t = setTimeout(() => dismiss(id), TOAST_DURATION_MS)
    return () => clearTimeout(t)
  }, [id, dismiss])
  return (
    <div role="alert"
      className={cn('flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg animate-slide-up text-sm font-medium max-w-sm w-full', TYPE_STYLES[type])}>
      <span className="text-base font-bold flex-shrink-0">{TYPE_ICON[type]}</span>
      <span className="flex-1 leading-snug">{message}</span>
      <button onClick={() => dismiss(id)} aria-label="Dismiss"
        className="flex-shrink-0 opacity-70 hover:opacity-100 transition-opacity">✕</button>
    </div>
  )
}

export const ToastContainer: React.FC = () => {
  const toasts = useToastStore((s) => s.toasts)
  if (!toasts.length) return null
  return (
    <div aria-live="polite"
      className="fixed bottom-4 left-4 right-4 sm:left-auto sm:right-4 sm:w-auto z-50 flex flex-col gap-2 items-end">
      {toasts.map((t) => <ToastItem key={t.id} id={t.id} message={t.message} type={t.type} />)}
    </div>
  )
}
