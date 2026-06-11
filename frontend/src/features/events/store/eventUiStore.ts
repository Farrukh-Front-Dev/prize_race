import { create } from 'zustand'

type EventPage = 'overview' | 'tasks' | 'leaderboard'

interface EventUIState {
  selectedEventId: number | null
  eventPage: EventPage
  selectEvent: (id: number, page?: EventPage) => void
  clearSelection: () => void
  setEventPage: (page: EventPage) => void
}
export const useEventUiStore = create<EventUIState>((set) => ({
  selectedEventId: null,
  eventPage: 'overview',
  selectEvent: (id, page = 'overview') => set({ selectedEventId: id, eventPage: page }),
  clearSelection: () => set({ selectedEventId: null, eventPage: 'overview' }),
  setEventPage: (page) => set({ eventPage: page }),
}))
