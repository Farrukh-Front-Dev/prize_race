# PrizeRace Backend

Web3 Sprint Platform — Telegram Mini App + TON blockchain.

## Stack

| Layer | Tech |
|---|---|
| Framework | FastAPI 0.104 + Python 3.11 |
| Primary DB | PostgreSQL 15 (SQLAlchemy 2.0) |
| In-memory DB | Tarantool 2.11 (leaderboard + idempotency locks) |
| Migrations | Alembic 1.13 |
| Auth | Telegram Mini App InitData (HMAC-SHA256) |
| Blockchain | TON via TON Center HTTP API |
| Tests | pytest + SQLite :memory: |

---

## Project Structure

```
backend/
├── app/
│   ├── core/               # config, database, security, middleware, exceptions, deps
│   ├── models/             # SQLAlchemy ORM (one file per model)
│   ├── schemas/            # Pydantic v2 (one file per domain)
│   ├── repositories/       # DB query layer (decoupled from services)
│   ├── services/           # Business logic (anti_fraud, leaderboard, ton, channel, sync)
│   ├── api/v1/             # Versioned HTTP routes + router assembler
│   └── main.py             # App factory + lifespan
├── migrations/             # Alembic env + versions
├── tests/                  # pytest (74 tests, 100% pass)
├── scripts/                # seed_dev_data.py, create_superuser.py
├── tarantool/init.lua      # Tarantool instance config
├── Dockerfile              # Multi-stage build
├── docker-compose.yml      # api + postgres + tarantool
└── pyproject.toml          # deps, ruff, mypy, pytest config
```

---

## Quick Start (Docker)

```bash
cp .env.example .env
# Edit .env — set TELEGRAM_BOT_TOKEN, TON_API_KEY, TON_CONTRACT_ADDRESS, SECRET_KEY

docker-compose up --build
```

API will be available at `http://localhost:8000`.  
Swagger UI (dev mode): `http://localhost:8000/docs`

---

## Local Development

```bash
# 1. Create virtualenv
python -m venv .venv && source .venv/bin/activate

# 2. Install dependencies
pip install -e ".[dev]"

# 3. Set up .env
cp .env.example .env   # then edit values

# 4. Run PostgreSQL + Tarantool (Docker)
docker-compose up postgres tarantool -d

# 5. Apply migrations
alembic upgrade head

# 6. Seed dev data (optional)
python scripts/seed_dev_data.py

# 7. Start API
uvicorn app.main:app --reload --port 8000
```

---

## Running Tests

```bash
pytest tests/ -v
```

Tests use **SQLite :memory:** — no Postgres/Tarantool needed.  
Tarantool is mocked globally via `unittest.mock.patch`.

---

## API Overview

All endpoints are prefixed with `/api/v1`.  
Authentication: `X-Telegram-Init-Data: <initData>` header on all non-public endpoints.

### Auth
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | ❌ public | Upsert user by telegram_id |
| GET | `/auth/me` | ✅ | Get current user profile |
| PUT | `/auth/me` | ✅ | Update username |

### Events (Sprint lifecycle)
| Method | Path | Description |
|---|---|---|
| POST | `/events/` | Create event (DRAFT) |
| GET | `/events/` | List events (filter by status) |
| GET | `/events/{id}` | Get event details |
| PUT | `/events/{id}` | Update event (DRAFT only) |
| POST | `/events/{id}/lock` | Lock → PENDING_PAYMENT |
| POST | `/events/{id}/finish` | Finish → FINISHED (after end_date) |
| GET | `/events/{id}/leaderboard` | Real-time XP ranking (Tarantool) |
| GET | `/events/{id}/winners` | Final top-N (FINISHED only) |

### Tasks
| Method | Path | Description |
|---|---|---|
| POST | `/tasks/event/{event_id}` | Create task (organiser, DRAFT) |
| GET | `/tasks/event/{event_id}` | List tasks for event |
| GET | `/tasks/{id}` | Get task details |
| POST | `/tasks/{id}/verify` | Complete task + award XP |

### Wallet
| Method | Path | Description |
|---|---|---|
| POST | `/wallet/connect` | Connect TON wallet (ownership check) |
| POST | `/wallet/deposit` | Validate deposit → activates event |
| GET | `/wallet/balance` | Get wallet balance |

---

## Sprint Lifecycle

```
DRAFT ──► PENDING_PAYMENT ──► ACTIVE ──► FINISHED
  │              │                │           │
Create      Lock params      Deposit       end_date
& edit      (no edit)       verified      passed
```

---

## Security Notes

- Telegram InitData validated with HMAC-SHA256 per official spec
- `X-Test-Telegram-Id` header bypass works **only when `DEBUG=true`**
- `wallet_address` is only writable via `POST /wallet/connect` (ownership verified)
- Idempotency locks via Tarantool prevent race conditions on mutations
- PostgreSQL UNIQUE constraints are the final duplicate guard at DB level
- `total_prize_pool` stored as `NUMERIC(18,9)` — no floating-point errors
- Multi-worker safe: XP sync uses atomic SQL `UPDATE ... SET xp = xp + ?`

---

## Environment Variables

See `.env.example` for full reference.

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | ✅ | — | PostgreSQL connection string |
| `TELEGRAM_BOT_TOKEN` | ✅ | — | Used for HMAC key derivation |
| `TON_API_KEY` | ✅ | — | TON Center API key |
| `TON_CONTRACT_ADDRESS` | ✅ | `""` | Smart contract address |
| `SECRET_KEY` | ✅ | — | App secret (future JWT use) |
| `DEBUG` | — | `false` | Enables /docs, test bypass |
| `MIN_ACCOUNT_AGE_DAYS` | — | `30` | Anti-fraud account age |
| `SYNC_INTERVAL_SECONDS` | — | `5` | Tarantool→PG sync interval |

---

## Known TODOs (production before go-live)

1. **TON wallet ownership** — replace balance-check stub with real `ed25519` TonConnect proof
2. **Prize distribution endpoint** — trigger smart contract `Distribute` call after event finishes
3. **Event auto-finish** — background scheduler (APScheduler/Celery) to finish events at `end_date`
4. **Referral system** — `max_daily_referrals` config exists, implementation needed
5. **`telegram_created_at` population** — store Telegram account join date for accurate age checks
