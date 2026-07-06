# Supabase setup

This backend persists every analysis to a Supabase (hosted Postgres) project
via `supabase-py`. Follow these steps once per environment (local dev, CI,
production).

## 1. Create a Supabase project

1. Go to [supabase.com](https://supabase.com) and create a new project (or
   reuse an existing one).
2. Wait for provisioning to finish.

## 2. Run the schema

1. In the Supabase Dashboard, open **SQL Editor -> New Query**.
2. Paste the contents of `schema.sql` (this directory) and click **Run**.
3. Confirm the `analyses` table now appears under **Table Editor**.

`schema.sql` is idempotent — safe to re-run any time you pull down a newer
version of this file (e.g. after adding a column), without dropping existing
data.

## 3. Get your API credentials

In **Project Settings -> API**:

- **Project URL** -> `SUPABASE_URL` (bare URL, no trailing `/rest/v1/`)
- **anon / public key** (under "Project API keys") -> `SUPABASE_ANON_KEY`

> This project intentionally does **not** use the `service_role` key —
> anywhere. The FastAPI backend authenticates to Supabase with the anon key
> only. Because the anon key normally has very limited default access,
> `schema.sql` grants the `anon` Postgres role explicit read/write policies
> on every table via Row Level Security — RLS is the entire access-control
> layer here, not a backstop. This is a reasonable trade-off for a
> single-tenant/dev project with no per-user auth yet, but if you add
> authentication later, tighten those `for all ... using (true)` policies to
> scope by an owner column instead of leaving this file as-is.

## 4. Configure the backend

```bash
cd backend
cp .env.example .env
```

Edit `.env` and fill in:

```env
SUPABASE_URL=https://<your-project-ref>.supabase.co
SUPABASE_ANON_KEY=<your-anon-key>
```

## 5. Install dependencies and run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Verify with:

```bash
curl http://localhost:8000/api/health
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?"}'
curl http://localhost:8000/api/history
curl http://localhost:8000/api/stats/overview
```

Then check **Table Editor -> analyses** in the Supabase Dashboard — the row
from the `curl` call above should be there.

## Notes

- The app never runs migrations or `CREATE TABLE` at startup. Schema
  changes are always made by editing `schema.sql` and re-running it in the
  SQL Editor — this keeps the schema change explicit and reviewable.
- There is no `service_role` key in this project. Every table the backend
  touches must have an explicit RLS policy granting the `anon` role access,
  or that endpoint will silently fail (PostgREST returns an empty result
  set / a permission error, not a Python exception) — if you add a new
  table, remember to add its anon policy in the same PR.
- Tests never touch a real Supabase project — `backend/tests/conftest.py`
  monkeypatches `app.db.crud.get_supabase_client` with an in-memory fake
  (`backend/tests/fake_supabase.py`), so `pytest` runs fully offline.
- This schema also defines `users`, `reports`, and `settings` tables for
  work that hasn't shipped yet (auth, Milestone 13 PDF report metadata, and
  persisted app settings, respectively). Only `analyses` is read/written by
  the app today.
