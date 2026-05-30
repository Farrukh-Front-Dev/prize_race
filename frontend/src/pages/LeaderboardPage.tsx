/**
 * Leaderboard Page
 * Shows event leaderboard with top participants
 */

import React, { useEffect } from 'react'
import { useEventStore } from '../store/eventStore'
import { useAuthStore } from '../store/authStore'
import { Header, Container } from '../components/layout'
import { Leaderboard } from '../components/leaderboard'

interface LeaderboardPageProps {
  eventId: number
  onBack?: () => void
}

export const LeaderboardPage: React.FC<LeaderboardPageProps> = ({
  eventId,
  onBack,
}) => {
  const user = useAuthStore((state) => state.user)
  const { currentEvent, leaderboard, isLoading, fetchEvent, fetchLeaderboard } =
    useEventStore()

  useEffect(() => {
    fetchEvent(eventId)
    fetchLeaderboard(eventId)
  }, [eventId, fetchEvent, fetchLeaderboard])

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <Header
        title={currentEvent?.title || 'Leaderboard'}
        subtitle="Top Participants"
        action={
          onBack && (
            <button
              onClick={onBack}
              className="text-white hover:opacity-80"
            >
              ← Back
            </button>
          )
        }
      />

      <Container className="py-6">
        <Leaderboard
          entries={leaderboard}
          isLoading={isLoading}
          currentUserId={user?.id}
        />
      </Container>
    </div>
  )
}
