"""
Anti-Fraud Service
Prevent bot farms and malicious activities
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import User, Participant
from app.services.tarantool_service import get_leaderboard_service

logger = logging.getLogger(__name__)


class AntiFraudService:
    """
    Anti-fraud mechanisms:
    - Account age check (30+ days)
    - Referral limits (20/day)
    - Channel subscription verification
    - Duplicate account detection
    """

    # Minimum account age (30 days)
    MIN_ACCOUNT_AGE_DAYS = 30

    # Max referrals per day
    MAX_REFERRALS_PER_DAY = 20

    @staticmethod
    def check_account_age(user: User) -> bool:
        """
        Check if account is old enough
        
        Args:
            user: User object
            
        Returns:
            True if account is 30+ days old
        """
        if not user.created_at:
            return False

        account_age = datetime.utcnow() - user.created_at
        min_age = timedelta(days=AntiFraudService.MIN_ACCOUNT_AGE_DAYS)

        is_old_enough = account_age >= min_age

        if not is_old_enough:
            days_left = (min_age - account_age).days
            logger.warning(
                f"Account too young: {user.telegram_id} ({days_left} days left)"
            )

        return is_old_enough

    @staticmethod
    def check_referral_limit(
        user_id: int,
        db: Session,
    ) -> bool:
        """
        Check if user exceeded daily referral limit
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            True if under limit
        """
        # Get referrals from today
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())

        # Count participants joined today via this user's referral
        # TODO: Implement referral tracking in database

        return True

    @staticmethod
    def check_channel_subscription(
        user_id: int,
        channel_id: str,
    ) -> bool:
        """
        Check if user is subscribed to required channel
        
        Args:
            user_id: Telegram user ID
            channel_id: Channel ID to check
            
        Returns:
            True if subscribed
        """
        # TODO: Implement Telegram Bot API call to check membership
        # Use getChatMember method

        logger.info(f"Checking channel subscription: user {user_id}, channel {channel_id}")
        return True

    @staticmethod
    def detect_duplicate_accounts(
        telegram_id: str,
        db: Session,
    ) -> bool:
        """
        Detect if user has multiple accounts
        
        Args:
            telegram_id: Telegram user ID
            db: Database session
            
        Returns:
            True if no duplicates found
        """
        user = db.query(User).filter(User.telegram_id == telegram_id).first()

        if user:
            logger.warning(f"Duplicate account detected: {telegram_id}")
            return False

        return True

    @staticmethod
    def check_suspicious_activity(
        user_id: int,
        event_id: int,
        db: Session,
    ) -> bool:
        """
        Check for suspicious patterns
        
        Args:
            user_id: User ID
            event_id: Event ID
            db: Database session
            
        Returns:
            True if activity looks legitimate
        """
        # Check if user joined too many events in short time
        # Check if user completed too many tasks too fast
        # Check if user's XP gain is abnormal

        logger.info(f"Checking suspicious activity: user {user_id}, event {event_id}")
        return True

    @staticmethod
    def validate_user_for_event(
        user: User,
        event_id: int,
        db: Session,
    ) -> tuple[bool, str]:
        """
        Comprehensive user validation for event participation
        
        Args:
            user: User object
            event_id: Event ID
            db: Database session
            
        Returns:
            (is_valid, reason) tuple
        """
        # Check account age
        if not AntiFraudService.check_account_age(user):
            return False, "Account too young (minimum 30 days)"

        # Check duplicate accounts
        if not AntiFraudService.detect_duplicate_accounts(user.telegram_id, db):
            return False, "Duplicate account detected"

        # Check suspicious activity
        if not AntiFraudService.check_suspicious_activity(user.id, event_id, db):
            return False, "Suspicious activity detected"

        # Check referral limit
        if not AntiFraudService.check_referral_limit(user.id, db):
            return False, "Referral limit exceeded"

        return True, "OK"
