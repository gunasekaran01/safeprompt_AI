"""
Supabase client factory.

Provides a single, cached Supabase client used throughout the backend
(JWT validation now; database persistence once the analyses table and
related services are built). Credentials come from SUPABASE_URL and
SUPABASE_KEY (see core/config.py and .env.example).
"""

from functools import lru_cache

from supabase import Client, create_client

from app.core.config import get_settings
from app.db.local_store import LocalDataStore


class _LocalDataHybridClient:
    """
    Wraps a real Supabase client so `.auth` (session/JWT validation)
    still goes through the real Supabase project -- that only needs the
    anon/public key, never a secret -- while `.table()` calls are
    redirected to an in-memory LocalDataStore instead of Postgres. This
    is what lets the backend run without the Supabase service-role key.

    Every method the rest of the app calls on a "Supabase client" is
    either `.auth....` or `.table(...)`, so this thin wrapper is a
    drop-in replacement -- no other file needs to know which mode is
    active.
    """

    def __init__(self, real_client: Client, local_store: LocalDataStore):
        self._real_client = real_client
        self.auth = real_client.auth
        self._local_store = local_store

    def table(self, name: str):
        return self._local_store.table(name)


@lru_cache
def _get_local_data_store() -> LocalDataStore:
    return LocalDataStore()


@lru_cache
def get_supabase_client():
    """
    Returns a cached client instance, created once per process.

    Raises RuntimeError with a clear, actionable message if the project
    hasn't been configured yet, rather than failing with an opaque error
    deep inside the supabase-py library.

    When settings.USE_LOCAL_DATA_STORE is True (the default), the
    returned object uses the real Supabase project only for `.auth`
    (which works fine with the anon/public key) and an in-memory
    LocalDataStore for `.table()` -- so no Supabase *service role*
    secret is ever needed. Set USE_LOCAL_DATA_STORE=False in .env once
    you have a real service-role key and want data to persist in
    Supabase's Postgres tables instead.
    """
    settings = get_settings()
    if not settings.is_supabase_configured:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_KEY or SUPABASE_ANON_KEY must be set (see backend/.env.example) "
            "before the database or authentication can be used."
        )
    api_key = settings.SUPABASE_KEY or settings.SUPABASE_ANON_KEY
    real_client = create_client(settings.SUPABASE_URL, api_key)
    if settings.USE_LOCAL_DATA_STORE:
        return _LocalDataHybridClient(real_client, _get_local_data_store())
    return real_client


def get_user_scoped_client(access_token: str):
    """
    Returns a client authenticated as one specific end user, for routes
    that need per-user Row Level Security to be the actual enforcement
    boundary (app/db/profile_crud.py, app/db/admin_crud.py -- see
    app.api.deps.get_current_user_client, which wraps this).

    Mode-aware, matching get_supabase_client() above:
    - USE_LOCAL_DATA_STORE=True (the default): there is no real Postgres
      RLS to attach a JWT to -- .table() calls are served by the single
      shared in-memory LocalDataStore regardless of which client asks --
      so this just returns the same cached get_supabase_client(). Every
      caller (profile_crud.py, admin_crud.py) already filters explicitly
      by user_id/id in Python, which is what actually enforces isolation
      in this mode; admin routes deliberately skip that filter to see
      everyone, which is safe because they're gated by
      app.api.deps.require_admin at the route layer instead.
    - USE_LOCAL_DATA_STORE=False (real Supabase Postgres): creates a
      fresh, uncached client with the given user's own JWT attached via
      `.postgrest.auth()`, so RLS policies using auth.uid() (see
      backend/supabase/schema.sql) are the real, Postgres-enforced
      boundary -- not just an application-level filter.
    """
    settings = get_settings()
    if not settings.is_supabase_configured:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_KEY must be set (see backend/.env.example) "
            "before a user-scoped client can be created."
        )
    if settings.USE_LOCAL_DATA_STORE:
        return get_supabase_client()
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    client.postgrest.auth(access_token)
    return client
