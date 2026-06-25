import { apiClient } from '../../../shared/api/client'
import { LeaderboardEntry } from '../../../shared/types'

export const leaderboardApi = {
  get: (eventId: number, params?: { limit?: number; offset?: number }) =>
    apiClient.get<LeaderboardEntry[]>(`/events/${eventId}/leaderboard`, { params }).then((r) => r.data),

  getWinners: (eventId: number) =>
    apiClient.get<LeaderboardEntry[]>(`/events/${eventId}/winners`).then((r) => r.data),
}
