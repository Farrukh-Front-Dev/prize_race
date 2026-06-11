# PrizeRace Frontend

React 18 + TypeScript + Vite Telegram Mini App.  
Arxitektura: **Feature-Sliced Design (FSD)**.

---

## Stack

| | Tech |
|---|---|
| Framework | React 18 + TypeScript 5 |
| Build | Vite 5 + Tailwind CSS v4 |
| State | Zustand 4 |
| Server state | TanStack Query v5 |
| Web3 | TonConnect UI React v2 |
| Virtualisation | react-window |
| HTTP | Axios |

---

## Quick Start

```bash
npm install
npm run dev        # http://localhost:3000
```

Backend `http://localhost:8000`da ishlayotgan bo'lishi kerak (Vite proxy orqali `/api` yo'naltiriladi).  
`window.Telegram` mavjud bo'lmaganda app avtomatik mock data ishlatadi.

---

## Arxitektura — Feature-Sliced Design

```
src/
├── app/                        ← App setup layer
│   ├── AppShell.tsx            ← Auth init + loading/error states
│   ├── providers.tsx           ← TonConnect + QueryClient + ErrorBoundary
│   └── router.tsx              ← Zustand-based lightweight router
│
├── features/                   ← Business domain features
│   ├── auth/
│   │   ├── api/authApi.ts      ← /auth/* endpoints
│   │   ├── store/authStore.ts  ← Zustand auth state
│   │   └── index.ts
│   ├── events/
│   │   ├── api/eventsApi.ts    ← /events/* endpoints
│   │   ├── components/         ← EventCard, EventList
│   │   ├── hooks/useEvents.ts  ← React Query hooks
│   │   ├── store/eventUiStore  ← Navigation UI state
│   │   └── index.ts
│   ├── leaderboard/
│   │   ├── api/leaderboardApi.ts
│   │   ├── components/         ← Leaderboard (virtualised), LeaderboardRow
│   │   ├── hooks/useLeaderboard.ts
│   │   └── index.ts
│   ├── tasks/
│   │   ├── api/tasksApi.ts
│   │   ├── components/         ← TaskCard, TaskList
│   │   ├── hooks/useTasks.ts
│   │   └── index.ts
│   ├── wallet/
│   │   ├── api/walletApi.ts
│   │   └── hooks/useWallet.ts
│   └── notifications/
│       └── store.ts            ← Global toast queue (Zustand)
│
├── shared/                     ← Cross-cutting reusable code
│   ├── api/
│   │   └── client.ts           ← Axios instance + ApiError class
│   ├── components/
│   │   ├── ui/                 ← Button, Card, Badge, Spinner, Progress, Stat…
│   │   ├── layout/             ← Header, Container
│   │   └── feedback/           ← ErrorBoundary, ToastContainer
│   ├── hooks/
│   │   └── useTelegram.ts      ← WebApp SDK init + mock fallback
│   ├── lib/
│   │   ├── queryClient.ts      ← React Query client instance
│   │   └── tonConnect.ts       ← TON Connect manifest URL
│   ├── types/index.ts          ← Domain types (mirrors backend schemas)
│   ├── constants/index.ts      ← Query keys, labels, durations
│   └── utils/index.ts          ← Formatters (cn, formatTon, displayName…)
│
└── pages/                      ← Thin page wrappers (entry points)
    ├── HomePage.tsx
    ├── EventDetailPage.tsx
    └── LeaderboardPage.tsx
```

---

## FSD Qoidalari

**Import yo'nalishi** (bir tomonlama, pastdan yuqoriga):
```
pages → features → shared
app   → features → shared
features → shared  (cross-feature import YO'Q)
```

**Har bir feature ichki tuzilmasi:**
```
feature/
├── api/          ← HTTP calls (apiClient ishlatadi)
├── components/   ← Feature-specific UI
├── hooks/        ← React Query hooks
├── store/        ← Zustand state (agar kerak bo'lsa)
└── index.ts      ← Public API (faqat shu orqali import)
```

---

## Navigation

`react-router` yo'q — `useEventUiStore` (Zustand) orqali boshqariladi:

```
selectedEventId == null        →  HomePage
selectedEventId != null
  eventPage == 'overview'      →  EventDetailPage (Overview tab)
  eventPage == 'tasks'         →  EventDetailPage (Tasks tab)
  eventPage == 'leaderboard'   →  LeaderboardPage
```

---

## Key Patterns

**Double-click guard** — join/verify tugmalari `mutation.isPending` paytida `disabled`.  
Backend ham `429` qaytaradi (Tarantool idempotency lock).

**Error mapping** — `ApiError(status, detail)`:
- `400/409` → "already joined/completed" toasti
- `403`     → `error.detail` matni toastda
- `429`     → "please wait" toasti

**Virtualised leaderboard** — `react-window FixedSizeList`.  
10 000+ ishtirokchi ham past telefonlarda lag yo'q.

**Axios interceptor** — barcha requestlarga `X-Telegram-Init-Data` header.

---

## Build

```bash
npm run build    # dist/ papkasiga
npm run preview  # dist/ ni lokali serve qilish
```

Bundle: ~218 KB gzip (TonConnect asosiy hissa).
