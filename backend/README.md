# PrizeRace Backend

FastAPI backend for PrizeRace Web3 Sprint Platform.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

### 3. Database Setup

Make sure PostgreSQL is running:

```bash
# Create database
createdb prizerace
```

### 4. Run Server

```bash
python -m uvicorn app.main:app --reload
```

Server will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
app/
├── main.py           # FastAPI app entry point
├── config.py         # Configuration settings
├── models.py         # SQLAlchemy models
├── schemas.py        # Pydantic schemas
├── database.py       # Database connections
├── middleware.py     # Custom middleware
└── routes/
    ├── auth.py       # Authentication endpoints
    ├── events.py     # Event/Sprint endpoints
    └── tasks.py      # Task endpoints
```

## Key Features

- ✅ PostgreSQL + Tarantool integration
- ✅ HMAC-SHA256 Telegram validation
- ✅ Idempotency locks for duplicate prevention
- ✅ Leaderboard system
- ✅ Task verification
- ✅ Anti-fraud measures
