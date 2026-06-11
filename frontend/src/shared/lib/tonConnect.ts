/**
 * TonConnect configuration.
 * manifestUrl is derived at runtime so it works on any deployment origin.
 */
export const TON_MANIFEST_URL =
  typeof window !== 'undefined'
    ? `${window.location.origin}/tonconnect-manifest.json`
    : 'https://your-domain.com/tonconnect-manifest.json'
