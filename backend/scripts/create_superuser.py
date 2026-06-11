"""
scripts/create_superuser.py
─────────────────────────────
Create or update a user by telegram_id.
Useful for setting up admin/test accounts without going through Mini App.

Usage:
    python scripts/create_superuser.py --telegram-id 123456789 --username admin
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal, init_db
from app.repositories.user_repository import UserRepository


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or update a PrizeRace user")
    parser.add_argument("--telegram-id", required=True, help="Telegram user ID")
    parser.add_argument("--username", default=None)
    parser.add_argument("--first-name", default=None)
    parser.add_argument("--wallet", default=None)
    args = parser.parse_args()

    init_db()
    db = SessionLocal()

    try:
        repo = UserRepository(db)
        user = repo.upsert(
            telegram_id=args.telegram_id,
            username=args.username,
            first_name=args.first_name,
        )
        if args.wallet:
            user = repo.set_wallet(user, args.wallet)
        print(f"✅ User id={user.id} telegram_id={user.telegram_id} username={user.username}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
