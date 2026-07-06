"""
Account deletion — SaaS Phase 7.

Deleting a Supabase Auth user (via the GoTrue admin API, exposed through
supabase-py as `client.auth.admin.delete_user`) requires the
service-role key — this is the one operation in the app that must go
through app.db.supabase_client.get_supabase_client()'s service-role path
rather than a per-user scoped client, since no end user's own JWT can
ever be granted permission to delete their own auth.users row directly
(that would let anyone escalate into deleting arbitrary accounts if the
policy were ever misconfigured).

Deleting the auth.users row cascades to every table that references
public.profiles(id) with `on delete cascade` (profiles itself, plus
analyses/reports/settings — see backend/supabase/schema.sql), so this
one call is sufficient to fully remove the user's data. There is no
separate cleanup step needed here, and none should be added — adding
manual per-table deletes here would just be a second, easier-to-forget
place for that logic to drift out of sync with the schema.
"""

from app.db.supabase_client import get_supabase_client


def delete_account(user_id: str) -> None:
    """
    Permanently deletes a user's Supabase Auth account and, via
    cascading foreign keys, every row they own across profiles,
    analyses, reports, and settings. This cannot be undone.
    """
    client = get_supabase_client()
    client.auth.admin.delete_user(user_id)
