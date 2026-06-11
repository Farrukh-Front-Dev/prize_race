import React from 'react'
import { QueryClientProvider } from '@tanstack/react-query'
import { TonConnectUIProvider } from '@tonconnect/ui-react'
import { queryClient } from '../shared/lib/queryClient'
import { TON_MANIFEST_URL } from '../shared/lib/tonConnect'
import { ErrorBoundary } from '../shared/components/feedback'
import { ToastContainer } from '../shared/components/feedback'

interface ProvidersProps { children: React.ReactNode }

export const Providers: React.FC<ProvidersProps> = ({ children }) => (
  <TonConnectUIProvider manifestUrl={TON_MANIFEST_URL}>
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        <ToastContainer />
        {children}
      </ErrorBoundary>
    </QueryClientProvider>
  </TonConnectUIProvider>
)
