import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { tasksApi } from '../api/tasksApi'
import { QUERY_KEYS } from '../../../shared/constants'

export const useTasks = (eventId: number) =>
  useQuery({ queryKey: QUERY_KEYS.tasks(eventId), queryFn: () => tasksApi.listByEvent(eventId), enabled: !!eventId, staleTime: 60_000 })

export function useVerifyTask() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (taskId: number) => tasksApi.verify(taskId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['leaderboard'] })
      qc.invalidateQueries({ queryKey: ['tasks'] })
    },
  })
}
