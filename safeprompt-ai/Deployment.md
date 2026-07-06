# Deployment

This covers a two-container Docker Compose deployment (FastAPI backend +
Nginx-served React frontend), against a managed Supabase project. There
is no database container in this stack — Supabase is external and
managed.

## 1. Supabase project setup

1. Create a project at [supabase.com](https://supabase.com).
2. **SQL Editor → New Query** → paste the full contents of
   `backend/supabase/schema.sql` → **Run**. This creates `profiles`,
   `analyses`, `reports`, `settings`, every index, every RLS policy, and
   the `handle_new_user`/`set_updated_at` triggers. The file is
   idempotent — safe to re-run after future schema edits.
3. **Authentication → Providers**: confirm **Email** is enabled.
4. **Authentication → URL Configuration**: set:
   - **Site URL** to your production frontend origin (e.g. `https://app.example.com`)
   - **Redirect URLs**: add `https://app.example.com/auth/callback` and `https://app.example.com/reset-password` (plus the `localhost:5173` equivalents for local development)
5. **Project Settings → API**: note the **Project URL**, **`anon` key**, and **`service_role` key**. Treat the service-role key like a root password — it bypasses Row Level Security entirely and must never reach the frontend or version control.

## 2. Environment configuration

Copy each `.env.production.example` to `.env` on your production host
(or translate into your platform's secret manager — Docker Compose
`env_file`, Kubernetes Secrets, Railway/Render/Fly secrets, etc.):

**`backend/.env`** (from `backend/.env.production.example`):
```env
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=["https://your-production-domain.com"]

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key   # required — see Architecture.md

ENABLE_ML_DETECTORS=True
# ... (see backend/.env.production.example for the full list, including
# scoring-engine weights and risk thresholds)
```

**`frontend/.env`** (from `frontend/.env.production.example`):
```env
VITE_API_BASE_URL=/api
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

**Repo root `.env`** (from `.env.example`) — read by `docker compose
build` to substitute `${VITE_...}` into `docker-compose.yml`'s frontend
build args:
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

> The frontend's `VITE_*` variables are compiled **into** the JS bundle
> at build time (Vite's behavior), not read at container runtime — this
> is why they're passed as Docker build args (`frontend/Dockerfile`),
> not `docker run -e` environment variables. Changing them requires
> rebuilding the frontend image.

## 3. Docker Compose

```bash
docker compose up --build
```

- **`backend`** — built from `backend/Dockerfile` (Python 3.11-slim, non-root user, `HEALTHCHECK` against `/api/health`), exposed on `:8000`, with a named volume (`reports_data`) mounted at `/app/reports` so generated PDFs survive container recreation.
- **`frontend`** — a two-stage build (`frontend/Dockerfile`): Node compiles the Vite app, then `nginx:alpine` serves the static output on `:80` and reverse-proxies `/api/*` to the `backend` service (`frontend/nginx.conf`), waiting on `backend`'s healthcheck before starting.

Verify:
```bash
curl http://localhost:8000/api/health
curl http://localhost/           # frontend
curl http://localhost/api/health # same backend, via the Nginx proxy
```

## 4. Reverse proxy / TLS

`frontend/nginx.conf` deliberately does **not** terminate TLS — in most
real deployments this container sits behind a managed load balancer
(e.g. a cloud provider's HTTPS load balancer) or a separate
TLS-terminating reverse proxy (Caddy, Traefik, or Nginx + Certbot) in
front of it. If this container must terminate TLS itself, add a second
`server` block on `443` with `ssl_certificate`/`ssl_certificate_key` and
redirect the port-80 block to it.

## 5. CI/CD

`.github/workflows/ci.yml` runs on every push/PR to `main`:

| Job | What it does |
|---|---|
| `backend-tests` | `pytest -v` against `tests/fake_supabase.py` — no real Supabase credentials needed, dummy `SUPABASE_URL`/`SUPABASE_ANON_KEY` just satisfy settings validation |
| `frontend-build` | `npm run lint` + `npm run build`, with dummy `VITE_*` values |
| `frontend-tests` | `npm test` (Vitest) |
| `docker-build` | Builds both production images (`push: false`) — gated on all three jobs above passing |

Nothing in this workflow pushes an image anywhere. Add a push step once
you've picked a registry (GitHub Container Registry, Docker Hub, ECR,
etc.) and a deploy target — the exact steps depend on where you're
hosting, which is outside this file's scope.

## 6. Scaling notes

- The backend Docker image installs `torch`/`transformers`/`sentence-transformers`/`detoxify` unconditionally (several GB) even if `ENABLE_ML_DETECTORS=False` at runtime — there's no separate "lite" image today.
- `backend/Dockerfile` runs a single Uvicorn worker per container by design — scale by running multiple container replicas behind a load balancer rather than multiple Uvicorn workers in one container, so each replica's memory footprint (torch + transformer models, if ML detectors are enabled) stays predictable and replicas can be restarted independently.
- Expect the first request after a cold start/deploy to be slower while ML models load into memory, if `ENABLE_ML_DETECTORS=True`.

## 7. Rollback

Since there's no database migration tool (schema changes are applied
manually via `supabase/schema.sql`, and the file is written to be
additive/idempotent rather than destructive), rolling back is primarily
about redeploying the previous Docker images. If a schema change did
need to be reverted, write and run the reverse SQL by hand in the
Supabase SQL Editor — there is no `schema.sql` "down" migration.
