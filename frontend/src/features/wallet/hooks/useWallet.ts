import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { walletApi } from '../api/walletApi'
import { QUERY_KEYS } from '../../../shared/constants'

export const useWalletBalance = (enabled: boolean) =>
  useQuery({ queryKey: QUERY_KEYS.balance, queryFn: () => walletApi.getBalance(), enabled, staleTime: 30_000 })

export function useConnectWallet() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: { wallet_address: string; signature: string; message: string }) => walletApi.connect(body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: QUERY_KEYS.me })
      qc.invalidateQueries({ queryKey: QUERY_KEYS.balance })
    },
  })
}
