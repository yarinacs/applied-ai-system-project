import csv
import logging
from typing import List, Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Song:
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


def load_songs(csv_path: str) -> List[Dict]:
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
                "youtube_id":   row.get("youtube_id", "").strip(),
            })
    logger.info(f"Loaded {len(songs)} songs from {csv_path}")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user preferences. Max possible score: 5.75."""
    score = 0.0
    reasons = []

    if song["genre"].lower() == user_prefs["genre"].lower():
        score += 1.0
        reasons.append("genre match (+1.0)")

    if song["mood"].lower() == user_prefs["mood"].lower():
        score += 1.5
        reasons.append("mood match (+1.5)")

    energy_pts = 2.0 * (1.0 - abs(song["energy"] - user_prefs["target_energy"]))
    score += energy_pts
    reasons.append(f"energy similarity (+{energy_pts:.2f})")

    valence_pts = 0.75 * (1.0 - abs(song["valence"] - user_prefs["target_valence"]))
    score += valence_pts
    reasons.append(f"valence similarity (+{valence_pts:.2f})")

    danceability_pts = 0.50 * (1.0 - abs(song["danceability"] - user_prefs["target_danceability"]))
    score += danceability_pts
    reasons.append(f"danceability similarity (+{danceability_pts:.2f})")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score all songs and return the top-k as (song, score, explanation) tuples."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, " | ".join(reasons)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
