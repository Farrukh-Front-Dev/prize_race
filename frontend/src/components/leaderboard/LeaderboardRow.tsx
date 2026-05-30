/**
 * LeaderboardRow Component
 * Single row in leaderboard with modern design
 */

import React from 'react'
import { LeaderboardEntry } from '../../types'

interface LeaderboardRowProps {
  entry: LeaderboardEntry
  isCurrentUser?: boolean
}

export const LeaderboardRow: React.FC<LeaderboardRowProps> = ({
  entry,
  isCurrentUser,
}) => {
  const getMedalEmoji = (rank: number) => {
    switch (rank) {
      case 1:
        return '🥇'
      case 2:
        return '🥈'
      case 3:
        return '🥉'
      default:
        return null
    }
  }

  return (
    <div
      className={`flex items-center px-4 py-3 border-b border-gray-100 transition-colors ${
        isCurrentUser
          ? 'bg-gradient-to-r from-blue-50 to-blue-100 border-blue-200'
          : 'bg-white hover:bg-gray-50'
      }`}
    >
      {/* Rank with Medal */}
      <div className="w-12 flex-shrink-0 flex items-center justify-center">
        {getMedalEmoji(entry.rank) ? (
          <span className="text-xl">{getMedalEmoji(entry.rank)}</span>
        ) : (
          <span className="text-sm font-bold text-gray-600">#{entry.rank}</span>
        )}
      </div>

      {/* User Info */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-gray-900 truncate">
          {entry.username || `User ${entry.user_id}`}
          {isCurrentUser && <span className="ml-2 text-xs text-blue-600 font-bold">YOU</span>}
        </p>
        {entry.wallet_address && (
          <p className="text-xs text-gray-500 truncate font-mono">
            {entry.wallet_address.slice(0, 6)}...{entry.wallet_address.slice(-4)}
          </p>
        )}
      </div>

      {/* XP */}
      <div className="flex-shrink-0 text-right">
        <p className="text-lg font-bold text-primary">{entry.total_xp.toLocaleString()}</p>
        <p className="text-xs text-gray-600 font-medium">XP</p>
      </div>
    </div>
  )
}
