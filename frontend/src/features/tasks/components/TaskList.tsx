import React from 'react'
import { Task } from '../../../shared/types'
import { Spinner } from '../../../shared/components/ui'
import { TaskCard } from './TaskCard'

interface TaskListProps {
  tasks: Task[]
  completedIds?: Set<number>
  isLoading?: boolean
  onVerify?: (taskId: number) => void
  verifyingId?: number | null
}
export const TaskList: React.FC<TaskListProps> = ({ tasks, completedIds = new Set(), isLoading, onVerify, verifyingId }) => {
  if (isLoading) return <div className="flex justify-center py-8"><Spinner size="md" /></div>
  if (!tasks.length) return <div className="text-center py-10"><p className="text-gray-400 text-sm">No tasks for this event</p></div>
  return (
    <div>
      {tasks.map((task) => (
        <TaskCard key={task.id} task={task} isCompleted={completedIds.has(task.id)}
          onVerify={onVerify ? () => onVerify(task.id) : undefined}
          isVerifying={verifyingId === task.id}
        />
      ))}
    </div>
  )
}
