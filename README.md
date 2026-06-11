# PrizeRace

Web3 Sprint Platform — Telegram Mini App + TON blockchain.

Users compete in timed sprints by completing tasks to earn XP.  
Top participants win a TON prize pool distributed automatically via smart contract.

---

## Repository Layout

```
prize_race/
├── backend/          ← FastAPI + PostgreSQL + Tarantool
│   └── README.md     ← Backend setup, API docs, architecture
├── frontend/         ← React + TypeScript + Vite Telegram Mini App
│   └── README.md     ← Frontend setup, component guide
└── vercel.json       ← Vercel deployment config (frontend + API proxy)
```

---

## Quick Start (Full Stack)

### 1. Start infrastructure

```bash
cd backend
docker-compose up postgres tarantool -d
```

### 2. Start backend

```bash
cd backend
cp .env.example .env    # fill in TELEGRAM_BOT_TOKEN, TON_API_KEY, etc.
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 3. Start frontend

```bash
cd frontend
npm install
npm run dev             # http://localhost:3000
```

Open `http://localhost:3000` in a browser.  
In dev mode mock Telegram data is used automatically.

---

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.11 / FastAPI |
| Primary DB | PostgreSQL 15 |
| In-memory DB | Tarantool 2.11 (leaderboard + locks) |
| Migrations | Alembic |
| Frontend | React 18 / TypeScript / Vite |
| Styling | Tailwind CSS v4 |
| State | Zustand + TanStack Query |
| Web3 | TonConnect UI React |
| Auth | Telegram WebApp HMAC-SHA256 |
| Deploy | Vercel (frontend) + any VPS/cloud (backend) |

---

## Sprint Lifecycle

```
DRAFT ──► PENDING_PAYMENT ──► ACTIVE ──► FINISHED
  │              │                │           │
Create      Lock params      Deposit       end_date
& edit      (no edit)       verified      passed
```

---

## Security Highlights

- Telegram InitData validated server-side with correct HMAC spec
- `wallet_address` only writable via `/wallet/connect` (ownership proof required)
- Idempotency locks via Tarantool prevent race conditions and double-clicks
- PostgreSQL UNIQUE constraints as final database-level duplicate guard
- Monetary amounts stored as `NUMERIC(18,9)` — no floating-point drift
- Atomic SQL `UPDATE ... SET xp = xp + ?` prevents lost updates under concurrency

---

## Tests

```bash
cd backend
pytest tests/ -v     # 74 tests, 0 failures
```
