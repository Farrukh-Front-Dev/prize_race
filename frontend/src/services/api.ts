/**
 * API Service
 * Handles all backend communication with Telegram validation
 */

import axios, { AxiosInstance, AxiosError } from 'axios'
import { User, Event, Task, Participant, LeaderboardEntry } from '../types'

class ApiService {
  private client: AxiosInstance
  private initData: string = ''

  constructor() {
    this.client = axios.create({
      baseURL: '/api',
      timeout: 10000,
    })

    // Add Telegram Init Data to all requests
    this.client.interceptors.request.use((config) => {
      if (this.initData) {
        config.headers['X-Telegram-Init-Data'] = this.initData
      }
      return config
    })

    // Handle errors globally
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 429) {
          console.warn('Rate limited - request in progress')
        }
        return Promise.reject(error)
      }
    )
  }

  setInitData(data: string) {
    this.initData = data
  }

  // Auth endpoints
  async registerUser(telegramId: string, username?: string) {
    const response = await this.client.post<User>('/auth/register', {
      telegram_id: telegramId,
      username,
    })
    return response.data
  }

  async getCurrentUser(telegramId: string) {
    const response = await this.client.get<User>('/auth/me', {
      params: { telegram_id: telegramId },
    })
    return response.data
  }

  async updateUser(telegramId: string, data: Partial<User>) {
    const response = await this.client.put<User>('/auth/me', data, {
      params: { telegram_id: telegramId },
    })
    return response.data
  }

  // Event endpoints
  async listEvents(status?: string) {
    const response = await this.client.get<Event[]>('/events', {
      params: { status_filter: status },
    })
    return response.data
  }

  async getEvent(eventId: number) {
    const response = await this.client.get<Event>(`/events/${eventId}`)
    return response.data
  }

  async createEvent(data: Partial<Event>, organizerId: number) {
    const response = await this.client.post<Event>('/events', data, {
      params: { organizer_id: organizerId },
    })
    return response.data
  }

  async updateEvent(eventId: number, data: Partial<Event>, organizerId: number) {
    const response = await this.client.put<Event>(`/events/${eventId}`, data, {
      params: { organizer_id: organizerId },
    })
    return response.data
  }

  async joinEvent(eventId: number, userId: number) {
    const response = await this.client.post<Participant>(
      `/events/${eventId}/join`,
      {},
      { params: { user_id: userId } }
    )
    return response.data
  }

  async getLeaderboard(eventId: number, limit: number = 100) {
    const response = await this.client.get<LeaderboardEntry[]>(
      `/events/${eventId}/leaderboard`,
      { params: { limit } }
    )
    return response.data
  }

  // Task endpoints
  async getTask(taskId: number) {
    const response = await this.client.get<Task>(`/tasks/${taskId}`)
    return response.data
  }

  async verifyTask(taskId: number, userId: number) {
    const response = await this.client.post(
      `/tasks/${taskId}/verify`,
      {},
      { params: { user_id: userId } }
    )
    return response.data
  }

  // Wallet endpoints
  async connectWallet(walletAddress: string, signature: string, message: string, userId: number) {
    const response = await this.client.post<User>(
      '/wallet/connect',
      { wallet_address: walletAddress, signature, message },
      { params: { user_id: userId } }
    )
    return response.data
  }

  async validateDeposit(eventId: number, txHash: string, amount: number, userId: number) {
    const response = await this.client.post(
      '/wallet/deposit',
      { event_id: eventId, tx_hash: txHash, amount },
      { params: { user_id: userId } }
    )
    return response.data
  }

  async getWalletBalance(userId: number) {
    const response = await this.client.get(
      '/wallet/balance',
      { params: { user_id: userId } }
    )
    return response.data
  }
}

export const apiService = new ApiService()
