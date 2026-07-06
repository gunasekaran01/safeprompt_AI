"""
Aggregate API router.

Combines all route modules into a single router mounted at /api in
main.py. New route modules register themselves here rather than in
main.py, keeping main.py focused on application bootstrap only.

Mounted routers:
- analysis  -> POST /api/analyze                          (app/api/analysis.py)
- history   -> GET/DELETE /api/history..., /api/dashboard/*  (app/api/history.py)
- reports   -> GET /api/reports/{analysis_id}              (app/api/reports.py)
- auth      -> GET /api/auth/me                            (app/api/routes/auth.py)
- profiles  -> GET/PATCH /api/profiles/me                  (app/api/routes/profiles.py)
- profile_compat -> GET/PATCH /api/profile (singular)      (app/api/routes/profile_compat.py)
- admin     -> GET /api/admin/overview, /api/admin/users...  (app/api/routes/admin.py)

Note: app/api/analysis.py, history.py, and reports.py (top-level, under
app/api/ directly) are the current, correct implementations — they use
app/core/security.py for auth and app/services/history_service.py (etc.)
for persistence, matching the actual `analyses` table schema. The
similarly-named modules under app/api/routes/ (analysis.py, history.py,
reports.py, stats.py) are an earlier, incompatible implementation built
against app/db/crud.py and a schema class (AnalyzeResponse) that no
longer exists in app/schemas/analysis.py — they are NOT imported here.
See backend/_deprecated/ and backend/supabase/README.md.
"""

from fastapi import APIRouter

from app.api.analysis import router as analysis_router
from app.api.history import router as history_router
from app.api.reports import router as reports_router
from app.api.routes import admin, auth, profile_compat, profiles

api_router = APIRouter()
api_router.include_router(analysis_router)
api_router.include_router(history_router)
api_router.include_router(reports_router)
api_router.include_router(auth.router)
api_router.include_router(profiles.router)
api_router.include_router(profile_compat.router)
api_router.include_router(admin.router)
