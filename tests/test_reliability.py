import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.reliability import retrieval_confidence, confidence_label, confidence_detail


def _retrieved(scores):
    return [({"title": f"Song {i}"}, s) for i, s in enumerate(scores)]


def test_clear_winner_gives_high_confidence():
    assert retrieval_confidence(_retrieved([0.95, 0.60, 0.55])) > 0.30


def test_near_tie_gives_low_confidence():
    assert retrieval_confidence(_retrieved([0.82, 0.81, 0.80])) < 0.05


def test_single_result_is_full_confidence():
    assert retrieval_confidence(_retrieved([0.90])) == 1.0


def test_zero_top_score_returns_zero():
    assert retrieval_confidence(_retrieved([0.0, 0.0])) == 0.0


def test_confidence_never_exceeds_one():
    assert retrieval_confidence(_retrieved([1.0, 0.0])) <= 1.0


def test_confidence_labels():
    assert confidence_label(0.15) == "High"
    assert confidence_label(0.06) == "Medium"
    assert confidence_label(0.01) == "Low"


def test_confidence_detail_returns_string():
    for score in [0.0, 0.05, 0.15]:
        result = confidence_detail(score)
        assert isinstance(result, str)
        assert len(result) > 0
