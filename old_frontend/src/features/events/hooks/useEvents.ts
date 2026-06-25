import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { eventsApi } from '../api/eventsApi'
import { QUERY_KEYS } from '../../../shared/constants'
import { EventStatus } from '../../../shared/types'

export const useEvents = (status?: EventStatus) =>
  useQuery({ queryKey: QUERY_KEYS.events(status), queryFn: () => eventsApi.list({ status }), staleTime: 30_000 })

export const useEvent = (eventId: number) =>
  useQuery({ queryKey: QUERY_KEYS.event(eventId), queryFn: () => eventsApi.get(eventId), staleTime: 30_000, enabled: !!eventId })

export function useJoinEvent() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (eventId: number) => eventsApi.join(eventId),
    onSuccess: (_, eventId) => {
      qc.invalidateQueries({ queryKey: QUERY_KEYS.event(eventId) })
      qc.invalidateQueries({ queryKey: QUERY_KEYS.leaderboard(eventId) })
    },
  })
}
