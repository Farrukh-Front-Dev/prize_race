import React from 'react'
import { Event } from '../../../shared/types'
import { SkeletonCard } from '../../../shared/components/ui'
import { EventCard } from './EventCard'

interface EventListProps {
  events: Event[]
  isLoading?: boolean
  currentUserId?: number
  onJoin?: (eventId: number) => void
  onOpen?: (eventId: number) => void
  joiningId?: number | null
}
export const EventList: React.FC<EventListProps> = ({ events, isLoading, currentUserId, onJoin, onOpen, joiningId }) => {
  if (isLoading) return <div>{[1, 2, 3].map((i) => <SkeletonCard key={i} />)}</div>
  if (!events.length) return (
    <div className="text-center py-16">
      <p className="text-4xl mb-3">🏁</p>
      <p className="text-gray-600 font-medium">No active events right now</p>
      <p className="text-gray-400 text-sm mt-1">Check back soon!</p>
    </div>
  )
  return (
    <div>
      {events.map((event) => (
        <EventCard key={event.id} event={event}
          onJoin={onJoin ? () => onJoin(event.id) : undefined}
          onOpen={onOpen ? () => onOpen(event.id) : undefined}
          isJoining={joiningId === event.id}
          isOrganiser={currentUserId === event.organizer_id}
        />
      ))}
    </div>
  )
}
