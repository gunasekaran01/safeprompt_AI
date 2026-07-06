"""
Pytest configuration for the backend test suite.

Forces ENABLE_ML_DETECTORS=False for all tests by setting the environment
variable before any test module imports app.main (and therefore
app.core.config.get_settings(), which is lru_cache'd). This keeps the
suite fast and fully offline: it exercises the regex/keyword fallback
paths in the Milestone 7/8 detectors rather than downloading and running
sentence-transformers/Detoxify models.

Database: this backend is Supabase-only. Rather than hitting a real
Supabase project, every test monkeypatches
`app.db.crud.get_supabase_client` with a fresh `FakeSupabaseClient`
(tests/fake_supabase.py) — an in-memory stand-in for `supabase.Client`
that implements enough of the PostgREST query-builder surface
(`.table().select()/.insert()/.delete()`, `.eq()`, `.ilike()`, `.order()`,
`.range()`, `.limit()`, `.execute()`) for app/db/crud.py to run against
unmodified. This keeps the suite fast, fully offline, and free of any
dependency on real SUPABASE_URL / SUPABASE_ANON_KEY /
SUPABASE_SERVICE_ROLE_KEY credentials — and gives every test a clean,
isolated table (no leakage between tests, no shared state, no cleanup
step needed).
"""

import os

os.environ.setdefault("ENABLE_ML_DETECTORS", "False")
# Dummy but well-formed values so Settings validation never fails in
# tests — the fake client below means these are never actually used to
# make a network call.
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "test-anon-key")

from types import SimpleNamespace

import pytest  # noqa: E402

from tests.fake_supabase import FakeSupabaseClient  # noqa: E402

TEST_AUTH_TOKEN = "test-user-token"
TEST_USER_ID = "11111111-1111-1111-1111-111111111111"
TEST_USER_EMAIL = "test-user@example.com"
AUTH_HEADERS = {"Authorization": "Bearer " + TEST_AUTH_TOKEN}


@pytest.fixture(autouse=True)
def fake_supabase(monkeypatch):
    """
    Replaces app.db.crud.get_supabase_client with a fresh in-memory fake
    for every test. Autouse so no test needs to remember to request it —
    persistence tests can use `app.db.crud` directly and API tests can use
    a `TestClient` normally, and both transparently hit the fake instead
    of a real Supabase project.
    """
    fake_client = FakeSupabaseClient()
    monkeypatch.setattr("app.db.crud.get_supabase_client", lambda: fake_client)
    return fake_client


class _FakeAuth:
    """Stands in for `supabase.Client.auth`, faking only `get_user`."""

    def get_user(self, token):
        if token == TEST_AUTH_TOKEN:
            user = SimpleNamespace(id=TEST_USER_ID, email=TEST_USER_EMAIL)
            return SimpleNamespace(user=user)
        return SimpleNamespace(user=None)


class _FakeAuthClient:
    def __init__(self):
        self.auth = _FakeAuth()


@pytest.fixture(autouse=True)
def fake_auth(monkeypatch):
    """
    Patches the Supabase client app.core.security.get_current_user validates
    tokens against (that's where the auth resolution actually lives, even
    though app.api.deps.get_current_user is the name routes depend on), so
    a request bearing AUTH_HEADERS is treated as an authenticated request
    from TEST_USER_ID, without needing a real Supabase Auth server. Autouse
    + conftest-level so every test file's TestClient can just send
    AUTH_HEADERS and get a valid session for free. test_auth.py, which
    specifically exercises authentication *failure* modes, layers its own
    more detailed fake auth client on top of this — its module-level
    autouse fixture runs after this conftest-level one, so its
    tokens/behaviors still take effect there.
    """
    monkeypatch.setattr("app.core.security.get_supabase_client", lambda: _FakeAuthClient())
