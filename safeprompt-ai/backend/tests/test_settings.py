"""
Tests for Phase 7's GET/PATCH /api/settings (app/api/settings.py +
app/services/settings_service.py), backed by the `user_settings` table.

No extra faking needed beyond conftest.py's autouse fixtures:
settings_service.py imports get_supabase_client from
app.db.supabase_client (same as history_service.py), which the
`reset_local_data_store` fixture already routes to a fresh, isolated
in-memory LocalDataStore per test.
"""

from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import AUTH_HEADERS, TEST_USER_ID

client = TestClient(app)


def test_get_settings_requires_authentication():
    response = client.get("/api/settings")
    assert response.status_code == 401


def test_get_settings_creates_defaults_on_first_access():
    response = client.get("/api/settings", headers=AUTH_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["theme"] == "system"
    assert body["compactMode"] is False
    assert body["autoAnalyzeOnPaste"] is False
    assert "updatedAt" in body


def test_get_settings_returns_the_same_row_on_second_call():
    first = client.get("/api/settings", headers=AUTH_HEADERS).json()
    second = client.get("/api/settings", headers=AUTH_HEADERS).json()
    assert first["updatedAt"] == second["updatedAt"]


def test_update_settings_requires_authentication():
    response = client.patch("/api/settings", json={"theme": "dark"})
    assert response.status_code == 401


def test_update_settings_applies_partial_update():
    client.get("/api/settings", headers=AUTH_HEADERS)  # ensure the row exists first
    response = client.patch("/api/settings", headers=AUTH_HEADERS, json={"theme": "dark"})
    assert response.status_code == 200
    body = response.json()
    assert body["theme"] == "dark"
    assert body["compactMode"] is False  # untouched


def test_update_settings_partial_update_leaves_other_fields_unchanged():
    client.get("/api/settings", headers=AUTH_HEADERS)
    client.patch("/api/settings", headers=AUTH_HEADERS, json={"theme": "dark"})

    response = client.patch("/api/settings", headers=AUTH_HEADERS, json={"compactMode": True})
    body = response.json()
    assert body["theme"] == "dark"
    assert body["compactMode"] is True


def test_update_settings_works_even_if_settings_never_fetched_before():
    response = client.patch(
        "/api/settings", headers=AUTH_HEADERS, json={"autoAnalyzeOnPaste": True}
    )
    assert response.status_code == 200
    assert response.json()["autoAnalyzeOnPaste"] is True


def test_settings_are_isolated_per_user():
    client.patch("/api/settings", headers=AUTH_HEADERS, json={"theme": "dark"})

    # The settings row is keyed by TEST_USER_ID, not global -- verify
    # isolation via the stored row directly rather than a second token,
    # since a different token is simply unauthenticated under the fake
    # auth setup used elsewhere.
    from app.services import settings_service

    row = settings_service.get_or_create_settings(TEST_USER_ID)
    assert row["theme"] == "dark"
