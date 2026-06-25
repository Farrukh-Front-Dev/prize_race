import { apiClient } from '../../../shared/api/client'
import { User, EventStatus } from '../../../shared/types'

export const walletApi = {
  connect: (body: { wallet_address: string; signature: string; message: string }) =>
    apiClient.post<User>('/wallet/connect', body).then((r) => r.data),

  deposit: (body: { event_id: number; tx_hash: string; amount: string }) =>
    apiClient.post<{ status: string; event_id: number; event_status: EventStatus; tx_hash: string }>('/wallet/deposit', body).then((r) => r.data),

  getBalance: () =>
    apiClient.get<{ wallet_address: string; balance_ton: number; currency: string }>('/wallet/balance').then((r) => r.data),
}
