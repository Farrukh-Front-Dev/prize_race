/**
 * Type definitions for PrizeRace Frontend
 */

export interface User {
  id: number
  telegram_id: string
  username?: string
  first_name?: string
  last_name?: string
  wallet_address?: string
  created_at: string
  updated_at: string
}

export interface Event {
  id: number
  organizer_id: number
  title: string
  description?: string
  status: EventStatus
  top_n_winners: number
  total_prize_pool: number
  start_date: string
  end_date: string
  tx_hash?: string
  created_at: string
  updated_at: string
}

export type EventStatus = 'DRAFT' | 'PENDING_PAYMENT' | 'ACTIVE' | 'FINISHED'

export interface Task {
  id: number
  event_id: number
  title: string
  description?: string
  xp_reward: number
  verification_type: string
  required_channel?: string
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
  username?: string
  total_xp: number
  wallet_address?: string
}

export interface TaskCompletion {
  id: number
  user_id: number
  task_id: number
  completed_at: string
  verified: boolean
}

export interface TelegramUser {
  id: number
  is_bot: boolean
  first_name: string
  last_name?: string
  username?: string
  language_code?: string
  is_premium?: boolean
}

export interface ApiError {
  detail: string
}
