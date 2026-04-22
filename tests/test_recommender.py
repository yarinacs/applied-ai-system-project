import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.recommender import score_song, recommend_songs


def _songs():
    return [
        {
            "id": 1, "title": "Pop Song", "artist": "A", "genre": "pop", "mood": "happy",
            "energy": 0.8, "tempo_bpm": 120, "valence": 0.8, "danceability": 0.8, "acousticness": 0.2,
        },
        {
            "id": 2, "title": "Chill Song", "artist": "B", "genre": "lofi", "mood": "chill",
            "energy": 0.3, "tempo_bpm": 75, "valence": 0.5, "danceability": 0.5, "acousticness": 0.8,
        },
    ]


def test_genre_match_increases_score():
    prefs = {"genre": "pop", "mood": "sad", "target_energy": 0.5, "target_valence": 0.5, "target_danceability": 0.5}
    pop_score, _ = score_song(prefs, _songs()[0])
    lofi_score, _ = score_song(prefs, _songs()[1])
    assert pop_score > lofi_score


def test_mood_match_increases_score():
    prefs = {"genre": "rock", "mood": "chill", "target_energy": 0.5, "target_valence": 0.5, "target_danceability": 0.5}
    pop_score, _ = score_song(prefs, _songs()[0])
    lofi_score, _ = score_song(prefs, _songs()[1])
    assert lofi_score > pop_score


def test_recommend_returns_k_results():
    prefs = {"genre": "pop", "mood": "happy", "target_energy": 0.8, "target_valence": 0.8, "target_danceability": 0.8}
    results = recommend_songs(prefs, _songs(), k=1)
    assert len(results) == 1


def test_recommend_sorted_descending():
    prefs = {"genre": "lofi", "mood": "chill", "target_energy": 0.3, "target_valence": 0.5, "target_danceability": 0.5}
    results = recommend_songs(prefs, _songs(), k=2)
    assert results[0][1] >= results[1][1]


def test_score_returns_reasons():
    prefs = {"genre": "pop", "mood": "happy", "target_energy": 0.8, "target_valence": 0.8, "target_danceability": 0.8}
    score, reasons = score_song(prefs, _songs()[0])
    assert isinstance(reasons, list)
    assert len(reasons) > 0
    assert score > 0
