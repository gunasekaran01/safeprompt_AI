"""
Prompt analysis routes.

Milestone 6 scope: a real POST /api/analyze endpoint backed by the
scoring in app/services/analysis_service.py.

Milestone 10 scope (originally SQLite, since migrated to Supabase): every
analysis is persisted immediately after scoring via app/db/crud.py.
Persistence failures are not swallowed — if the database write fails,
the request fails loudly (a 500) rather than silently returning an
unsaved result, since a "successful" analysis the user can never see
again in their history is a worse experience than a clear error.

SaaS Phase 4: this route now requires authentication
(Depends(get_current_user)) and persists every analysis with the
requesting user's id, so it appears only in *their* history/stats, never
anyone else's.
"""

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, get_current_user
from app.db import crud
from app.schemas.analysis import PromptAnalysisRequest, AnalyzeResponse
from app.services.analysis_service import analyze_prompt

router = APIRouter(prefix="/analyze", tags=["Analysis"])


@router.post("", response_model=AnalyzeResponse, summary="Analyze a prompt for safety")
def analyze(
    request: PromptAnalysisRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> AnalyzeResponse:
    """
    Analyzes a submitted prompt for injection attempts and toxic language,
    persists the result to Supabase under the authenticated user, and
    returns a 0-100 safety score, risk level, recommendation, and
    reasoning.
    """
    result = analyze_prompt(request.prompt)
    crud.create_analysis(result, user_id=current_user.id)
    return result
