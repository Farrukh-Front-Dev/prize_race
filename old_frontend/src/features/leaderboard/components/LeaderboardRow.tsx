import React from 'react'
import { LeaderboardEntry } from '../../../shared/types'
import { cn, formatNumber, truncateAddress } from '../../../shared/utils'

const MEDAL: Record<number, string> = { 1: '🥇', 2: '🥈', 3: '🥉' }

export const LeaderboardRow: React.FC<{ entry: LeaderboardEntry; isCurrentUser?: boolean }> = ({ entry, isCurrentUser = false }) => {
  const medal = MEDAL[entry.rank]
  const name = entry.username ? `@${entry.username}` : `User #${entry.user_id}`
  return (
    <div className={cn('flex items-center gap-3 px-4 py-3 border-b border-gray-100 last:border-0', isCurrentUser ? 'bg-blue-50' : 'bg-white hover:bg-gray-50')}>
      <div className="w-10 flex-shrink-0 text-center">
        {medal
          ? <span className="text-xl" aria-label={`Rank ${entry.rank}`}>{medal}</span>
          : <span className="text-sm font-bold text-gray-500">#{entry.rank}</span>}
      </div>
      <div className="flex-1 min-w-0">
        <p className={cn('text-sm font-semibold truncate', isCurrentUser ? 'text-blue-700' : 'text-gray-900')}>
          {name}{isCurrentUser && <span className="ml-1.5 text-xs font-normal text-blue-500">(you)</span>}
        </p>
        {entry.wallet_address && <p className="text-xs text-gray-400 font-mono truncate">{truncateAddress(entry.wallet_address, 6)}</p>}
      </div>
      <div className="flex-shrink-0 text-right">
        <p className={cn('text-sm font-bold', isCurrentUser ? 'text-blue-700' : 'text-gray-900')}>{formatNumber(entry.total_xp)}</p>
        <p className="text-xs text-gray-400">XP</p>
      </div>
    </div>
  )
}
