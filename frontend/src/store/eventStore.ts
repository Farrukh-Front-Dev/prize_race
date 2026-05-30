/**
 * Event Store
 * Manages events and leaderboard state
 */

import { create } from 'zustand'
import { Event, LeaderboardEntry } from '../types'
import { apiService } from '../services/api'

interface EventState {
  events: Event[]
  currentEvent: Event | null
  leaderboard: LeaderboardEntry[]
  isLoading: boolean
  error: string | null

  // Actions
  fetchEvents: (status?: string) => Promise<void>
  fetchEvent: (eventId: number) => Promise<void>
  fetchLeaderboard: (eventId: number, limit?: number) => Promise<void>
  joinEvent: (eventId: number, userId: number) => Promise<void>
}

export const useEventStore = create<EventState>((set) => ({
  events: [],
  currentEvent: null,
  leaderboard: [],
  isLoading: false,
  error: null,

  fetchEvents: async (status?: string) => {
    set({ isLoading: true, error: null })
    try {
      const events = await apiService.listEvents(status)
      set({ events, isLoading: false })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch events'
      set({ error: message, isLoading: false })
    }
  },

  fetchEvent: async (eventId: number) => {
    set({ isLoading: true, error: null })
    try {
      const event = await apiService.getEvent(eventId)
      set({ currentEvent: event, isLoading: false })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch event'
      set({ error: message, isLoading: false })
    }
  },

  fetchLeaderboard: async (eventId: number, limit: number = 100) => {
    set({ isLoading: true, error: null })
    try {
      const leaderboard = await apiService.getLeaderboard(eventId, limit)
      set({ leaderboard, isLoading: false })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch leaderboard'
      set({ error: message, isLoading: false })
    }
  },

  joinEvent: async (eventId: number, userId: number) => {
    set({ isLoading: true, error: null })
    try {
      await apiService.joinEvent(eventId, userId)
      set({ isLoading: false })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to join event'
      set({ error: message, isLoading: false })
      throw error
    }
  },
}))
