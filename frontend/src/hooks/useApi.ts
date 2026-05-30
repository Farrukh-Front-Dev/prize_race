/**
 * useApi Hook
 * Wrapper around React Query for API calls
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { AxiosError } from 'axios'
import { ApiError } from '../types'

export const useApi = () => {
  const queryClient = useQueryClient()

  return {
    queryClient,
    handleError: (error: unknown): string => {
      if (error instanceof AxiosError) {
        const data = error.response?.data as ApiError
        return data?.detail || error.message
      }
      return error instanceof Error ? error.message : 'Unknown error'
    },
  }
}
