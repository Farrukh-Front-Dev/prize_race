import React from 'react'
import { Task } from '../../../shared/types'
import { Card, Badge, Button } from '../../../shared/components/ui'
import { cn } from '../../../shared/utils'

const VTYPE_ICON: Record<string, string> = { manual: '✏️', channel_subscription: '📢' }

export const TaskCard: React.FC<{ task: Task; isCompleted?: boolean; onVerify?: () => void; isVerifying?: boolean }> = ({ task, isCompleted = false, onVerify, isVerifying = false }) => (
  <Card variant="default" className={cn('mb-3', isCompleted && 'opacity-70')}>
    <div className="flex items-start gap-3">
      <span className="text-2xl flex-shrink-0 mt-0.5">{VTYPE_ICON[task.verification_type] ?? '📋'}</span>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2 mb-1">
          <p className={cn('text-sm font-semibold truncate', isCompleted ? 'text-gray-400 line-through' : 'text-gray-900')}>{task.title}</p>
          <Badge variant="primary" size="sm" className="flex-shrink-0">+{task.xp_reward} XP</Badge>
        </div>
        {task.description && <p className="text-xs text-gray-500 mb-2">{task.description}</p>}
        {task.required_channel && <p className="text-xs text-blue-600 mb-2 font-mono">Subscribe: {task.required_channel}</p>}
        {!isCompleted && onVerify && <Button variant="outline" size="sm" isLoading={isVerifying} onClick={onVerify} aria-label={`Complete task: ${task.title}`}>Complete</Button>}
        {isCompleted && <p className="text-xs text-green-600 font-semibold">✓ Completed</p>}
      </div>
    </div>
  </Card>
)
