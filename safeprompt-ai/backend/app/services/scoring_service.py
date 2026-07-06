"""
Safety scoring engine.

Milestone 6 baseline: combines the injection and toxicity results into a
single 0-100 safety score and one of five risk levels, using the
thresholds defined in core/config.py, so /api/analyze returns a complete,
usable result.

Milestone 9 formalizes this into the full scoring engine: configurable
signal weighting, multi-factor reasoning, and richer recommendation
templates per risk level.
"""

from app.core.config import get_settings
from app.services.injection_service import InjectionDetectionResult
from app.services.toxicity_service import ToxicityDetectionResult

settings = get_settings()

# Maximum points deducted from a perfect 100 when a signal is detected at
# full (1.0) confidence. Injection is weighted higher than toxicity
# because it represents an attempt to compromise the system itself.
INJECTION_PENALTY_WEIGHT = 70.0
TOXICITY_PENALTY_WEIGHT = 60.0

_RECOMMENDATIONS = {
    "safe": "Safe to process. No suspicious instructions or harmful language were detected.",
    "low": "Likely safe, but a brief review is advised due to minor risk signals.",
    "medium": "Proceed with caution. Review this prompt before processing it further.",
    "high": "Do not process automatically. Manual review is strongly recommended.",
    "critical": "Block this prompt. Strong indicators of injection or harmful content were found.",
}


def calculate_safety_score(
    injection: InjectionDetectionResult,
    toxicity: ToxicityDetectionResult,
) -> float:
    """Combines detector confidences into a single 0-100 safety score."""
    score = 100.0
    if injection.detected:
        score -= injection.confidence * INJECTION_PENALTY_WEIGHT
    if toxicity.detected:
        score -= toxicity.confidence * TOXICITY_PENALTY_WEIGHT
    return round(max(0.0, min(100.0, score)), 1)


def determine_risk_level(score: float) -> str:
    """Maps a 0-100 score to one of five risk levels using configured thresholds."""
    if score >= settings.RISK_THRESHOLD_SAFE:
        return "safe"
    if score >= settings.RISK_THRESHOLD_LOW:
        return "low"
    if score >= settings.RISK_THRESHOLD_MEDIUM:
        return "medium"
    if score >= settings.RISK_THRESHOLD_HIGH:
        return "high"
    return "critical"


def build_recommendation(risk_level: str) -> str:
    """Returns a plain-language recommendation for the given risk level."""
    return _RECOMMENDATIONS.get(risk_level, _RECOMMENDATIONS["medium"])


def build_reasoning(
    injection: InjectionDetectionResult,
    toxicity: ToxicityDetectionResult,
) -> str:
    """Combines both detectors' explanations into a single reasoning string."""
    return f"{injection.reason} {toxicity.explanation}"
