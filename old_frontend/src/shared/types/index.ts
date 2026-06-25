// ── Domain types (mirror backend Pydantic schemas) ────────────────────────────

export type EventStatus = 'DRAFT' | 'PENDING_PAYMENT' | 'ACTIVE' | 'FINISHED'
export type VerificationType = 'manual' | 'channel_subscription'

export interface User {
  id: number
  telegram_id: string
  username?: string | null
  first_name?: string | null
  last_name?: string | null
  wallet_address?: string | null
  created_at: string
  updated_at: string
}

export interface Event {
  id: number
  organizer_id: number
  title: string
  description?: string | null
  status: EventStatus
  top_n_winners: number
  total_prize_pool: string // Decimal → string
  start_date: string
  end_date: string
  tx_hash?: string | null
  created_at: string
  updated_at: string
}

export interface Task {
  id: number
  event_id: number
  title: string
  description?: string | null
  xp_reward: number
  verification_type: VerificationType
  required_channel?: string | null
  created_at: string
}

export interface Participant {
  id: number
  user_id: number
  event_id: number
  total_xp: number
  joined_at: string
}

export interface LeaderboardEntry {
  rank: number
  user_id: number
  username?: string | null
  total_xp: number
  wallet_address?: string | null
}

export interface TaskCompletion {
  id: number
  user_id: number
  task_id: number
  completed_at: string
  verified: boolean
}

// ── Telegram ──────────────────────────────────────────────────────────────────

export interface TelegramUser {
  id: number
  is_bot: boolean
  first_name: string
  last_name?: string
  username?: string
  language_code?: string
  is_premium?: boolean
}

// ── UI ────────────────────────────────────────────────────────────────────────

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface ToastItem {
  id: string
  message: string
  type: ToastType
}
