import logging
from typing import List, Tuple, Dict

logger = logging.getLogger(__name__)


def retrieval_confidence(retrieved: List[Tuple[Dict, float]]) -> float:
    """
    Measures how decisive the top retrieval result is compared to the second.
    Returns a score from 0.0 (tie) to 1.0 (clear winner).
    """
    if len(retrieved) < 2:
        return 1.0
    top, second = retrieved[0][1], retrieved[1][1]
    if top == 0:
        return 0.0
    return min(1.0, (top - second) / top)


def confidence_label(score: float) -> str:
    if score >= 0.10:
        return "High"
    elif score >= 0.04:
        return "Medium"
    return "Low"


def confidence_detail(score: float) -> str:
    if score >= 0.10:
        return "The top match is clearly better than the alternatives."
    elif score >= 0.04:
        return "The top match is somewhat better than the alternatives."
    return "Several songs closely match your query — the recommendation may vary."
