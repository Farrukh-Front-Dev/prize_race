/**
 * Home Page
 * Main page showing all active events with modern design
 */

import React, { useEffect, useState } from 'react'
import { useEventStore } from '../store/eventStore'
import { useAuthStore } from '../store/authStore'
import { Header, Container } from '../components/layout'
import { EventList } from '../components/events'
import { Toast, ToastType } from '../components/feedback'
import { Card } from '../components/common'

export const HomePage: React.FC = () => {
  const user = useAuthStore((state) => state.user)
  const { events, isLoading, error, fetchEvents, joinEvent } = useEventStore()
  const [toast, setToast] = useState<{ message: string; type: ToastType } | null>(null)
  const [joiningEventId, setJoiningEventId] = useState<number | null>(null)

  useEffect(() => {
    fetchEvents('ACTIVE')
  }, [fetchEvents])

  const handleJoinEvent = async (eventId: number) => {
    if (!user) return

    setJoiningEventId(eventId)
    try {
      await joinEvent(eventId, user.id)
      setToast({ message: '🎉 Successfully joined event!', type: 'success' })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to join event'
      setToast({ message, type: 'error' })
    } finally {
      setJoiningEventId(null)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 pb-20">
      <Header
        title="🏆 PrizeRace"
        subtitle="Compete, Win, Earn Rewards"
        variant="gradient"
      />

      <Container className="py-6 sm:py-8">
        {/* Welcome Card */}
        {user && (
          <Card variant="glass" className="mb-6 animate-fade-in">
            <div className="flex items-center gap-3">
              <span className="text-3xl">👋</span>
              <div>
                <p className="text-sm text-gray-600">Welcome back,</p>
                <p className="text-lg font-bold text-gray-900">
                  {user.first_name || user.username || 'Player'}
                </p>
              </div>
            </div>
          </Card>
        )}

        {/* Error Alert */}
        {error && (
          <Card variant="default" className="mb-6 border-l-4 border-red-500 bg-red-50">
            <div className="flex items-start gap-3">
              <span className="text-xl">⚠️</span>
              <div>
                <p className="font-semibold text-red-900">Error</p>
                <p className="text-sm text-red-800 mt-1">{error}</p>
              </div>
            </div>
          </Card>
        )}

        {/* Events List */}
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Active Events</h2>
          <EventList
            events={events}
            isLoading={isLoading}
            onJoinEvent={handleJoinEvent}
            joiningEventId={joiningEventId}
          />
        </div>
      </Container>

      {/* Toast Notification */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  )
}
