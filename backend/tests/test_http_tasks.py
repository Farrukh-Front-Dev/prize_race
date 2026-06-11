"""
tests/test_http_tasks.py
─────────────────────────
HTTP integration tests for /api/v1/tasks endpoints.
"""
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from tests.conftest import auth_headers

EVENTS = "/api/v1/events"
TASKS = "/api/v1/tasks"
AUTH = "/api/v1/auth"


def _register(client, tid):
    client.post(AUTH + "/register", json={"telegram_id": tid})
    return tid


def _create_event(client, tid):
    now = datetime.utcnow()
    return client.post(EVENTS + "/", json={
        "title": "Sprint",
        "total_prize_pool": "5",
        "start_date": now.isoformat(),
        "end_date": (now + timedelta(days=7)).isoformat(),
    }, headers=auth_headers(tid)).json()


def _add_task(client, event_id, org_tid):
    return client.post(
        f"{TASKS}/event/{event_id}",
        json={"title": "Do task", "xp_reward": 50},
        headers=auth_headers(org_tid),
    )


class TestCreateTask:

    def test_organiser_creates_task(self, client: TestClient):
        tid = _register(client, "ct_org1")
        event = _create_event(client, tid)
        r = _add_task(client, event["id"], tid)
        assert r.status_code == 201
        assert r.json()["xp_reward"] == 50

    def test_non_organiser_cannot_create(self, client: TestClient):
        tid = _register(client, "ct_org2")
        event = _create_event(client, tid)
        r = _add_task(client, event["id"], "ct_attacker")
        assert r.status_code == 403

    def test_cannot_add_task_after_lock(self, client: TestClient):
        tid = _register(client, "ct_org3")
        event = _create_event(client, tid)
        client.post(f"{EVENTS}/{event['id']}/lock", headers=auth_headers(tid))
        r = _add_task(client, event["id"], tid)
        assert r.status_code == 400

    def test_invalid_xp_rejected(self, client: TestClient):
        tid = _register(client, "ct_org4")
        event = _create_event(client, tid)
        r = client.post(
            f"{TASKS}/event/{event['id']}",
            json={"title": "Bad XP", "xp_reward": 0},
            headers=auth_headers(tid),
        )
        assert r.status_code == 422


class TestListTasks:

    def test_list_tasks_for_event(self, client: TestClient):
        tid = _register(client, "lt_org1")
        event = _create_event(client, tid)
        _add_task(client, event["id"], tid)
        _add_task(client, event["id"], tid)

        r = client.get(f"{TASKS}/event/{event['id']}", headers=auth_headers(tid))
        assert r.status_code == 200
        assert len(r.json()) >= 2

    def test_list_tasks_nonexistent_event(self, client: TestClient):
        r = client.get(f"{TASKS}/event/999999", headers=auth_headers("lt_any"))
        assert r.status_code == 404


class TestGetTask:

    def test_get_task(self, client: TestClient):
        tid = _register(client, "gt_org1")
        event = _create_event(client, tid)
        task = _add_task(client, event["id"], tid).json()

        r = client.get(f"{TASKS}/{task['id']}", headers=auth_headers(tid))
        assert r.status_code == 200
        assert r.json()["id"] == task["id"]

    def test_get_nonexistent_task(self, client: TestClient):
        r = client.get(f"{TASKS}/999999", headers=auth_headers("gt_any"))
        assert r.status_code == 404


class TestVerifyTask:
    """
    Verify task requires the event to be ACTIVE.
    Since we can't hit the blockchain in tests (TONService mocked via
    Tarantool mock), we test the guard conditions only.
    """

    def test_verify_on_draft_event_rejected(self, client: TestClient):
        tid = _register(client, "vt_org1")
        event = _create_event(client, tid)
        task = _add_task(client, event["id"], tid).json()

        # Not a participant, event is DRAFT — should get 400 (not active)
        r = client.post(f"{TASKS}/{task['id']}/verify", headers=auth_headers("vt_usr1"))
        assert r.status_code == 400
        assert "not active" in r.json()["detail"].lower()

    def test_verify_without_participation_rejected(self, client: TestClient):
        """
        Even if event were ACTIVE, non-participant should be blocked.
        We test the participant guard by making event ACTIVE-like via
        repository directly — tested at service level in test_participants.py.
        """
        pass  # covered by test_participants.py::TestAntiFraudJoin
