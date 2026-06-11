import { apiClient } from '../../../shared/api/client'
import { Task, TaskCompletion } from '../../../shared/types'

export const tasksApi = {
  listByEvent: (eventId: number) =>
    apiClient.get<Task[]>(`/tasks/event/${eventId}`).then((r) => r.data),

  get: (taskId: number) =>
    apiClient.get<Task>(`/tasks/${taskId}`).then((r) => r.data),

  create: (eventId: number, body: { title: string; description?: string; xp_reward?: number; verification_type?: string; required_channel?: string }) =>
    apiClient.post<Task>(`/tasks/event/${eventId}`, body).then((r) => r.data),

  verify: (taskId: number) =>
    apiClient.post<TaskCompletion>(`/tasks/${taskId}/verify`).then((r) => r.data),
}
