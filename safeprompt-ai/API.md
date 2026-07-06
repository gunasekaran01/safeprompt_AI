# API Reference

Base URL: `/api` (proxied to the FastAPI backend — see `frontend/vite.config.js` in
development, `frontend/nginx.conf` in production). Interactive Swagger
docs are always available at `/api/docs` against a running backend.

## Authentication

Every endpoint below except `GET /api/health` requires:

```
Authorization: Bearer <supabase-access-token>
```

The token is a Supabase Auth JWT, obtained client-side via
`@supabase/supabase-js` (sign up / login — see `Architecture.md`'s
Authentication flow) — this API never issues its own tokens. A
missing, malformed, or invalid/expired token returns:

```
401 Unauthorized
WWW-Authenticate: Bearer
{ "detail": "<human-readable reason>" }
```

All list/get/delete endpoints scope their results to the authenticated
user automatically. There is no way to pass another user's id and no
endpoint that accepts one — a resource that exists but belongs to
someone else is indistinguishable from one that doesn't exist (both
return `404`).

---

## Health

### `GET /api/health`

No authentication required. Returns `200 OK` with a small status body —
used by both Dockerfiles' `HEALTHCHECK` and `docker-compose.yml`.

---

## Analysis

### `POST /api/analyze`

Analyzes a prompt and persists the result.

**Request body:**
```json
{ "prompt": "string, 1-5000 characters" }
```

**Response `200`:**
```json
{
  "id": "string",
  "prompt": "string",
  "timestamp": "ISO 8601 datetime",
  "score": 0-100,
  "risk_level": "safe | low | medium | high | critical",
  "injection_detected": true,
  "toxicity_detected": false,
  "injection_confidence": 0.0-1.0,
  "toxicity_scores": { "toxicity": 0.0, "insult": 0.0, "...": "..." },
  "recommendation": "string",
  "reasoning": ["string", "..."]
}
```

`422` for a prompt outside 1–5000 characters.

---

## History

### `GET /api/history`

Paginated, filterable list of the authenticated user's own past analyses.

**Query params:**

| Param | Type | Default | Notes |
|---|---|---|---|
| `limit` | int | 20 | 1–100 |
| `offset` | int | 0 | |
| `risk_level` | string | — | `safe`\|`low`\|`medium`\|`high`\|`critical`; `422` if invalid |
| `search` | string | — | case-insensitive substring match over `prompt` |
| `injection_only` | bool | false | |
| `toxicity_only` | bool | false | |

**Response `200`:**
```json
{ "items": [ /* AnalyzeResponse[] */ ], "total": 0, "limit": 20, "offset": 0 }
```

### `GET /api/history/{analysis_id}`

Returns a single `AnalyzeResponse`, or `404` if it doesn't exist (or isn't the caller's).

### `DELETE /api/history/{analysis_id}`

`204 No Content` on success, `404` if it doesn't exist (or isn't the caller's).

---

## Stats

All three routes aggregate only the authenticated user's own analyses.

### `GET /api/stats`

Convenience endpoint combining the two below in one call.
```json
{ "overview": { /* StatsOverview */ }, "charts": { /* ChartDataResponse */ } }
```

### `GET /api/stats/overview`

```json
{
  "total_analyses": 0,
  "safe_prompts": 0,
  "unsafe_prompts": 0,
  "injection_attempts": 0,
  "toxic_prompts": 0,
  "average_safety_score": 0.0
}
```

### `GET /api/stats/charts`

**Query params:** `days` (int, default 14, range 1–90) — trailing window for the score trend.

```json
{
  "score_trend": [{ "date": "YYYY-MM-DD", "average_score": 0.0, "count": 0 }],
  "risk_level_distribution": [{ "risk_level": "safe", "count": 0 }],
  "detection_breakdown": { "injection_only": 0, "toxicity_only": 0, "both": 0, "none": 0 }
}
```

---

## Reports

### `GET /api/reports/{analysis_id}`

Generates a PDF safety report for one of the caller's own analyses and
streams it back as a file download (`Content-Type: application/pdf`).
Also logs the generation to the `reports` table (best-effort — a
Supabase hiccup here still returns the PDF, since the file itself is
what the user asked for). `404` if the analysis doesn't exist or isn't
the caller's.

---

## Profiles

### `GET /api/profiles/me`

Returns (lazily creating on first call) the authenticated user's profile.

```json
{
  "id": "uuid",
  "name": "string | null",
  "email": "string",
  "avatar_url": "string | null",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```

### `PATCH /api/profiles/me`

**Request body** (all fields optional, at least one required — `400` if empty):
```json
{ "name": "string, 1-100 chars", "avatar_url": "string, up to 2048 chars" }
```

Returns the updated profile (same shape as `GET`). `404` if the profile
somehow doesn't exist after the lazy-create step.

### `DELETE /api/profiles/me`

Permanently deletes the authenticated user's Supabase Auth account.
Every row they own across `profiles`/`analyses`/`reports`/`settings`
cascades via foreign keys — there is no confirmation step at the API
layer; the frontend (`DeleteAccountSection.jsx`) is responsible for
confirming intent before calling this. `204 No Content` on success.

---

## Auth

### `GET /api/auth/me`

Returns the identity Supabase associates with the current bearer token
— useful for the frontend to confirm a session is valid against this
backend specifically, independent of Supabase's own client-side state.

```json
{ "id": "uuid", "email": "string | null" }
```
