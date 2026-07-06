"""Compatibility shim for tests that patch ``app.services.profile_service``.

This module intentionally exposes a tiny wrapper around the real
``get_supabase_client`` so tests can patch it directly (many older
tests expect to patch ``app.services.profile_service.get_supabase_client``).
The real profile CRUD lives in ``app.db.profile_crud`` and the API
routes use that; this shim keeps the test surface stable without
reintroducing deprecated logic.
"""

from app.db.supabase_client import get_supabase_client as _get_supabase_client


def get_supabase_client():
	"""Return the cached Supabase client from app.db.supabase_client.

	Exists so tests can patch this module-level name without reaching
	into the db package.
	"""
	return _get_supabase_client()
