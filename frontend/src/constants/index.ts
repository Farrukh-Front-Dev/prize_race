/**
 * Application Constants
 */

export const API_BASE_URL = '/api'

export const EVENT_STATUS = {
  DRAFT: 'DRAFT',
  PENDING_PAYMENT: 'PENDING_PAYMENT',
  ACTIVE: 'ACTIVE',
  FINISHED: 'FINISHED',
} as const

export const TOAST_DURATION = {
  SHORT: 2000,
  NORMAL: 3000,
  LONG: 5000,
} as const

export const PAGINATION = {
  DEFAULT_LIMIT: 100,
  MAX_LIMIT: 1000,
} as const
