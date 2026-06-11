import { EventStatus } from '../types'

export const EVENT_STATUS_LABEL: Record<EventStatus, string> = {
  DRAFT:           'Draft',
  PENDING_PAYMENT: 'Awaiting Deposit',
  ACTIVE:          'Active',
  FINISHED:        'Finished',
}

export const QUERY_KEYS = {
  me:          ['me']                                   as const,
  events:      (status?: string) => ['events', status] as const,
  event:       (id: number)      => ['event',  id]     as const,
  tasks:       (eventId: number) => ['tasks',  eventId]        as const,
  leaderboard: (eventId: number) => ['leaderboard', eventId]   as const,
  winners:     (eventId: number) => ['winners',     eventId]   as const,
  balance:     ['wallet', 'balance']                    as const,
} as const

export const TOAST_DURATION_MS    = 3_500
export const LEADERBOARD_PAGE_SIZE = 100
