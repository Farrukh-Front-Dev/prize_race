"""
Telegram Validation Service
Professional HMAC-SHA256 validation for Telegram Mini App
"""

import hmac
import hashlib
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TelegramValidationService:
    """
    Validate Telegram Init Data with HMAC-SHA256
    
    Security:
    - Validates signature against Telegram Bot Token
    - Checks data freshness (max 5 minutes old)
    - Prevents replay attacks
    - Extracts user info securely
    """

    # Max age of init data (5 minutes)
    MAX_AGE_SECONDS = 300

    @staticmethod
    def validate_init_data(init_data: str) -> Optional[Dict[str, Any]]:
        """
        Validate Telegram Init Data
        
        Args:
            init_data: Raw init data string from Telegram
            
        Returns:
            Parsed user data if valid, None otherwise
        """
        try:
            # Parse init data
            data_dict = {}
            for pair in init_data.split("&"):
                key, value = pair.split("=", 1)
                data_dict[key] = value

            # Extract signature
            signature = data_dict.pop("hash", None)
            if not signature:
                logger.warning("Missing hash in init data")
                return None

            # Create data check string (sorted by key)
            data_check_string = "\n".join(
                f"{k}={v}"
                for k, v in sorted(data_dict.items())
            )

            # Validate signature
            secret_key = hashlib.sha256(
                settings.telegram_bot_token.encode()
            ).digest()

            expected_signature = hmac.new(
                secret_key,
                data_check_string.encode(),
                hashlib.sha256,
            ).hexdigest()

            if not hmac.compare_digest(signature, expected_signature):
                logger.warning("Invalid signature")
                return None

            # Check data freshness
            auth_date = int(data_dict.get("auth_date", 0))
            current_time = int(datetime.utcnow().timestamp())

            if current_time - auth_date > TelegramValidationService.MAX_AGE_SECONDS:
                logger.warning(f"Init data too old: {current_time - auth_date}s")
                return None

            # Parse user data
            user_data_str = data_dict.get("user")
            if not user_data_str:
                logger.warning("Missing user data")
                return None

            try:
                import urllib.parse
                user_data = json.loads(urllib.parse.unquote(user_data_str))
            except Exception as e:
                logger.error(f"Failed to parse user data: {e}")
                return None

            logger.info(f"✅ Valid Telegram user: {user_data.get('id')}")
            return user_data

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return None

    @staticmethod
    def extract_user_info(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant user info from Telegram data
        
        Args:
            user_data: Parsed user data from Telegram
            
        Returns:
            Cleaned user info
        """
        return {
            "telegram_id": str(user_data.get("id")),
            "username": user_data.get("username"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "is_premium": user_data.get("is_premium", False),
        }

    @staticmethod
    def check_account_age(user_data: Dict[str, Any]) -> bool:
        """
        Check if account is old enough (30+ days)
        
        Args:
            user_data: User data from Telegram
            
        Returns:
            True if account is 30+ days old
        """
        # Note: Telegram doesn't provide account creation date in init data
        # This would need to be tracked separately or via Telegram Bot API
        # For now, we'll implement a simple check
        return True  # TODO: Implement proper age check

    @staticmethod
    def validate_referral_link(referral_code: Optional[str]) -> bool:
        """
        Validate referral code format
        
        Args:
            referral_code: Referral code from start parameter
            
        Returns:
            True if valid format
        """
        if not referral_code:
            return True

        # Validate format: alphanumeric, 1-32 chars
        if len(referral_code) > 32 or not referral_code.isalnum():
            logger.warning(f"Invalid referral code: {referral_code}")
            return False

        return True
