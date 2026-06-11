import { apiClient } from '../../../shared/api/client'
import { Event, EventStatus, Participant } from '../../../shared/types'

export const eventsApi = {
  list: (params?: { status?: EventStatus; skip?: number; limit?: number }) =>
    apiClient.get<Event[]>('/events', { params }).then((r) => r.data),

  get: (id: number) =>
    apiClient.get<Event>(`/events/${id}`).then((r) => r.data),

  create: (body: { title: string; description?: string; top_n_winners?: number; total_prize_pool: string; start_date: string; end_date: string }) =>
    apiClient.post<Event>('/events', body).then((r) => r.data),

  update: (id: number, body: Partial<{ title: string; description: string; top_n_winners: number; total_prize_pool: string; start_date: string; end_date: string }>) =>
    apiClient.put<Event>(`/events/${id}`, body).then((r) => r.data),

  lock:   (id: number) => apiClient.post<Event>(`/events/${id}/lock`).then((r) => r.data),
  finish: (id: number) => apiClient.post<Event>(`/events/${id}/finish`).then((r) => r.data),
  join:   (id: number) => apiClient.post<Participant>(`/events/${id}/join`).then((r) => r.data),
}
