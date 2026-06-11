"""
app/repositories/user_repository.py
─────────────────────────────────────
All DB queries related to the User model.
"""
from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):

    def __init__(self, db: Session) -> None:
        super().__init__(User, db)

    # ── Lookups ───────────────────────────────────────────────────────────

    def get_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.telegram_id == telegram_id)
            .first()
        )

    def get_many_by_ids(self, ids: List[int]) -> List[User]:
        if not ids:
            return []
        return self.db.query(User).filter(User.id.in_(ids)).all()

    # ── Upsert ────────────────────────────────────────────────────────────

    def upsert(
        self,
        telegram_id: str,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> User:
        """
        Insert new user or update mutable fields on the existing one.
        Returns the (possibly updated) user.
        """
        user = self.get_by_telegram_id(telegram_id)
        if user:
            changed = False
            for field, value in [
                ("username", username),
                ("first_name", first_name),
                ("last_name", last_name),
            ]:
                if value is not None and getattr(user, field) != value:
                    setattr(user, field, value)
                    changed = True
            if changed:
                return self.update(user)
            return user

        try:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            return self.create(user)
        except IntegrityError:
            self.db.rollback()
            # Race condition: parallel request created the user first
            return self.get_by_telegram_id(telegram_id)  # type: ignore[return-value]

    # ── Mutations ─────────────────────────────────────────────────────────

    def set_wallet(self, user: User, wallet_address: str) -> User:
        user.wallet_address = wallet_address
        return self.update(user)
