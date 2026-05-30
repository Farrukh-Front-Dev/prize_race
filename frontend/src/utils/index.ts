/**
 * Utility Functions
 */

export const cn = (...classes: (string | undefined | null | false)[]): string => {
  return classes.filter(Boolean).join(' ')
}

export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat().format(num)
}

export const truncateAddress = (address: string, chars = 4): string => {
  return `${address.slice(0, chars)}...${address.slice(-chars)}`
}
