/**
 * EventList Component
 * Displays list of events
 */

import React from 'react'
import { Event } from '../../types'
import { EventCard } from './EventCard'
import { Spinner } from '../common'

interface EventListProps {
  events: Event[]
  isLoading?: boolean
  onJoinEvent?: (eventId: number) => void
  joiningEventId?: number | null
}

export const EventList: React.FC<EventListProps> = ({
  events,
  isLoading,
  onJoinEvent,
  joiningEventId,
}) => {
  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Spinner size="lg" />
      </div>
    )
  }

  if (events.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">No active events</p>
      </div>
    )
  }

  return (
    <div>
      {events.map((event) => (
        <EventCard
          key={event.id}
          event={event}
          onJoin={() => onJoinEvent?.(event.id)}
          isLoading={joiningEventId === event.id}
        />
      ))}
    </div>
  )
}
