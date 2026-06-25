import { apiClient } from '../../../shared/api/client'
import { User } from '../../../shared/types'

export const authApi = {
  register: (params: { telegram_id: string; username?: string; first_name?: string; last_name?: string }) =>
    apiClient.post<User>('/auth/register', params).then((r) => r.data),

  getMe: () =>
    apiClient.get<User>('/auth/me').then((r) => r.data),

  updateMe: (params: { username?: string }) =>
    apiClient.put<User>('/auth/me', params).then((r) => r.data),
}
