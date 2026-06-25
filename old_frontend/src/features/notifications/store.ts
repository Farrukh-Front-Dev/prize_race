import { create } from 'zustand'
import { ToastItem, ToastType } from '../../shared/types'

interface ToastState {
  toasts: ToastItem[]
  push: (message: string, type?: ToastType) => void
  dismiss: (id: string) => void
}
let _seq = 0
export const useToastStore = create<ToastState>((set) => ({
  toasts: [],
  push: (message, type = 'info') => {
    const id = String(++_seq)
    set((s) => ({ toasts: [...s.toasts, { id, message, type }] }))
  },
  dismiss: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}))

export const toast = {
  success: (msg: string) => useToastStore.getState().push(msg, 'success'),
  error:   (msg: string) => useToastStore.getState().push(msg, 'error'),
  warning: (msg: string) => useToastStore.getState().push(msg, 'warning'),
  info:    (msg: string) => useToastStore.getState().push(msg, 'info'),
}
