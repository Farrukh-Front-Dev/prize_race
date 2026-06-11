import React from 'react'
import { Header, Container } from '../shared/components/layout'
import { Card } from '../shared/components/ui'
import { EventList, useEvents, useJoinEvent, useEventUiStore } from '../features/events'
import { useAuthStore } from '../features/auth'
import { toast } from '../features/notifications/store'
import { ApiError, getErrorMessage } from '../shared/api'
import { displayName } from '../shared/utils'

export const HomePage: React.FC = () => {
  const user = useAuthStore((s) => s.user)
  const selectEvent = useEventUiStore((s) => s.selectEvent)
  const { data: events = [], isLoading } = useEvents('ACTIVE')
  const joinMutation = useJoinEvent()

  const handleJoin = (eventId: number) => {
    if (joinMutation.isPending) return
    joinMutation.mutate(eventId, {
      onSuccess: () => { toast.success('🎉 Joined! Check the leaderboard.'); selectEvent(eventId, 'leaderboard') },
      onError: (err) => {
        const e = err as ApiError
        if (e.status === 400 || e.status === 409) { toast.info('You already joined this event.'); selectEvent(eventId, 'leaderboard') }
        else if (e.status === 429) toast.warning('Request in progress — please wait.')
        else if (e.status === 403) toast.warning(e.detail)
        else toast.error(getErrorMessage(err))
      },
    })
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-8">
      <Header title="🏆 PrizeRace" subtitle="Compete · Win · Earn TON" />
      <Container className="py-5">
        {user && (
          <Card variant="glass" className="mb-5">
            <div className="flex items-center gap-3">
              <span className="text-3xl select-none">👋</span>
              <div>
                <p className="text-xs text-gray-500">Welcome back</p>
                <p className="text-base font-bold text-gray-900">{displayName(user)}</p>
              </div>
              {user.wallet_address && (
                <span className="ml-auto text-xs text-green-600 font-semibold bg-green-50 px-2 py-0.5 rounded-full">Wallet ✓</span>
              )}
            </div>
          </Card>
        )}
        <h2 className="text-sm font-bold text-gray-500 uppercase tracking-wide mb-3">Active Sprints</h2>
        <EventList
          events={events} isLoading={isLoading} currentUserId={user?.id}
          onJoin={handleJoin}
          onOpen={(id) => selectEvent(id, 'overview')}
          joiningId={joinMutation.isPending ? joinMutation.variables ?? null : null}
        />
      </Container>
    </div>
  )
}
