import os
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are VibeMatch AI, a warm and knowledgeable music recommendation assistant. "
    "You help people discover songs that match their mood and needs. "
    "When given retrieved songs and a user's request, pick the best match and explain "
    "your reasoning using specific song features like genre, mood, energy, and tempo."
)


def _format_songs_context(retrieved: List[Tuple[Dict, float]]) -> str:
    lines = []
    for i, (song, sim) in enumerate(retrieved, 1):
        lines.append(
            f"{i}. \"{song['title']}\" by {song['artist']} "
            f"— {song['genre']}, {song['mood']} mood, "
            f"energy {song['energy']:.2f}, valence {song['valence']:.2f}, "
            f"danceability {song['danceability']:.2f}, "
            f"acousticness {song['acousticness']:.2f}, "
            f"{song['tempo_bpm']:.0f} BPM "
            f"(relevance: {sim:.2f})"
        )
    return "\n".join(lines)


def _build_prompt(user_query: str, songs_context: str) -> str:
    return (
        f"User's request: \"{user_query}\"\n\n"
        f"Retrieved songs from catalog (ranked by relevance):\n{songs_context}\n\n"
        "Please:\n"
        "1. Pick the single best song from the list that fits the user's request.\n"
        "2. Explain in 2-3 sentences WHY it fits — reference specific features "
        "(genre, mood, energy level, tempo, feel).\n"
        "3. Mention 1-2 runner-up alternatives with a brief reason each."
    )


def _call_claude(user_prompt: str) -> str:
    import anthropic
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is not set.")
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=[
            {
                "type": "text",
                "text": _SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


def _call_gemini(user_prompt: str) -> str:
    from google import genai
    from google.genai import types
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set. Get a free key at aistudio.google.com.")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(system_instruction=_SYSTEM_PROMPT),
    )
    return response.text


def generate_recommendation(
    user_query: str,
    retrieved_songs: List[Tuple[Dict, float]],
) -> str:
    """Generate a recommendation using Claude if available, otherwise Gemini."""
    if not user_query.strip():
        raise ValueError("User query cannot be empty.")
    if not retrieved_songs:
        raise ValueError("No songs were retrieved to recommend from.")

    songs_context = _format_songs_context(retrieved_songs)
    user_prompt = _build_prompt(user_query, songs_context)

    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            logger.info(f"Calling Claude | query='{user_query[:60]}'")
            response = _call_claude(user_prompt)
            logger.info(f"Claude responded: {len(response)} chars")
            return response
        except Exception as e:
            logger.warning(f"Claude failed ({e}), falling back to Gemini.")

    logger.info(f"Calling Gemini | query='{user_query[:60]}'")
    response = _call_gemini(user_prompt)
    logger.info(f"Gemini responded: {len(response)} chars")
    return response
