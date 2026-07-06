"""
Prompt injection detector — Milestone 7.

Combines two independent signals:

1. Regex pattern matching for known injection/jailbreak phrasing — fast,
   exact, zero-dependency. Carried over and extended from the Milestone 6
   interim heuristic.
2. Semantic similarity — embeds the prompt with a sentence-transformers
   model and compares it against a curated corpus of known injection
   examples (datasets/injection_examples.json), catching paraphrased or
   novel attacks that don't match any fixed regex.

The semantic path is optional at runtime: if `sentence-transformers`
isn't installed, the model fails to load, or
`Settings.ENABLE_ML_DETECTORS` is False, `detect_injection()`
transparently falls back to regex-only detection so the rest of the API
keeps working without the heavy ML dependencies installed. This mirrors
the README's note that torch/transformers/sentence-transformers are
optional until they're actually needed — which, as of this milestone,
they now are.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Pattern, Tuple

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# safeprompt-ai/backend/app/services/detectors/injection_detector.py
# parents: [0]=detectors [1]=services [2]=app [3]=backend [4]=safeprompt-ai
DATASET_PATH = Path(__file__).resolve().parents[4] / "datasets" / "injection_examples.json"


# ---------------------------------------------------------------------------
# Signal 1: regex patterns
#
# Each entry is (compiled regex, human-readable reason, score penalty).
# Case-insensitive, matched anywhere in the prompt.
# ---------------------------------------------------------------------------
_INJECTION_PATTERNS: List[Tuple[Pattern, str, int]] = [
    (
        re.compile(r"ignore (all )?(previous|prior|above|the) instructions", re.I),
        'Matched known instruction-override pattern: "ignore previous instructions"',
        45,
    ),
    (
        re.compile(r"disregard (all )?(previous|prior|above|the) (instructions|rules)", re.I),
        'Matched known instruction-override pattern: "disregard previous instructions"',
        45,
    ),
    (
        re.compile(r"forget (your|all|previous) (rules|instructions|training)", re.I),
        'Matched instruction-override pattern: "forget your rules/instructions"',
        40,
    ),
    (
        re.compile(r"\b(dev(eloper)? mode|dan mode|jailbreak(ed)?)\b", re.I),
        "Requests a known jailbreak persona (developer mode / DAN / jailbreak)",
        40,
    ),
    (
        re.compile(r"no (restrictions|filters|limitations|rules)( from now on)?", re.I),
        "Requests unrestricted/unfiltered behavior",
        30,
    ),
    (
        re.compile(r"pretend (you are|to be) .*(unrestricted|unfiltered|without (any )?rules)", re.I),
        "Role-play framing used to bypass restrictions",
        35,
    ),
    (
        re.compile(r"(reveal|show|print|output) (your|the) (system prompt|instructions)", re.I),
        "Requests disclosure of internal system prompt",
        35,
    ),
    (
        re.compile(r"act as an? (unfiltered|unrestricted|uncensored) ai", re.I),
        "Requests an unfiltered/uncensored AI persona",
        35,
    ),
    (
        re.compile(r"bypass (your |the )?(restrictions|safeguards|filters|guardrails)", re.I),
        "Explicitly requests bypassing safety restrictions",
        40,
    ),
    (
        re.compile(r"repeat everything above", re.I),
        "Requests verbatim repetition of prior context (prompt exfiltration)",
        30,
    ),
    (
        re.compile(r"maintenance mode|disable (all )?safety checks", re.I),
        "Requests entering a privileged/unsafe mode",
        35,
    ),
]


def _regex_matches(prompt: str) -> Tuple[bool, int, List[str]]:
    total_penalty = 0
    reasons: List[str] = []
    for pattern, reason, penalty in _INJECTION_PATTERNS:
        if pattern.search(prompt):
            reasons.append(reason)
            total_penalty += penalty
    return bool(reasons), total_penalty, reasons


# ---------------------------------------------------------------------------
# Signal 2: semantic similarity against a reference corpus
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ReferenceExample:
    text: str
    category: str


def _load_reference_examples() -> List[ReferenceExample]:
    if not DATASET_PATH.exists():
        logger.warning(
            "Injection reference dataset not found at %s; semantic detection disabled.",
            DATASET_PATH,
        )
        return []
    with DATASET_PATH.open(encoding="utf-8") as f:
        raw = json.load(f)
    return [ReferenceExample(text=item["text"], category=item["category"]) for item in raw]


@lru_cache(maxsize=1)
def _get_embedder():
    """
    Lazily loads the sentence-transformers model. Returns None if the
    dependency isn't installed, the model fails to load, or ML detectors
    are disabled via settings — callers must handle None by falling back
    to regex-only detection.
    """
    if not settings.ENABLE_ML_DETECTORS:
        return None
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        logger.warning(
            "sentence-transformers not installed; falling back to regex-only injection detection."
        )
        return None
    try:
        return SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    except Exception:  # noqa: BLE001 - any load failure should degrade gracefully
        logger.exception(
            "Failed to load embedding model '%s'; falling back to regex-only detection.",
            settings.EMBEDDING_MODEL_NAME,
        )
        return None


@lru_cache(maxsize=1)
def _get_reference_embeddings():
    embedder = _get_embedder()
    examples = _load_reference_examples()
    if embedder is None or not examples:
        return None
    embeddings = embedder.encode([example.text for example in examples], normalize_embeddings=True)
    return examples, embeddings


def _semantic_match(prompt: str) -> Optional[Tuple[float, ReferenceExample]]:
    """
    Returns (cosine similarity, best-matching reference example) if the ML
    path is available, else None (caller falls back to regex-only).
    """
    bundle = _get_reference_embeddings()
    embedder = _get_embedder()
    if bundle is None or embedder is None:
        return None
    examples, ref_embeddings = bundle

    query_vector = embedder.encode(prompt, normalize_embeddings=True)

    best_similarity = -1.0
    best_example: Optional[ReferenceExample] = None
    for ref_vector, example in zip(ref_embeddings, examples):
        # Both vectors are L2-normalized, so dot product == cosine similarity.
        similarity = float(sum(a * b for a, b in zip(ref_vector, query_vector)))
        if similarity > best_similarity:
            best_similarity = similarity
            best_example = example

    if best_example is None:
        return None
    return best_similarity, best_example


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
@dataclass
class InjectionDetectionResult:
    detected: bool
    penalty: int
    confidence: float  # 0-1, highest signal strength found
    method: str  # "regex", "semantic", or "regex+semantic"
    reasons: List[str] = field(default_factory=list)


def detect_injection(prompt: str) -> InjectionDetectionResult:
    """
    Runs both detection signals over `prompt` and returns a combined
    result. Regex hits and semantic-similarity hits each contribute their
    own penalty (capped at 100 total); confidence reflects the strongest
    single signal.
    """
    regex_hit, regex_penalty, reasons = _regex_matches(prompt)
    method_parts: List[str] = []
    confidence = 1.0 if regex_hit else 0.0
    semantic_penalty = 0

    if regex_hit:
        method_parts.append("regex")

    semantic_result = _semantic_match(prompt)
    if semantic_result is not None:
        similarity, example = semantic_result
        method_parts.append("semantic")
        confidence = max(confidence, similarity)
        if similarity >= settings.INJECTION_SIMILARITY_THRESHOLD:
            semantic_penalty = round(45 * similarity)
            reasons.append(
                f"Semantically similar ({similarity:.0%}) to a known "
                f"{example.category.replace('_', ' ')} example"
            )

    detected = regex_hit or semantic_penalty > 0
    penalty = min(100, regex_penalty + semantic_penalty)
    method = "+".join(method_parts) if method_parts else "regex"

    return InjectionDetectionResult(
        detected=detected,
        penalty=penalty,
        confidence=round(max(0.0, confidence), 4),
        method=method,
        reasons=reasons,
    )
