import { useQuery } from '@tanstack/react-query'
import { leaderboardApi } from '../api/leaderboardApi'
import { QUERY_KEYS, LEADERBOARD_PAGE_SIZE } from '../../../shared/constants'

export const useLeaderboard = (eventId: number) =>
  useQuery({
    queryKey: QUERY_KEYS.leaderboard(eventId),
    queryFn: () => leaderboardApi.get(eventId, { limit: LEADERBOARD_PAGE_SIZE }),
    enabled: !!eventId,
    staleTime: 10_000,
    refetchInterval: 15_000,
  })

export const useWinners = (eventId: number, enabled: boolean) =>
  useQuery({
    queryKey: QUERY_KEYS.winners(eventId),
    queryFn: () => leaderboardApi.getWinners(eventId),
    enabled: enabled && !!eventId,
    staleTime: 5 * 60_000,
  })
