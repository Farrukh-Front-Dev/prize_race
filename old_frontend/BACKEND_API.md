# PrizeRace — Backend API Reference (for Frontend)

This document describes the PrizeRace backend so the frontend can be built
against the **real API contract**. PrizeRace is a Telegram Mini App on the TON
blockchain: organizers create timed sprints with a TON prize pool, participants
complete tasks to earn XP, and the top N players win the pool.

---

## 1. Base URL & Conventions

| Item | Value |
|------|-------|
| Base path | `/api/v1` (frontend proxies `/api` to the backend) |
| Content-Type | `application/json` |
| Error shape | `{ "detail": "human readable message" }` |
| Date format | ISO 8601 strings (e.g. `2026-06-20T12:00:00Z`) |
| Money format | **string** (Decimal, 9 dp) — never a JS number |

### Authentication

- Every request **except `POST /auth/register`** must send the header:
  ```
  X-Telegram-Init-Data: <Telegram WebApp initData string>
  ```
- The backend validates it via HMAC-SHA256. The user is resolved from
  `request.state.telegram_id` — the frontend never sends `user_id` in the body
  or query.
- Missing/invalid header → **401** `{ "detail": "Missing X-Telegram-Init-Data header" }`
  or `"Invalid or expired Telegram InitData"`.
- In dev/browser mode the app sends mock initData (backend must run with `DEBUG=true`).

### Idempotency lock (important for UI)

- All `POST`/`PUT` on `/events`, `/tasks`, `/wallet` acquire an atomic lock keyed
  by `lock:{telegram_id}:{METHOD}:{path}` (TTL ~5s).
- If the same user fires the same mutation while one is in flight →
  **429** `{ "detail": "Request is already being processed, please wait" }`.
- **Frontend rule:** disable action buttons + show a spinner while a mutation is
  pending; on `429` show a "please wait" toast instead of erroring.

---

## 2. Data Models

### EventStatus (enum)
`DRAFT` → `PENDING_PAYMENT` → `ACTIVE` → `FINISHED`

### VerificationType (enum)
`manual` · `channel_subscription`

### User
```ts
{
  id: number
  telegram_id: string
  username: string | null
  first_name: string | null
  last_name: string | null
  wallet_address: string | null
  created_at: string   // ISO
  updated_at: string
}
```

### Event
```ts
{
  id: number
  organizer_id: number
  title: string
  description: string | null
  status: EventStatus
  top_n_winners: number          // 1..1000
  total_prize_pool: string       // Decimal as string, in TON
  start_date: string             // ISO
  end_date: string               // ISO
  tx_hash: string | null
  created_at: string
  updated_at: string
}
```

### Task
```ts
{
  id: number
  event_id: number
  title: string
  description: string | null
  xp_reward: number              // 1..10000
  verification_type: VerificationType
  required_channel: string | null  // required when type = channel_subscription
  created_at: string
}
```

### Participant
```ts
{
  id: number
  user_id: number
  event_id: number
  total_xp: number
  joined_at: string
}
```

### LeaderboardEntry
```ts
{
  rank: number
  user_id: number
  username: string | null
  total_xp: number
  wallet_address: string | null
}
```

### TaskCompletion
```ts
{
  id: number
  user_id: number
  task_id: number
  completed_at: string
  verified: boolean
}
```

---

## 3. Endpoints

### Auth

#### `POST /auth/register` — public, no auth header
Upsert user on first app open.
```jsonc
// Request (UserCreate)
{ "telegram_id": "100000001", "username": "devuser", "first_name": "Dev", "last_name": "User" }
// Response 200 → User
```

#### `GET /auth/me` → `User`
Authenticated profile.

#### `PUT /auth/me` → `User`
Body: `{ "username"?: string }` (wallet is NOT updatable here — use `/wallet/connect`).

---

### Events

#### `POST /events/` → 201 `Event`
Create a sprint (status starts as `DRAFT`). Caller becomes organizer.
```jsonc
// Request (EventCreate)
{
  "title": "Summer Sprint",
  "description": "Complete tasks, win TON",
  "top_n_winners": 10,          // 1..1000, default 10
  "total_prize_pool": "250.0",  // string, > 0
  "start_date": "2026-06-20T00:00:00Z",
  "end_date":   "2026-06-27T00:00:00Z"  // must be after start_date
}
```

#### `GET /events/?status=&skip=&limit=` → `Event[]`
List events. Optional `status` filter (e.g. `ACTIVE`), `skip` (≥0), `limit` (1..200, default 50).

#### `GET /events/{id}` → `Event`
404 if not found.

#### `PUT /events/{id}` → `Event`
Update — **organizer only, DRAFT status only**. Partial body (EventUpdate).
- 403 if not organizer · 400 if not DRAFT.

#### `POST /events/{id}/lock` → `Event`
`DRAFT → PENDING_PAYMENT`. Organizer only.
- 400 if not DRAFT · 403 if not organizer.

#### `POST /events/{id}/join` → 201 `Participant`
Join an **ACTIVE** event.
- 400 `"Event is not active"`
- 403 anti-fraud: `"Organiser cannot participate in their own event"`,
  `"Account too young — N day(s) until eligible"` (min 30 days)
- 409 `"Already joined this event"`
- 429 lock in flight

#### `GET /events/{id}/leaderboard?limit=&offset=` → `LeaderboardEntry[]`
Real-time leaderboard (from Tarantool, fast for 10k+ players).
`limit` 1..1000 (default 100), `offset` ≥0. Empty array if no participants.

#### `POST /events/{id}/finish` → `Event`
`ACTIVE → FINISHED`. Organizer only, **only after `end_date` passed**.
- 400 if not ACTIVE or end_date not reached · 403 if not organizer.

#### `GET /events/{id}/winners` → `LeaderboardEntry[]`
Final top-`top_n_winners` list (includes `wallet_address` for payouts).
**Only when status is FINISHED** (400 otherwise).

---

### Tasks

#### `POST /tasks/event/{event_id}` → 201 `Task`
Add a task — **organizer only, DRAFT status only**.
```jsonc
// Request (TaskCreate)
{
  "title": "Join our channel",
  "description": "Subscribe to stay updated",
  "xp_reward": 50,                        // 1..10000, default 10
  "verification_type": "channel_subscription",  // or "manual"
  "required_channel": "@prizerace"        // required if channel_subscription
}
```
- 403 if not organizer · 400 if not DRAFT.

#### `GET /tasks/event/{event_id}` → `Task[]`
All tasks for an event.

#### `GET /tasks/{task_id}` → `Task`

#### `POST /tasks/{task_id}/verify` → 201 `TaskCompletion`
Complete a task and award XP. **Event must be ACTIVE and user must be a participant.**
- 400 `"Event is not active"`
- 403 `"You are not a participant in this event"`, rate-limit
  `"Too many task completions in 60s — slow down"`, or for channel tasks
  `"Subscribe to @channel to complete this task"`
- 409 `"Task already completed"`
- 429 lock in flight

---

### Wallet (TON)

#### `POST /wallet/connect` → `User`
Connect & verify wallet ownership; stores `wallet_address`.
```jsonc
// Request (WalletConnectRequest)
{ "wallet_address": "EQ...", "signature": "...", "message": "..." }
// wallet_address: 48..64 chars
```
- 401 `"Wallet ownership verification failed"`.

#### `POST /wallet/deposit` → `{ status, event_id, event_status, tx_hash }`
Organizer deposits the prize pool → activates the event (`PENDING_PAYMENT → ACTIVE`).
```jsonc
// Request (DepositRequest)
{ "event_id": 1, "tx_hash": "<64..128 hex>", "amount": "250.0" }
```
- 400 wallet not connected / not PENDING_PAYMENT / on-chain verify failed
- 403 not organizer · 404 event not found · 409 tx_hash already used

#### `GET /wallet/balance` → `{ wallet_address, balance_ton, currency }`
- 400 if wallet not connected · 502 if TON network unreachable.

---

## 4. Sprint Lifecycle → UI mapping

```
DRAFT ──lock──► PENDING_PAYMENT ──deposit──► ACTIVE ──finish(after end)──► FINISHED
```

| Status | Organizer can | Participant sees |
|--------|---------------|------------------|
| DRAFT | edit event, add/edit tasks, lock | not listed (not joinable) |
| PENDING_PAYMENT | connect wallet, deposit | awaiting activation |
| ACTIVE | finish (after end_date) | **Join**, complete tasks, leaderboard |
| FINISHED | — | **Winners / podium**, final XP & payouts |

**Business rules surfaced in UI:**
- Organizer cannot join their own event → show "You are the organiser".
- Account younger than 30 days → 403 on join → warning toast.
- Tasks are completable only after joining and only while ACTIVE.
- All mutations are idempotent-locked → disable buttons + handle 429.

---

## 5. Error → Toast mapping (frontend convention)

| HTTP | Meaning | UI |
|------|---------|----|
| 400 / 409 | already joined / completed / wrong state | info toast, reflect completed state |
| 403 | anti-fraud / not participant / not organizer | warning toast with `detail` |
| 429 | mutation already in flight | warning toast "please wait" |
| 401 | bad/expired initData | re-init or error screen |
| 5xx / 502 | server / TON network | error toast |
