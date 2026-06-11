"""
scripts/check_health.py
────────────────────────
Lightweight health check for PostgreSQL and Tarantool connections.
Useful in CI/CD and deployment smoke tests.

Usage:
    python scripts/check_health.py
Exit code 0 = healthy, 1 = any failure.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def check_postgres() -> bool:
    try:
        from app.core.database import engine
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        print("✅ PostgreSQL: connected")
        return True
    except Exception as exc:
        print(f"❌ PostgreSQL: {exc}")
        return False


def check_tarantool() -> bool:
    try:
        from app.core.database import get_tarantool
        conn = get_tarantool()
        if conn is None:
            print("❌ Tarantool: no connection")
            return False
        conn.ping()
        print("✅ Tarantool: connected")
        return True
    except Exception as exc:
        print(f"❌ Tarantool: {exc}")
        return False


def main() -> None:
    ok = all([check_postgres(), check_tarantool()])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
