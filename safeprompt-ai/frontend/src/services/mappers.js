/**
 * Shared mapping from the backend's AnalyzeResponse (snake_case, Pydantic
 * convention) to the camelCase shape used throughout the frontend
 * (mockData.js originally established this shape; every real endpoint
 * that returns analysis records maps into it the same way here).
 *
 * Used by analyzerService.js (POST /api/analyze), historyService.js
 * (GET /api/history), and dashboardService.js (GET /api/history, for the
 * recent activity feed) so there is exactly one place that knows about
 * the backend's field names.
 */
export function mapAnalysisRecord(data) {
  return {
    id: data.id,
    prompt: data.prompt,
    timestamp: data.timestamp,
    score: data.score,
    riskLevel: data.risk_level,
    injectionDetected: data.injection_detected,
    toxicityDetected: data.toxicity_detected,
    injectionConfidence: data.injection_confidence ?? 0,
    toxicityScores: data.toxicity_scores ?? {},
    recommendation: data.recommendation,
    reasoning: data.reasoning ?? [],
    status: data.score >= 75 ? 'safe' : 'unsafe',
  }
}

/**
 * Maps the backend's GET /api/stats/overview response to the camelCase
 * shape the Dashboard's StatsGrid has consumed since Milestone 4 (see the
 * old mockData.js:MOCK_STATS).
 */
export function mapStatsOverview(data) {
  return {
    totalAnalyses: data.total_analyses,
    safePrompts: data.safe_prompts,
    unsafePrompts: data.unsafe_prompts,
    injectionAttempts: data.injection_attempts,
    toxicPrompts: data.toxic_prompts,
    averageSafetyScore: data.average_safety_score,
  }
}
