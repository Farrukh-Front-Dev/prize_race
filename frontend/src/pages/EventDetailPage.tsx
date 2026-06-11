import React, { useState } from 'react'
import { Header, Container } from '../shared/components/layout'
import { Card, Badge, Stat, Spinner, statusVariant } from '../shared/components/ui'
import { TaskList, useVerifyTask, useTasks } from '../features/tasks'
import { Leaderboard, useLeaderboard } from '../features/leaderboard'
import { useEvent, useEventUiStore } from '../features/events'
import { useAuthStore } from '../features/auth'
import { toast } from '../features/notifications/store'
import { ApiError, getErrorMessage } from '../shared/api'
import { formatTon, formatDate } from '../shared/utils'

type Tab = 'overview' | 'tasks' | 'leaderboard'

export const EventDetailPage: React.FC<{ eventId: number }> = ({ eventId }) => {
  const user = useAuthStore((s) => s.user)
  const clearSelection = useEventUiStore((s) => s.clearSelection)
  const [tab, setTab] = useState<Tab>('overview')
  const [completedIds, setCompletedIds] = useState<Set<number>>(new Set())

  const { data: event, isLoading: eventLoading } = useEvent(eventId)
  const { data: tasks = [], isLoading: tasksLoading } = useTasks(eventId)
  const { data: leaderboard = [], isLoading: lbLoading } = useLeaderboard(eventId)
  const verifyMutation = useVerifyTask()
  const currentUserEntry = leaderboard.find((e) => e.user_id === user?.id) ?? null

  const handleVerify = (taskId: number) => {
    if (verifyMutation.isPending) return
    verifyMutation.mutate(taskId, {
      onSuccess: () => { setCompletedIds((p) => new Set([...p, taskId])); toast.success('✅ Task completed! XP awarded.') },
      onError: (err) => {
        const e = err as ApiError
        if (e.status === 400 || e.status === 409) { setCompletedIds((p) => new Set([...p, taskId])); toast.info('Already completed.') }
        else if (e.status === 403) toast.warning(e.detail)
        else if (e.status === 429) toast.warning('Processing — please wait.')
        else toast.error(getErrorMessage(err))
      },
    })
  }

  if (eventLoading) return <div className="min-h-screen bg-gray-50"><Header title="Loading…" onBack={clearSelection} /><div className="flex justify-center py-16"><Spinner size="lg" /></div></div>
  if (!event) return <div className="min-h-screen bg-gray-50"><Header title="Not found" onBack={clearSelection} /><Container className="py-8 text-center"><p className="text-gray-500">Event not found.</p></Container></div>

  const isOrganiser = user?.id === event.organizer_id

  return (
    <div className="min-h-screen bg-gray-50 pb-8">
      <Header title={event.title} subtitle={`Status: ${event.status}`} onBack={clearSelection} />
      <Container className="py-4">
        <Card variant="elevated" className="mb-4">
          <div className="flex items-center justify-between mb-3">
            <Badge variant={statusVariant(event.status)}>{event.status}</Badge>
            {isOrganiser && <span className="text-xs text-blue-600 font-semibold">You organised this</span>}
          </div>
          {event.description && <p className="text-sm text-gray-600 mb-4">{event.description}</p>}
          <div className="grid grid-cols-3 gap-3">
            <Stat label="Prize" value={formatTon(event.total_prize_pool)} icon="🏆" />
            <Stat label="Winners" value={`Top ${event.top_n_winners}`} icon="🎯" />
            <Stat label="Ends" value={formatDate(event.end_date)} icon="📅" />
          </div>
        </Card>

        {currentUserEntry && (
          <Card variant="flat" padding="sm" className="mb-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Your position</span>
              <div className="flex items-center gap-3">
                <span className="text-xs text-gray-500">Rank #{currentUserEntry.rank}</span>
                <span className="text-base font-bold text-blue-700">{currentUserEntry.total_xp} XP</span>
              </div>
            </div>
          </Card>
        )}

        <div className="flex bg-white rounded-xl border border-gray-200 p-1 gap-1 mb-4">
          {(['overview', 'tasks', 'leaderboard'] as Tab[]).map((t) => (
            <button key={t} onClick={() => setTab(t)}
              className={['flex-1 py-2 text-sm font-semibold rounded-lg capitalize transition-colors', tab === t ? 'bg-blue-600 text-white' : 'text-gray-500 hover:text-gray-800'].join(' ')}>
              {t === 'leaderboard' ? '🏅 Board' : t === 'tasks' ? '📋 Tasks' : '📄 Info'}
            </button>
          ))}
        </div>

        {tab === 'overview' && (
          <Card>
            <h3 className="text-sm font-bold text-gray-700 mb-3">Sprint Details</h3>
            <dl className="space-y-2 text-sm">
              {[['Start', formatDate(event.start_date)], ['End', formatDate(event.end_date)], ['Prize Pool', formatTon(event.total_prize_pool)], ['Top Winners', `Top ${event.top_n_winners}`]].map(([l, v]) => (
                <div key={l} className="flex justify-between"><dt className="text-gray-500">{l}</dt><dd className="font-semibold text-gray-900">{v}</dd></div>
              ))}
            </dl>
          </Card>
        )}
        {tab === 'tasks' && <TaskList tasks={tasks} completedIds={completedIds} isLoading={tasksLoading} onVerify={event.status === 'ACTIVE' && !isOrganiser ? handleVerify : undefined} verifyingId={verifyMutation.isPending ? verifyMutation.variables ?? null : null} />}
        {tab === 'leaderboard' && <Leaderboard entries={leaderboard} isLoading={lbLoading} currentUserId={user?.id} currentUserEntry={currentUserEntry} />}
      </Container>
    </div>
  )
}
