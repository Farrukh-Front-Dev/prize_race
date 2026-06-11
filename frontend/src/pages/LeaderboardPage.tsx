import React from 'react'
import { Header, Container } from '../shared/components/layout'
import { Leaderboard, useLeaderboard } from '../features/leaderboard'
import { useEvent, useEventUiStore } from '../features/events'
import { useAuthStore } from '../features/auth'

export const LeaderboardPage: React.FC<{ eventId: number }> = ({ eventId }) => {
  const user = useAuthStore((s) => s.user)
  const clearSelection = useEventUiStore((s) => s.clearSelection)
  const { data: event } = useEvent(eventId)
  const { data: entries = [], isLoading } = useLeaderboard(eventId)
  const currentUserEntry = entries.find((e) => e.user_id === user?.id) ?? null

  return (
    <div className="min-h-screen bg-gray-50 pb-8">
      <Header title={event?.title ?? 'Leaderboard'} subtitle={`${entries.length} participant${entries.length !== 1 ? 's' : ''}`} onBack={clearSelection} />
      <Container className="py-4">
        <Leaderboard entries={entries} isLoading={isLoading} currentUserId={user?.id} currentUserEntry={currentUserEntry} />
      </Container>
    </div>
  )
}
