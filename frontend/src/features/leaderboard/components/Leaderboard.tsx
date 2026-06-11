import React from 'react'
import { FixedSizeList as VList, ListChildComponentProps } from 'react-window'
import { LeaderboardEntry } from '../../../shared/types'
import { Card, Spinner } from '../../../shared/components/ui'
import { LeaderboardRow } from './LeaderboardRow'

interface LeaderboardProps {
  entries: LeaderboardEntry[]
  isLoading?: boolean
  currentUserId?: number
  currentUserEntry?: LeaderboardEntry | null
}
const ROW_HEIGHT = 64
const Row: React.FC<ListChildComponentProps<{ entries: LeaderboardEntry[]; currentUserId?: number }>> = ({ index, style, data }) => (
  <div style={style}>
    <LeaderboardRow entry={data.entries[index]} isCurrentUser={data.entries[index].user_id === data.currentUserId} />
  </div>
)
export const Leaderboard: React.FC<LeaderboardProps> = ({ entries, isLoading, currentUserId, currentUserEntry }) => {
  if (isLoading) return <Card><div className="flex justify-center items-center py-16"><Spinner size="lg" /></div></Card>
  if (!entries.length) return (
    <Card><div className="text-center py-16"><p className="text-3xl mb-2">🏆</p><p className="font-medium text-gray-600">No participants yet</p><p className="text-sm text-gray-400 mt-1">Be the first to join!</p></div></Card>
  )
  const listHeight = Math.min(entries.length * ROW_HEIGHT, 480)
  return (
    <div>
      <div className="flex items-center gap-3 px-4 py-2 bg-gray-50 rounded-t-xl border border-b-0 border-gray-200">
        <div className="w-10 text-xs font-bold text-gray-500 uppercase text-center">Rank</div>
        <div className="flex-1 text-xs font-bold text-gray-500 uppercase">Player</div>
        <div className="text-xs font-bold text-gray-500 uppercase">XP</div>
      </div>
      <div className="border border-gray-200 rounded-b-xl overflow-hidden">
        <VList height={listHeight} itemCount={entries.length} itemSize={ROW_HEIGHT} width="100%" itemData={{ entries, currentUserId }} overscanCount={5}>{Row}</VList>
      </div>
      {currentUserEntry && !entries.slice(0, Math.floor(480 / ROW_HEIGHT)).find((e) => e.user_id === currentUserId) && (
        <div className="mt-2 border border-blue-200 rounded-xl overflow-hidden">
          <div className="bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-600">Your position</div>
          <LeaderboardRow entry={currentUserEntry} isCurrentUser />
        </div>
      )}
    </div>
  )
}
