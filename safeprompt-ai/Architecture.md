# Architecture

## Overview

```
┌─────────────┐        HTTPS         ┌──────────────┐      HTTPS       ┌───────────────┐
│   Browser   │ ───────────────────▶ │   FastAPI    │ ───────────────▶ │   Supabase    │
│  React SPA  │ ◀─────────────────── │   backend    │ ◀─────────────── │  (Postgres +  │
└─────────────┘   JSON over /api/*   └──────────────┘  PostgREST/Auth  │  Auth + RLS)  │
       │                                                                └───────────────┘
       │  Supabase Auth SDK (@supabase/supabase-js)                            ▲
       └────────────────────────────────────────────────────────────────────────┘
              sign up / login / logout / password reset — direct, no backend involved
```

Two things talk to Supabase independently:

1. **The browser**, directly, via `@supabase/supabase-js` — but *only* for
   authentication (sign up, login, logout, password reset, session
   persistence/refresh). It never queries a table directly.
2. **The FastAPI backend**, via `supabase-py` — for every actual read/write
   of application data (analyses, profiles, reports).

This split exists because Supabase Auth's email verification and password
recovery flows are built around redirect links and client-side session
detection (`detectSessionInUrl`) that only make sense from a browser
context — reimplementing them server-side would mean rebuilding
functionality Supabase already provides for free.

## Authentication flow

1. User submits the login form → `AuthContext.login()` calls
   `supabase.auth.signInWithPassword()` directly against Supabase Auth.
2. Supabase returns a session (JWT access token + refresh token).
   `@supabase/supabase-js` persists it to `localStorage` and schedules a
   silent refresh before it expires (`persistSession`/`autoRefreshToken`
   — see `frontend/src/services/supabaseClient.js`).
3. `AuthContext` subscribes to `supabase.auth.onAuthStateChange()`, so
   `session`/`user` state (and every `<ProtectedRoute>`) update live.
4. Every subsequent API call, `apiClient.js`'s axios interceptor reads
   the current session and attaches `Authorization: Bearer <access_token>`.
5. On the backend, `app/api/deps.get_current_user` extracts that header
   and validates the token by calling Supabase Auth's own
   `GET /auth/v1/user` (`client.auth.get_user(token)`) — **not** by
   verifying the JWT signature locally. This means the backend never
   needs the project's JWT signing secret, at the cost of one extra HTTP
   round-trip per authenticated request — an acceptable trade at this
   project's scale.
6. A valid token yields a `CurrentUser(id, email, access_token)`, which
   every protected route depends on and uses to scope its queries.

## Two different Supabase access patterns, on purpose

The backend uses **two different ways** of talking to Supabase, and
which one a given route uses is a deliberate, documented choice — not
inconsistency:

| Table | Client used | Enforcement | Why |
|---|---|---|---|
| `analyses`, `reports` | Shared client (`get_supabase_client()`), service-role key | Row Level Security exists as a backstop, but the real enforcement is **Python-level**: every `app/db/crud.py` function takes an explicit `user_id` and filters by it | These tables are queried with pagination, filtering, and aggregation (`stats_service.py`) that's simplest to reason about in application code; a single long-lived cached client also avoids reconnecting per request |
| `profiles` | Per-request client (`get_user_scoped_client(access_token)`), the user's own JWT | **RLS is the actual boundary** (`auth.uid() = id` policies in `supabase/schema.sql`) | A profile is a single-row-per-user lookup with no complex filtering — a natural fit for letting Postgres enforce ownership directly, and a smaller trust surface for a table holding PII |
| `settings` | Provisioned with RLS, not yet queried by any code | N/A | Reserved for a future cross-device preference sync (see `PROGRESS.md`'s Known Gaps) |

Account **deletion** is the one operation that must use the service-role
key even though it's user-specific: Supabase's admin API
(`auth.admin.delete_user`, called from `app/services/account_service.py`)
has no concept of "let this user delete themselves" — it's an
admin-only operation by design, so a service-role-authenticated backend
performing it (after validating the caller's own JWT identifies exactly
the account being deleted) is the correct place for it to live.

## Data flow: analyzing a prompt

1. `POST /api/analyze` (`app/api/routes/analysis.py`) requires
   `Depends(get_current_user)`.
2. `app/services/analysis_service.py` orchestrates:
   - `detectors/injection_detector.py` — regex patterns + (if
     `ENABLE_ML_DETECTORS=True`) semantic similarity via
     `sentence-transformers` against `datasets/injection_examples.json`.
   - `detectors/toxicity_detector.py` — Detoxify (if enabled) or a
     keyword fallback.
   - `scoring_engine.compute_score()` — blends both detectors' penalty +
     confidence/severity into a single 0-100 score via a probabilistic
     OR, with a hard floor for any high-confidence single-signal attack.
3. `crud.create_analysis(result, user_id=current_user.id)` persists the
   row, `user_id` set explicitly.
4. The same `AnalyzeResponse` shape is returned to the caller and is
   what gets stored — there's no separate "read" shape.

`GET /api/history`, `GET /api/stats/*`, and `GET /api/reports/{id}` all
follow the same shape: require `get_current_user`, then call a `crud.py`
function that takes `user_id` as an explicit parameter and filters by
it. A record that exists but belongs to someone else and a record that
doesn't exist at all are **indistinguishable** to the caller (both 404)
— this is deliberate, so no route can leak "that exists, it's just not
yours."

## Frontend structure

- **`pages/`** — one component per route, wired to a `services/*.js`
  module for data, never calling `axios`/`apiClient` directly.
- **`services/`** — one module per backend resource
  (`analyzerService.js`, `historyService.js`, `dashboardService.js`,
  `profileService.js`, `reportService.js`), each wrapping `apiClient.js`
  and mapping the backend's snake_case JSON to the camelCase shape the
  rest of the frontend expects (`services/mappers.js` centralizes the
  shared analysis-record mapping so there's exactly one place that knows
  the backend's field names).
- **`context/AuthContext.jsx`** — the only code that imports
  `services/supabaseClient.js` directly for anything other than reading
  the current session in `apiClient.js`'s interceptor.
- **`components/Auth/ProtectedRoute.jsx`** — a layout route in `App.jsx`
  wrapping every page that requires a session.

## Testing strategy

- **Backend:** `tests/fake_supabase.py` is an in-memory stand-in for
  `supabase.Client`, implementing just enough of the PostgREST
  query-builder surface (`select`/`insert`/`update`/`delete`, `.eq()`,
  `.ilike()`, `.order()`, `.range()`, `.limit()`, `.execute()`) that
  `app/db/crud.py` and `app/db/profile_crud.py` run completely unmodified
  against it. `conftest.py` monkeypatches `get_supabase_client`, and
  `test_auth.py` separately fakes `client.auth.get_user` for JWT
  validation — the full pytest suite runs offline, with no real
  Supabase project or credentials required.
- **Frontend:** Vitest + React Testing Library, with `apiClient.js`
  mocked at the module level in service tests (`historyService.test.js`)
  and `AuthContext`'s `useAuth()` mocked in component tests
  (`ProtectedRoute.test.jsx`) — no network calls, no real Supabase
  session needed to run the suite.

## Deployment topology

Two containers (see `Deployment.md` for the full walkthrough):

- **`backend`** — FastAPI, talks to Supabase over the internet; no
  database container in this stack at all.
- **`frontend`** — a two-stage build: Vite compiles the SPA, then Nginx
  serves the static output and reverse-proxies `/api/*` to the `backend`
  container, so the browser only ever talks to one origin (matching the
  dev-time Vite proxy in `vite.config.js`).

Supabase itself is not part of this deployment — it's a managed external
dependency, provisioned once via `supabase/schema.sql` and referenced by
URL/key in both containers' environment.
