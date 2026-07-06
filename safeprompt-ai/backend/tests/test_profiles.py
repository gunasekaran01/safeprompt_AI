"""
Tests for SaaS Phase 2 profile routes (GET/PATCH /api/profiles/me) and
Phase 7's account deletion (DELETE /api/profiles/me), all in
app/api/routes/profiles.py.

Two things need faking beyond conftest.py's autouse fixtures:

  - app.api.deps.get_user_scoped_client, which normally opens a real,
    JWT-authenticated Supabase client for `profiles` table RLS — replaced
    here with a fresh FakeSupabaseClient (tests/fake_supabase.py), the
    same in-memory fake used for app.db.crud, so profile_crud.py's
    `.table("profiles")...` calls run in memory instead of over the
    network.
  - app.services.account_service.get_supabase_client, which normally
    returns the shared service-role client whose `.auth.admin` actually
    deletes the Supabase Auth user — replaced with a minimal fake that
    just records which user ids were "deleted", so tests can assert on
    it without a real admin API call.
"""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import AUTH_HEADERS, TEST_USER_EMAIL, TEST_USER_ID
from tests.fake_supabase import FakeSupabaseClient

client = TestClient(app)


@pytest.fixture(autouse=True)
def fake_user_scoped_client(monkeypatch):
    """Routes profile_crud's user-scoped queries to an in-memory fake instead of a real Supabase client."""
    fake_client = FakeSupabaseClient()
    monkeypatch.setattr("app.api.deps.get_user_scoped_client", lambda token: fake_client)
    return fake_client


class _FakeAdminAuth:
    def __init__(self):
        self.deleted_user_ids = []

    def delete_user(self, user_id):
        self.deleted_user_ids.append(user_id)


class _FakeAdminClient:
    def __init__(self):
        self.auth = SimpleNamespace(admin=_FakeAdminAuth())


@pytest.fixture
def fake_admin_client(monkeypatch):
    admin_client = _FakeAdminClient()
    monkeypatch.setattr("app.services.account_service.get_supabase_client", lambda: admin_client)
    return admin_client


def test_get_my_profile_requires_authentication():
    response = client.get("/api/profiles/me")
    assert response.status_code == 401


def test_get_my_profile_creates_and_returns_profile_on_first_access():
    response = client.get("/api/profiles/me", headers=AUTH_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == TEST_USER_ID
    assert body["email"] == TEST_USER_EMAIL
    assert body["name"] is None
    assert body["avatar_url"] is None


def test_get_my_profile_returns_the_same_profile_on_second_call():
    first = client.get("/api/profiles/me", headers=AUTH_HEADERS).json()
    second = client.get("/api/profiles/me", headers=AUTH_HEADERS).json()
    assert first["id"] == second["id"]
    assert first["created_at"] == second["created_at"]


def test_update_my_profile_requires_authentication():
    response = client.patch("/api/profiles/me", json={"name": "Ada"})
    assert response.status_code == 401


def test_update_my_profile_sets_name_and_avatar():
    client.get("/api/profiles/me", headers=AUTH_HEADERS)  # ensure the row exists first
    response = client.patch(
        "/api/profiles/me",
        headers=AUTH_HEADERS,
        json={"name": "Ada Lovelace", "avatar_url": "https://example.com/avatar.png"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Ada Lovelace"
    assert body["avatar_url"] == "https://example.com/avatar.png"


def test_update_my_profile_partial_update_leaves_other_fields_unchanged():
    client.get("/api/profiles/me", headers=AUTH_HEADERS)
    client.patch("/api/profiles/me", headers=AUTH_HEADERS, json={"name": "Ada"})

    response = client.patch(
        "/api/profiles/me", headers=AUTH_HEADERS, json={"avatar_url": "https://example.com/a.png"}
    )
    body = response.json()
    assert body["name"] == "Ada"
    assert body["avatar_url"] == "https://example.com/a.png"


def test_update_my_profile_works_even_if_profile_never_fetched_before():
    # No prior GET /api/profiles/me — update_my_profile must create it first.
    response = client.patch("/api/profiles/me", headers=AUTH_HEADERS, json={"name": "Grace"})
    assert response.status_code == 200
    assert response.json()["name"] == "Grace"


def test_update_my_profile_requires_at_least_one_field():
    client.get("/api/profiles/me", headers=AUTH_HEADERS)
    response = client.patch("/api/profiles/me", headers=AUTH_HEADERS, json={})
    assert response.status_code == 400


def test_delete_my_account_requires_authentication(fake_admin_client):
    response = client.delete("/api/profiles/me")
    assert response.status_code == 401
    assert fake_admin_client.auth.admin.deleted_user_ids == []


def test_delete_my_account_calls_admin_delete_and_returns_204(fake_admin_client):
    response = client.delete("/api/profiles/me", headers=AUTH_HEADERS)
    assert response.status_code == 204
    assert fake_admin_client.auth.admin.deleted_user_ids == [TEST_USER_ID]
