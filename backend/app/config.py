from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/prizerace"
    tarantool_host: str = "localhost"
    tarantool_port: int = 3301

    # Telegram
    telegram_bot_token: str
    telegram_webhook_secret: str

    # TON
    ton_network: str = "testnet"
    ton_api_key: str

    # App
    debug: bool = True
    secret_key: str = "your-secret-key-change-in-production"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
