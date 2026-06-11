"""
tests/test_http_auth.py
────────────────────────
HTTP integration tests for /api/v1/auth endpoints.
"""
import pytest
from fastapi.testclient import TestClient

from tests.conftest import auth_headers

BASE = "/api/v1/auth"


class TestRegister:

    def test_register_creates_user(self, client: TestClient):
        r = client.post(BASE + "/register", json={
            "telegram_id": "reg_001",
            "username": "alice",
            "first_name": "Alice",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["telegram_id"] == "reg_001"
        assert data["username"] == "alice"
        assert "id" in data

    def test_register_is_public_no_auth_header_needed(self, client: TestClient):
        """Register must work without X-Telegram-Init-Data or X-Test-Telegram-Id."""
        r = client.post(BASE + "/register", json={"telegram_id": "reg_public_001"})
        assert r.status_code == 200

    def test_register_upsert_updates_username(self, client: TestClient):
        client.post(BASE + "/register", json={"telegram_id": "reg_002", "username": "old"})
        r = client.post(BASE + "/register", json={"telegram_id": "reg_002", "username": "new"})
        assert r.status_code == 200
        assert r.json()["username"] == "new"

    def test_register_invalid_body_rejected(self, client: TestClient):
        r = client.post(BASE + "/register", json={})  # missing telegram_id
        assert r.status_code == 422

    def test_register_telegram_id_too_long(self, client: TestClient):
        r = client.post(BASE + "/register", json={"telegram_id": "x" * 51})
        assert r.status_code == 422


class TestGetMe:

    def test_get_me_authenticated(self, client: TestClient):
        # First register
        client.post(BASE + "/register", json={"telegram_id": "me_001", "username": "bob"})
        r = client.get(BASE + "/me", headers=auth_headers("me_001"))
        assert r.status_code == 200
        assert r.json()["telegram_id"] == "me_001"

    def test_get_me_unauthenticated(self, client: TestClient):
        r = client.get(BASE + "/me")
        assert r.status_code == 401

    def test_get_me_auto_registers_on_first_visit(self, client: TestClient):
        """
        If a user passes auth but never called /register,
        get_current_user dependency auto-creates them.
        """
        r = client.get(BASE + "/me", headers=auth_headers("me_auto_001"))
        assert r.status_code == 200
        assert r.json()["telegram_id"] == "me_auto_001"


class TestUpdateMe:

    def test_update_username(self, client: TestClient):
        client.post(BASE + "/register", json={"telegram_id": "upd_001", "username": "before"})
        r = client.put(
            BASE + "/me",
            json={"username": "after"},
            headers=auth_headers("upd_001"),
        )
        assert r.status_code == 200
        assert r.json()["username"] == "after"

    def test_wallet_not_updatable_via_put_me(self, client: TestClient):
        """
        wallet_address must NOT be writable via PUT /auth/me —
        use PUT /wallet/connect which verifies ownership.
        """
        client.post(BASE + "/register", json={"telegram_id": "upd_sec_001"})
        r = client.put(
            BASE + "/me",
            json={"wallet_address": "EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"},
            headers=auth_headers("upd_sec_001"),
        )
        # Schema no longer accepts wallet_address — should be ignored or 422
        # The field is removed from UserUpdate so Pydantic ignores extra fields
        data = r.json()
        # wallet_address should remain None (not updated)
        assert data.get("wallet_address") is None
