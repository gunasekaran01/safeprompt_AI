"""
Toxicity detection service.

Milestone 6 baseline: a lightweight, keyword-based check so the
/api/analyze endpoint works end-to-end while the rest of the platform is
built out.

Milestone 8 replaces this module entirely with a Detoxify-based
classifier covering profanity, abuse, threats, harassment, and hate
speech, each with model-derived confidence scores and category-specific
explanations.
"""

import re
from dataclasses import dataclass


@dataclass
class ToxicityDetectionResult:
    detected: bool
    category: str
    confidence: float  # 0.0 - 1.0
    explanation: str


# Ordered by severity; the first match wins. Each tuple is
# (compiled pattern, category, confidence, human-readable explanation).
_TOXIC_PATTERNS = [
    (
        re.compile(r"\bkill (yourself|urself)\b|\bkys\b", re.IGNORECASE),
        "threat",
        0.9,
        "Detected language threatening self-harm directed at the reader.",
    ),
    (
        re.compile(r"\bi('|)ll (kill|hurt|beat) you\b", re.IGNORECASE),
        "threat",
        0.85,
        "Detected a direct threat of violence.",
    ),
    (
        re.compile(
            r"\byou('| a)re (useless|worthless|stupid|pathetic|an idiot)\b",
            re.IGNORECASE,
        ),
        "harassment",
        0.75,
        "Detected demeaning or harassing language directed at a person.",
    ),
    (
        re.compile(r"\bi hate (you|all)\b", re.IGNORECASE),
        "harassment",
        0.6,
        "Detected hostile language expressing hatred toward a person or group.",
    ),
    (
        re.compile(r"\b(shit|asshole|bastard|bitch|damn it)\b", re.IGNORECASE),
        "profanity",
        0.55,
        "Detected profane language.",
    ),
]


def analyze_toxicity(prompt: str) -> ToxicityDetectionResult:
    """
    Scans the prompt for known toxic-language patterns and returns the
    highest-severity match, or a clean result if none are found.
    """
    for pattern, category, confidence, explanation in _TOXIC_PATTERNS:
        if pattern.search(prompt):
            return ToxicityDetectionResult(
                detected=True,
                category=category,
                confidence=confidence,
                explanation=explanation,
            )

    return ToxicityDetectionResult(
        detected=False,
        category="none",
        confidence=0.9,
        explanation="No toxic language patterns were found in the input.",
    )
