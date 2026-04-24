import sys
import logging
import urllib.parse
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

        # --- AI recommendation ---
        recommended_song = None
        with st.spinner("Getting AI recommendation..."):
            try:
                response = generate_recommendation(query, retrieved)
                st.subheader("Recommendation")
                st.markdown(response)
                logger.info(f"Recommendation served for query: '{query[:60]}'")
                response_lower = response.lower()
                earliest_pos = len(response_lower)
                for song, _ in retrieved:
                    pos = response_lower.find(song["title"].lower())
                    if pos != -1 and pos < earliest_pos:
                        earliest_pos = pos
                        recommended_song = song
            except Exception as e:
                st.info("AI unavailable — showing top semantic match.")
                logger.error(f"Recommendation failed: {e}", exc_info=True)

        # --- YouTube autoplay for recommended song ---
        play_song = recommended_song or retrieved[0][0]
        youtube_id = play_song.get("youtube_id", "").strip()

        st.divider()
        st.markdown("#### 🎵 Now Playing")
        st.caption(
            f"**{play_song['title']}** by {play_song['artist']} "
            f"· {play_song['genre'].title()} · {play_song['mood']}"
        )

        if youtube_id:
            st.components.v1.html(f"""
            <!DOCTYPE html>
            <html>
            <head>
              <style>
                body {{ margin: 0; padding: 0; background: #000; }}
                #player {{ width: 100%; height: 200px; }}
              </style>
            </head>
            <body>
              <div id="player"></div>
              <script>
                var tag = document.createElement('script');
                tag.src = "https://www.youtube.com/iframe_api";
                document.head.appendChild(tag);

                function onYouTubeIframeAPIReady() {{
                  new YT.Player('player', {{
                    videoId: '{youtube_id}',
                    playerVars: {{
                      autoplay: 1,
                      mute: 1,
                      playsinline: 1,
                      rel: 0
                    }},
                    events: {{
                      onReady: function(e) {{ e.target.playVideo(); }}
                    }}
                  }});
                }}
              </script>
            </body>
            </html>
            """, height=210)
            st.link_button("Open in YouTube ↗", f"https://www.youtube.com/watch?v={youtube_id}")
        else:
            watch_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(play_song['title'] + ' ' + play_song['genre'])}"
            st.link_button("🔍 Find on YouTube", watch_url)
