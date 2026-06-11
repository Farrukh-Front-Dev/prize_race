import React, { useCallback } from 'react'
import { formatDistanceToNow } from 'date-fns'
import { Event } from '../../../shared/types'
import { Card, Badge, Button, Progress, Stat, statusVariant } from '../../../shared/components/ui'
import { formatTon } from '../../../shared/utils'

interface EventCardProps {
  event: Event
  onJoin?: () => void
  onOpen?: () => void
  isJoining?: boolean
  isOrganiser?: boolean
}
export const EventCard: React.FC<EventCardProps> = ({ event, onJoin, onOpen, isJoining = false, isOrganiser = false }) => {
  const endDate = new Date(event.end_date)
  const startDate = new Date(event.start_date)
  const now = new Date()
  const isActive = event.status === 'ACTIVE'
  const isFinished = event.status === 'FINISHED'
  const progressPct = endDate > now
    ? Math.min(100, Math.max(0, ((endDate.getTime() - now.getTime()) / (endDate.getTime() - startDate.getTime())) * 100))
    : 0

  const handleBodyClick = useCallback(() => onOpen?.(), [onOpen])
  const handleJoin = useCallback((e: React.MouseEvent) => { e.stopPropagation(); onJoin?.() }, [onJoin])

  return (
    <Card variant="default" className="mb-4 cursor-pointer hover:shadow-md transition-shadow active:scale-[0.99]" onClick={handleBodyClick}>
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1 min-w-0 mr-2">
          <h3 className="text-base font-bold text-gray-900 leading-tight truncate">{event.title}</h3>
          {event.description && <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{event.description}</p>}
        </div>
        <Badge variant={statusVariant(event.status)} size="sm">
          {event.status === 'PENDING_PAYMENT' ? 'Awaiting' : event.status}
        </Badge>
      </div>
      <div className="grid grid-cols-2 gap-3 pb-3 mb-3 border-b border-gray-100">
        <Stat label="Prize Pool" value={formatTon(event.total_prize_pool)} icon="🏆" />
        <Stat label="Top Winners" value={`Top ${event.top_n_winners}`} icon="🎯" />
      </div>
      {isActive && endDate > now && (
        <div className="mb-3">
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-500 font-medium">Time left</span>
            <span className="text-blue-600 font-bold">{formatDistanceToNow(endDate, { addSuffix: false })}</span>
          </div>
          <Progress value={progressPct} variant="primary" />
        </div>
      )}
      {isActive && !isOrganiser && (
        <Button variant="primary" size="md" fullWidth isLoading={isJoining} onClick={handleJoin} aria-label={`Join ${event.title}`}>
          Join Event
        </Button>
      )}
      {isOrganiser && isActive && <p className="text-center text-xs text-blue-600 font-semibold py-2 bg-blue-50 rounded-lg">You are the organiser</p>}
      {isFinished && <p className="text-center text-xs text-gray-500 font-semibold py-2 bg-gray-50 rounded-lg">Event finished — See winners ›</p>}
    </Card>
  )
}
