/** Merge class names (tiny clsx replacement) */
export const cn = (...classes: (string | undefined | null | false)[]): string =>
  classes.filter(Boolean).join(' ')

/** 12345 → "12,345" */
export const formatNumber = (n: number): string =>
  new Intl.NumberFormat().format(n)

/** "EQCxxxx" → "EQCx…xxxx" */
export const truncateAddress = (addr: string, chars = 4): string =>
  addr.length <= chars * 2 + 3 ? addr : `${addr.slice(0, chars)}…${addr.slice(-chars)}`

/** Decimal string or number → "10.50 TON" */
export const formatTon = (amount: string | number): string => {
  const n = typeof amount === 'string' ? parseFloat(amount) : amount
  return isNaN(n) ? '0 TON' : `${n.toFixed(2)} TON`
}

/** User → display name */
export const displayName = (user: {
  first_name?: string | null
  username?: string | null
  telegram_id: string
}): string =>
  user.first_name || (user.username ? `@${user.username}` : `#${user.telegram_id}`)

/** ISO → "Jun 12, 2026" */
export const formatDate = (iso: string): string =>
  new Date(iso).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
  })

/** Seconds remaining until ISO date (≥ 0) */
export const secondsUntil = (iso: string): number =>
  Math.max(0, Math.floor((new Date(iso).getTime() - Date.now()) / 1000))
