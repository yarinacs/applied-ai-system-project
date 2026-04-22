import logging
import numpy as np
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    _TRANSFORMERS_AVAILABLE = True
except ImportError:
    _TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not installed; falling back to keyword matching")

_model = None


def _get_model():
    global _model
    if not _TRANSFORMERS_AVAILABLE:
        return None
    if _model is None:
        logger.info("Loading embedding model (first run downloads ~80MB)...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def song_to_description(song: Dict) -> str:
    """Convert a song dict into a natural-language string suitable for embedding."""
    energy_label = "high" if song["energy"] > 0.7 else "medium" if song["energy"] > 0.4 else "low"
    tempo_label = "fast" if song["tempo_bpm"] > 130 else "moderate" if song["tempo_bpm"] > 90 else "slow"
    acoustic_label = "acoustic" if song["acousticness"] > 0.6 else "semi-acoustic" if song["acousticness"] > 0.3 else "electric"
    dance_label = "very danceable" if song["danceability"] > 0.75 else "danceable" if song["danceability"] > 0.5 else "not very danceable"
    feel_label = "uplifting" if song["valence"] > 0.7 else "neutral" if song["valence"] > 0.4 else "melancholic"

    return (
        f"{song['title']} by {song['artist']}: "
        f"{song['genre']} music with a {song['mood']} mood. "
        f"{energy_label.capitalize()} energy, {tempo_label} tempo ({song['tempo_bpm']:.0f} BPM), "
        f"{acoustic_label} sound. {feel_label.capitalize()} feel, {dance_label}."
    )


def build_song_index(songs: List[Dict]) -> Tuple[List[Dict], np.ndarray]:
    """Embed all songs and return (songs, embedding_matrix)."""
    model = _get_model()
    if model is None:
        return songs, np.zeros((len(songs), 1))

    descriptions = [song_to_description(s) for s in songs]
    embeddings = model.encode(descriptions, normalize_embeddings=True)
    logger.info(f"Built embeddings for {len(songs)} songs, shape={embeddings.shape}")
    return songs, embeddings


def _keyword_fallback(query: str, songs: List[Dict], k: int) -> List[Tuple[Dict, float]]:
    query_words = set(query.lower().split())
    results = []
    for song in songs:
        desc = song_to_description(song).lower()
        overlap = sum(1 for w in query_words if w in desc)
        results.append((song, overlap / max(len(query_words), 1)))
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:k]


def retrieve_songs(
    query: str,
    songs: List[Dict],
    embeddings: np.ndarray,
    k: int = 5,
) -> List[Tuple[Dict, float]]:
    """Return the top-k songs most semantically similar to the query."""
    model = _get_model()
    if model is None:
        logger.warning("Using keyword fallback for retrieval")
        return _keyword_fallback(query, songs, k)

    query_vec = model.encode([query], normalize_embeddings=True)[0]
    similarities = embeddings @ query_vec
    top_indices = np.argsort(similarities)[::-1][:k]
    results = [(songs[i], float(similarities[i])) for i in top_indices]
    logger.info(f"Retrieved {len(results)} songs for query '{query[:60]}'")
    return results
