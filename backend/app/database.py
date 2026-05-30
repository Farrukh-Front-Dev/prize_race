from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import get_settings
from app.models import Base
import tarantool

settings = get_settings()

# PostgreSQL
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)


# Tarantool Connection
class TarantoolClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = tarantool.connect(
                settings.tarantool_host,
                settings.tarantool_port,
            )
        return cls._instance

    def get_connection(self):
        return self.connection


def get_tarantool() -> tarantool.Connection:
    client = TarantoolClient()
    return client.get_connection()
