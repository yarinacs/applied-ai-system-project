import sys
import logging
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

# Ensure logs directory exists before configuring file handler
_LOG_DIR = Path(__file__).parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(_LOG_DIR / "app.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from src.recommender import load_songs
from src.rag import build_song_index, retrieve_songs
from src.ai_engine import generate_recommendation
from src.reliability import retrieval_confidence, confidence_label, confidence_detail

_DATA_PATH = Path(__file__).parent / "data" / "songs.csv"


@st.cache_resource
def get_song_index():
    songs = load_songs(str(_DATA_PATH))
    songs_list, embeddings = build_song_index(songs)
    return songs_list, embeddings


st.set_page_config(page_title="VibeMatch AI", page_icon="🎵", layout="centered")

st.title("VibeMatch AI")
st.caption("Describe your mood — AI finds your perfect song from a local catalog")

with st.sidebar:
    st.header("How it works")
    st.markdown("""
**1. You describe your mood**
Type what you're looking for in plain language.

**2. RAG retrieval**
The system semantically searches a local 18-song catalog and finds the most relevant matches using sentence embeddings.

**3. Claude AI recommends**
Claude reads the retrieved songs and picks the best fit, explaining why using specific song features.

**4. Confidence score**
Shows how decisive the recommendation is — based on the similarity gap between the top match and alternatives.
""")
    st.divider()
    st.caption("Built with Claude Sonnet 4.6 · sentence-transformers · VibeMatch scoring")

query = st.text_input(
    "What are you in the mood for?",
    placeholder="e.g. chill background for studying, upbeat for a morning run, sad late-night vibes...",
)

if st.button("Get Recommendation", type="primary"):
    if not query.strip():
        st.warning("Please describe what you're in the mood for first.")
    else:
        songs, embeddings = get_song_index()

        with st.spinner("Searching catalog..."):
            retrieved = retrieve_songs(query, songs, embeddings, k=5)

        with st.expander("RAG: Retrieved songs from catalog", expanded=False):
            st.caption("These are the songs the retrieval system surfaced before Claude made its pick.")
            for song, sim in retrieved:
                st.markdown(
                    f"**{song['title']}** by {song['artist']}  \n"
                    f"{song['genre'].title()} · {song['mood']} · "
                    f"energy {song['energy']:.2f} · similarity {sim:.2f}"
                )

        conf = retrieval_confidence(retrieved)
        label = confidence_label(conf)
        detail = confidence_detail(conf)

        col1, col2 = st.columns([1, 3])
        col1.metric("Confidence", label, help="How clearly the top match stands out from alternatives")
        col2.caption(f"_{detail}_")

        with st.spinner("Asking Claude for a recommendation..."):
            try:
                response = generate_recommendation(query, retrieved)
                st.subheader("Recommendation")
                st.markdown(response)
                logger.info(f"Recommendation served for query: '{query[:60]}'")
            except ValueError as e:
                st.error(str(e))
                logger.error(f"Validation error: {e}")
            except Exception as e:
                st.error("Something went wrong. Check that your ANTHROPIC_API_KEY is set in .env and try again.")
                logger.error(f"Recommendation failed: {e}", exc_info=True)
