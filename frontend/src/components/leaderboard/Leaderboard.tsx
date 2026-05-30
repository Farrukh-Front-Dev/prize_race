/**
 * Leaderboard Component
 * Displays top participants with virtualization for performance
 * Modern design with smooth animations
 */

import React from 'react'
import { FixedSizeList as List } from 'react-window'
import { LeaderboardEntry } from '../../types'
import { Card, Spinner } from '../common'
import { LeaderboardRow } from './LeaderboardRow'

interface LeaderboardProps {
  entries: LeaderboardEntry[]
  isLoading?: boolean
  currentUserId?: number
}

interface RowProps {
  index: number
  style: React.CSSProperties
  data: {
    entries: LeaderboardEntry[]
    currentUserId?: number
  }
}

const VirtualizedRow: React.FC<RowProps> = ({ index, style, data }) => {
  const entry = data.entries[index]
  const isCurrentUser = entry.user_id === data.currentUserId

  return (
    <div style={style}>
      <LeaderboardRow entry={entry} isCurrentUser={isCurrentUser} />
    </div>
  )
}

export const Leaderboard: React.FC<LeaderboardProps> = ({
  entries,
  isLoading,
  currentUserId,
}) => {
  const itemCount = entries.length
  const itemSize = 72

  if (isLoading) {
    return (
      <Card>
        <div className="flex justify-center items-center h-64">
          <Spinner size="lg" variant="primary" />
        </div>
      </Card>
    )
  }

  if (itemCount === 0) {
    return (
      <Card>
        <div className="text-center py-12">
          <p className="text-gray-600 font-medium">No participants yet</p>
          <p className="text-sm text-gray-500 mt-1">Be the first to join!</p>
        </div>
      </Card>
    )
  }

  return (
    <Card variant="elevated">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-blue-100 px-4 py-4 -m-6 mb-4 rounded-t-xl border-b border-blue-200">
        <div className="flex items-center gap-8">
          <div className="w-12 flex-shrink-0">
            <p className="text-xs font-bold text-blue-900 uppercase tracking-wider">Rank</p>
          </div>
          <div className="flex-1">
            <p className="text-xs font-bold text-blue-900 uppercase tracking-wider">User</p>
          </div>
          <div className="flex-shrink-0 text-right">
            <p className="text-xs font-bold text-blue-900 uppercase tracking-wider">XP</p>
          </div>
        </div>
      </div>

      {/* List */}
      <div className="mt-2">
        <List
          height={Math.min(itemCount * itemSize, 450)}
          itemCount={itemCount}
          itemSize={itemSize}
          width="100%"
          itemData={{ entries, currentUserId }}
        >
          {VirtualizedRow}
        </List>
      </div>
    </Card>
  )
}
