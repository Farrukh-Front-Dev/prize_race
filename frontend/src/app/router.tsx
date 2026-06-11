/**
 * app/router.tsx
 * ──────────────
 * Zustand-based lightweight router for Telegram Mini App.
 * No react-router — keeps bundle small and works perfectly inside Telegram WebView.
 */
import React from 'react'
import { useEventUiStore } from '../features/events'
import { HomePage }         from '../pages/HomePage'
import { EventDetailPage }  from '../pages/EventDetailPage'
import { LeaderboardPage }  from '../pages/LeaderboardPage'

export const AppRouter: React.FC = () => {
  const { selectedEventId, eventPage } = useEventUiStore()

  if (!selectedEventId) return <HomePage />
  if (eventPage === 'leaderboard') return <LeaderboardPage eventId={selectedEventId} />
  return <EventDetailPage eventId={selectedEventId} />
}
