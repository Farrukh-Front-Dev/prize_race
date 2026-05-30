/**
 * Events Component
 * Displays event information with status and countdown
 * Professional design with modern UI
 */

import React from 'react'
import { Event } from '../../types'
import { formatDistanceToNow } from 'date-fns'
import { Card, Badge, Button, Progress, Stat } from '../common'

interface EventCardProps {
  event: Event
  onJoin?: () => void
  isJoined?: boolean
  isLoading?: boolean
}

export const EventCard: React.FC<EventCardProps> = ({
  event,
  onJoin,
  isJoined,
  isLoading,
}) => {
  const endDate = new Date(event.end_date)
  const now = new Date()
  const isActive = event.status === 'ACTIVE'
  const isFinished = event.status === 'FINISHED'

  const getStatusVariant = (): 'success' | 'error' | 'warning' | 'info' | 'default' | 'primary' => {
    switch (event.status) {
      case 'ACTIVE':
        return 'success'
      case 'FINISHED':
        return 'default'
      case 'PENDING_PAYMENT':
        return 'warning'
      default:
        return 'info'
    }
  }

  const progressPercent = Math.max(
    0,
    (endDate.getTime() - now.getTime()) /
      (endDate.getTime() - new Date(event.start_date).getTime()) *
      100
  )

  return (
    <Card hover className="mb-4 animate-fade-in">
      {/* Header with Title and Status */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg sm:text-xl font-bold text-gray-900">{event.title}</h3>
          <p className="text-sm text-gray-600 mt-1 line-clamp-2">{event.description}</p>
        </div>
        <Badge variant={getStatusVariant()} size="sm" className="flex-shrink-0 ml-2">
          {event.status}
        </Badge>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 mb-4 pb-4 border-b border-gray-200">
        <Stat
          label="Prize Pool"
          value={`${event.total_prize_pool} TON`}
          icon="🏆"
        />
        <Stat
          label="Winners"
          value={`Top ${event.top_n_winners}`}
          icon="🎯"
        />
      </div>

      {/* Countdown Progress */}
      {isActive && endDate > now && (
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <p className="text-xs font-semibold text-gray-600 uppercase">Time Remaining</p>
            <p className="text-xs font-bold text-primary">
              {formatDistanceToNow(endDate, { addSuffix: false })}
            </p>
          </div>
          <Progress
            value={progressPercent}
            variant="primary"
            animated
          />
        </div>
      )}

      {/* Action Button */}
      {isActive && !isFinished && (
        <Button
          onClick={onJoin}
          disabled={isJoined || isLoading}
          isLoading={isLoading}
          variant={isJoined ? 'secondary' : 'primary'}
          fullWidth
          size="md"
        >
          {isJoined ? '✓ Already Joined' : 'Join Event'}
        </Button>
      )}

      {isFinished && (
        <div className="text-center py-3 bg-gray-50 rounded-lg">
          <p className="text-sm font-semibold text-gray-600">Event Finished</p>
        </div>
      )}
    </Card>
  )
}
