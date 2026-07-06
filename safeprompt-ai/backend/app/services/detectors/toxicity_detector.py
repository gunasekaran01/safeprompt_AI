"""
Toxicity detector — Milestone 8.

Wraps the Detoxify model (a multi-label toxic-comment classifier) to
score a prompt across several categories: toxicity, severe_toxicity,
obscene, threat, insult, and identity_attack (exact category set depends
on `Settings.TOXICITY_MODEL_NAME`: "original", "unbiased", or
"multilingual").

Falls back to the small keyword-list heuristic from Milestone 6 if
`detoxify`/`torch` aren't installed, the model fails to download/load, or
`Settings.ENABLE_ML_DETECTORS` is False — so the API keeps working even
without the heavy ML dependencies installed, and the test suite can run
fast without downloading models.
"""

import logging
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Dict, List, Tuple

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# ---------------------------------------------------------------------------
# Fallback: keyword heuristic (carried over from Milestone 6)
#
# A small, deliberately conservative list for mild-to-moderate
# hostility/insults, each with an independent penalty. Only used when the
# real Detoxify model isn't available.
# ---------------------------------------------------------------------------
_TOXIC_KEYWORDS: List[Tuple[str, int]] = [
    ("idiot", 20),
    ("stupid", 15),
    ("dumb", 12),
    ("shut up", 15),
    ("worthless", 20),
    ("pathetic", 15),
    ("hate you", 20),
    ("useless", 12),
    ("moron", 20),
]


def _keyword_fallback(prompt: str) -> Tuple[bool, int, List[str]]:
    lowered = prompt.lower()
    total_penalty = 0
    reasons: List[str] = []
    for keyword, penalty in _TOXIC_KEYWORDS:
        if keyword in lowered:
            reasons.append(f'Contains hostile/toxic language: "{keyword}"')
            total_penalty += penalty
    return bool(reasons), total_penalty, reasons


# ---------------------------------------------------------------------------
# Real detector: Detoxify
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _get_model():
    """
    Lazily loads the Detoxify model. Returns None if the dependency isn't
    installed, the model fails to load, or ML detectors are disabled via
    settings — callers must handle None by falling back to the keyword
    heuristic.
    """
    if not settings.ENABLE_ML_DETECTORS:
        return None
    try:
        from detoxify import Detoxify
    except ImportError:
        logger.warning(
            "detoxify not installed; falling back to keyword-based toxicity detection."
        )
        return None
    try:
        return Detoxify(settings.TOXICITY_MODEL_NAME)
    except Exception:  # noqa: BLE001 - any load failure should degrade gracefully
        logger.exception(
            "Failed to load Detoxify model '%s'; falling back to keyword-based detection.",
            settings.TOXICITY_MODEL_NAME,
        )
        return None


@dataclass
class ToxicityDetectionResult:
    detected: bool
    penalty: int
    scores: Dict[str, float] = field(default_factory=dict)
    method: str = "keyword"  # "keyword" or "model"
    reasons: List[str] = field(default_factory=list)


def detect_toxicity(prompt: str) -> ToxicityDetectionResult:
    """
    Scores `prompt` for toxicity. Prefers the real Detoxify model; falls
    back to the keyword heuristic if the model isn't available or
    prediction fails for any reason.
    """
    model = _get_model()
    if model is None:
        detected, penalty, reasons = _keyword_fallback(prompt)
        return ToxicityDetectionResult(
            detected=detected, penalty=penalty, scores={}, method="keyword", reasons=reasons
        )

    try:
        raw_scores = model.predict(prompt)
    except Exception:  # noqa: BLE001 - prediction failures should degrade gracefully
        logger.exception("Detoxify prediction failed; falling back to keyword-based detection.")
        detected, penalty, reasons = _keyword_fallback(prompt)
        return ToxicityDetectionResult(
            detected=detected, penalty=penalty, scores={}, method="keyword", reasons=reasons
        )

    scores: Dict[str, float] = {category: float(value) for category, value in raw_scores.items()}

    reasons: List[str] = []
    penalty = 0
    for category, score in scores.items():
        if score >= settings.TOXICITY_CATEGORY_THRESHOLD:
            label = category.replace("_", " ")
            reasons.append(f"Detected {label} ({score:.0%} confidence)")
            penalty += round(score * 40)

    return ToxicityDetectionResult(
        detected=bool(reasons),
        penalty=min(100, penalty),
        scores=scores,
        method="model",
        reasons=reasons,
    )
