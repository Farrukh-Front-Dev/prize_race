"""
app/core/config.py
──────────────────
Type-safe settings via pydantic-settings.
All values are read from environment variables / .env file.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── PostgreSQL ────────────────────────────────────────────────────────
    database_url: str = "postgresql://user:password@localhost:5432/prizerace"
    db_pool_size: int = 20
    db_max_overflow: int = 40

    # ── Tarantool ─────────────────────────────────────────────────────────
    tarantool_host: str = "localhost"
    tarantool_port: int = 3301

    # ── Telegram ──────────────────────────────────────────────────────────
    telegram_bot_token: str
    telegram_webhook_secret: str

    # ── TON ───────────────────────────────────────────────────────────────
    ton_network: str = "testnet"          # testnet | mainnet
    ton_api_key: str
    ton_contract_address: str = ""

    # ── App ───────────────────────────────────────────────────────────────
    debug: bool = False
    secret_key: str
    api_v1_prefix: str = "/api/v1"

    # ── Anti-fraud ────────────────────────────────────────────────────────
    min_account_age_days: int = 30
    max_daily_referrals: int = 20

    # ── Background sync ───────────────────────────────────────────────────
    sync_interval_seconds: int = 5
    sync_batch_size: int = 100

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()
