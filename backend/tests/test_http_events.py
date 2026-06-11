"""
tests/test_http_events.py
──────────────────────────
HTTP integration tests for /api/v1/events endpoints.
Uses the `client` fixture (auth bypassed via X-Test-Telegram-Id).
"""
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from tests.conftest import auth_headers

BASE = "/api/v1/events"


def _future_event_body(days_ahead=7):
    now = datetime.utcnow()
    return {
        "title": "HTTP Test Sprint",
        "description": "test",
        "top_n_winners": 3,
        "total_prize_pool": "10.5",
        "start_date": now.isoformat(),
        "end_date": (now + timedelta(days=days_ahead)).isoformat(),
    }


class TestCreateEvent:

    def test_create_returns_201(self, client: TestClient):
        r = client.post(BASE + "/", json=_future_event_body(), headers=auth_headers("c_org1"))
        assert r.status_code == 201
        data = r.json()
        assert data["status"] == "DRAFT"
        assert data["organizer_id"] is not None

    def test_create_requires_auth(self, client: TestClient):
        r = client.post(BASE + "/", json=_future_event_body())
        assert r.status_code == 401

    def test_create_end_before_start_rejected(self, client: TestClient):
        now = datetime.utcnow()
        body = {
            "title": "Bad Sprint",
            "total_prize_pool": "5",
            "start_date": now.isoformat(),
            "end_date": (now - timedelta(hours=1)).isoformat(),
        }
        r = client.post(BASE + "/", json=body, headers=auth_headers("c_org2"))
        assert r.status_code == 422


class TestListEvents:

    def test_list_returns_200(self, client: TestClient):
        client.post(BASE + "/", json=_future_event_body(), headers=auth_headers("l_org1"))
        r = client.get(BASE + "/", headers=auth_headers("l_org1"))
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_filter_by_status(self, client: TestClient):
        client.post(BASE + "/", json=_future_event_body(), headers=auth_headers("l_org2"))
        r = client.get(BASE + "/?status=DRAFT", headers=auth_headers("l_org2"))
        assert r.status_code == 200
        for event in r.json():
            assert event["status"] == "DRAFT"

    def test_list_unknown_status_rejected(self, client: TestClient):
        r = client.get(BASE + "/?status=INVALID", headers=auth_headers("l_org3"))
        assert r.status_code == 422


class TestGetEvent:

    def test_get_existing(self, client: TestClient):
        created = client.post(BASE + "/", json=_future_event_body(),
                              headers=auth_headers("g_org1")).json()
        r = client.get(f"{BASE}/{created['id']}", headers=auth_headers("g_org1"))
        assert r.status_code == 200
        assert r.json()["id"] == created["id"]

    def test_get_nonexistent_returns_404(self, client: TestClient):
        r = client.get(f"{BASE}/999999", headers=auth_headers("g_org1"))
        assert r.status_code == 404


class TestUpdateEvent:

    def test_update_draft_event(self, client: TestClient):
        created = client.post(BASE + "/", json=_future_event_body(),
                              headers=auth_headers("u_org1")).json()
        r = client.put(
            f"{BASE}/{created['id']}",
            json={"title": "Updated Title"},
            headers=auth_headers("u_org1"),
        )
        assert r.status_code == 200
        assert r.json()["title"] == "Updated Title"

    def test_non_organiser_cannot_update(self, client: TestClient):
        created = client.post(BASE + "/", json=_future_event_body(),
                              headers=auth_headers("u_org2")).json()
        r = client.put(
            f"{BASE}/{created['id']}",
            json={"title": "Hacked"},
            headers=auth_headers("u_attacker"),
        )
        assert r.status_code == 403


class TestLockEvent:

    def test_lock_moves_to_pending_payment(self, client: TestClient):
        created = client.post(BASE + "/", json=_future_event_body(),
                              headers=auth_headers("lk_org1")).json()
        r = client.post(f"{BASE}/{created['id']}/lock", headers=auth_headers("lk_org1"))
        assert r.status_code == 200
        assert r.json()["status"] == "PENDING_PAYMENT"

    def test_cannot_update_after_lock(self, client: TestClient):
        created = client.post(BASE + "/", json=_future_event_body(),
                              headers=auth_headers("lk_org2")).json()
        client.post(f"{BASE}/{created['id']}/lock", headers=auth_headers("lk_org2"))
        r = client.put(
            f"{BASE}/{created['id']}",
            json={"title": "Too late"},
            headers=auth_headers("lk_org2"),
        )
        assert r.status_code == 400

    def test_non_organiser_cannot_lock(self, client: TestClient):
        created = client.post(BASE + "/", json=_future_event_body(),
                              headers=auth_headers("lk_org3")).json()
        r = client.post(f"{BASE}/{created['id']}/lock", headers=auth_headers("lk_attacker"))
        assert r.status_code == 403


class TestLeaderboard:

    def test_leaderboard_empty(self, client: TestClient):
        created = client.post(BASE + "/", json=_future_event_body(),
                              headers=auth_headers("lb_org1")).json()
        r = client.get(f"{BASE}/{created['id']}/leaderboard", headers=auth_headers("lb_org1"))
        assert r.status_code == 200
        assert r.json() == []

    def test_leaderboard_nonexistent_event(self, client: TestClient):
        r = client.get(f"{BASE}/999998/leaderboard", headers=auth_headers("lb_org2"))
        assert r.status_code == 404
