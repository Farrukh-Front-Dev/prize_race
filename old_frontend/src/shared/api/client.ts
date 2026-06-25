/**
 * shared/api/client.ts
 * ─────────────────────
 * Axios instance — used by every feature API module.
 *
 * Auth header strategy:
 *   1. Real Telegram: window.Telegram.WebApp.initData (non-empty)
 *   2. Browser dev:   stored initData from setInitData() (mock hash accepted by backend DEBUG=True)
 */
import axios, { AxiosError } from 'axios'

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly detail: string,
  ) {
    super(detail)
    this.name = 'ApiError'
  }
}

export function getErrorMessage(err: unknown): string {
  if (err instanceof ApiError) return err.detail
  if (err instanceof Error) return err.message
  return 'Something went wrong'
}

// Module-level fallback initData used in dev/browser mode
let _storedInitData = ''

/** Called once by authStore after Telegram / mock init */
export function setInitData(initData: string): void {
  _storedInitData = initData
}

export const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 10_000,
  headers: { 'Content-Type': 'application/json' },
})

// Inject X-Telegram-Init-Data on every request
apiClient.interceptors.request.use((config) => {
  // Priority: stored initData (set after auth init) > live WebApp.initData
  // In browser mode, WebApp.initData is "" so we always use stored
  const initData = _storedInitData || window.Telegram?.WebApp?.initData || ''
  if (initData) {
    config.headers['X-Telegram-Init-Data'] = initData
  }
  return config
})

// Normalize all errors to ApiError
apiClient.interceptors.response.use(
  (res) => res,
  (err: AxiosError<{ detail?: string }>) => {
    const status = err.response?.status ?? 0
    const detail = err.response?.data?.detail ?? err.message ?? 'Unknown error'
    return Promise.reject(new ApiError(status, detail))
  },
)
