# VibeMatch AI

An applied AI music recommendation system that takes a natural language description of your mood and returns a personalized song recommendation — powered by semantic retrieval (RAG) and Claude Sonnet 4.6.

---

## Original Project

This project extends **VibeMatch 1.0**, built in Module 3 of CodePath AI110. The original system was a rule-based music recommender that scored a catalog of 18 songs against structured user profiles using weighted feature matching across genre, mood, energy, valence, and danceability. It demonstrated how recommendation algorithms work and surfaced known biases — for example, energy dominated scoring so heavily that genre and mood matches could be outweighed by a closer energy value. The original project had no natural language interface and no AI-generated explanations.

---

## What This Project Does

VibeMatch AI extends the Module 3 recommender into a full applied AI system. Instead of filling out a structured profile, you describe what you want in plain English — *"something chill for late-night studying"* or *"upbeat to push through a workout"* — and the system:

1. Converts your description into a semantic embedding
2. Retrieves the most relevant songs from a local catalog using cosine similarity (RAG)
3. Passes those songs to Claude, which picks the best match and explains why
4. Shows a confidence score indicating how decisive the recommendation is
5. Logs every interaction to a local file for auditability

This matters because it demonstrates the full RAG pipeline — retrieval that actively informs generation — rather than a chatbot that answers from training data alone.

---

## System Architecture

```
User Query (natural language)
        │
        ▼
 Streamlit UI (app.py)
        │
        ▼
 RAG Retriever (rag.py)
   ├── Embeds query with sentence-transformers/all-MiniLM-L6-v2
   ├── Compares against pre-built embeddings of all 18 songs
   └── Returns Top 5 most semantically similar songs
        │
        ├──────────────────────────────┐
        ▼                              ▼
 Claude Sonnet 4.6            Reliability Scorer (reliability.py)
 (ai_engine.py)               Computes confidence from similarity gap
 Picks best match +           between top and second result
 explains why                         │
        │                             │
        └──────────┬───────────────────┘
                   ▼
          Streamlit UI displays:
          - Recommendation + explanation
          - RAG retrieved songs (expandable)
          - Confidence: High / Medium / Low
                   │
                   ▼
          logs/app.log (all queries and responses)
```

**Component summary:**

| File | Role |
|---|---|
| `app.py` | Streamlit UI, orchestrates all components |
| `src/rag.py` | Embeds songs and query; retrieves top matches |
| `src/ai_engine.py` | Calls Claude API with retrieved context |
| `src/reliability.py` | Scores how decisive the retrieval result is |
| `src/recommender.py` | Original Module 3 scoring algorithm (preserved) |
| `data/songs.csv` | Local 18-song catalog with audio features |
| `tests/` | 12 pytest tests covering scoring and reliability |
| `logs/app.log` | Auto-generated interaction log |

The diagram image is in [`assets/system_diagram.png`](assets/system_diagram.png).

---

## Reflection and Ethics

### Limitations and Biases

The most significant limitation is the catalog size — 18 songs is far too small for a real recommender. The system cannot recommend across a broad range of moods, subgenres, or cultural contexts, and it will return the same small pool of results regardless of how specific the query is.

The inherited scoring algorithm (from Module 3) has a known bias: energy is weighted at 2x compared to other features, so high-energy queries dominate the results even when genre or mood would be a better signal. A user who wants "intense classical music" would likely receive a metal track because the energy proximity outweighs the genre mismatch.

The embedding model (`all-MiniLM-L6-v2`) was trained on general English text, not music metadata. This means it understands words like "chill" or "energetic" semantically, but has no understanding of what those words actually *sound like* in music. The system also treats genre and mood as flat labels — "lofi" and "ambient" score as completely different even though they share many acoustic qualities.

Finally, there is no diversity mechanism. If a user's query closely matches three lofi songs, the top recommendations will all be lofi — there is no logic to surface variety.

### Potential for Misuse

A music recommender is relatively low-risk, but a few concerns are worth noting. The user query is passed directly into a Claude prompt without sanitization, which creates a prompt injection risk — a crafty user could try to manipulate Claude's output by embedding instructions into their query. Adding input length limits and a content filter before the query reaches the prompt would address this.

The system also logs every query to a local file. If deployed as a public web app, those logs would constitute a record of user behavior, raising privacy concerns. For any public deployment, queries should be anonymized or not stored at all.

### What Surprised Me During Testing

The RAG retrieval was more robust than expected. A one-word query like *"sleepy"* correctly surfaced low-energy, acoustic tracks — the embedding model mapped "sleepy" to features like low tempo, soft acousticness, and calm mood without those words appearing in the song descriptions. I expected keyword-style brittleness but got genuine semantic understanding.

What *didn't* work as expected was the confidence scoring for vague queries. Short, ambiguous inputs like "sleepy" produced low confidence scores because many songs matched closely — the similarity scores between the top five results were clustered together. More specific queries like "upbeat pop song for a morning workout" produced high confidence because the embedding could distinguish clearly between candidates. This confirmed that the confidence score is a genuine signal about query quality, not just a number.

The error handling also surfaced an unintended gap: the generic error message ("check your API key") appeared even when the real cause was insufficient API credits. The error was logged correctly but the user-facing message was misleading — a small but real reliability issue.

### Collaboration with AI

This project was built in collaboration with Claude Code, an AI coding assistant that wrote the initial structure, suggested libraries, debugged errors, and drafted documentation.

**One instance where the AI gave a helpful suggestion:** When the project directory turned out to be a bare git repository (which cannot hold regular files or commits), the AI diagnosed the issue from the error output and proposed a surgical fix — creating a `.git/` subdirectory and moving the git internals into it, then unsetting the `bare` flag. This preserved the remote URL and avoided having to delete and reinitialize the repo from scratch.

**One instance where the AI's suggestion was flawed:** The AI wrote the error handler in `app.py` to display a single generic message — *"Check that your ANTHROPIC_API_KEY is set in .env and try again"* — for all API exceptions. In practice the actual error was insufficient credits, and the generic message pointed in the wrong direction. A better implementation would distinguish between authentication errors, credit errors, and network errors. The AI prioritized simplicity over diagnostic accuracy, which created confusion during testing.

---

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- An [Anthropic API key](https://console.anthropic.com) with available credits

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/yarinacs/applied-ai-system-project
cd applied-ai-system-project

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt
# Note: first run downloads the sentence-transformers model (~80MB)

# 4. Set your API key
cp .env.example .env
# Open .env and replace "your_api_key_here" with your Anthropic API key

# 5. Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`.

### Run tests

```bash
pytest tests/ -v
```

---

## Sample Interactions

### Example 1 — Late-night study session

**Input:** `"something chill and focused for late night studying"`

**RAG retrieved:** Focus Flow (lofi/focused), Library Rain (lofi/chill), Midnight Coding (lofi/chill), Spacewalk Thoughts (ambient/chill), Coffee Shop Stories (jazz/relaxed)

**Confidence:** High

**Claude's recommendation:**
> **Focus Flow** by LoRoom is your best match. It's a lofi track with a focused mood and low energy (0.40), making it ideal for sustained concentration without being distracting. The slow 80 BPM tempo and high acousticness (0.78) create a calm, grounded atmosphere that supports deep work.
>
> Runner-ups: **Library Rain** offers a slightly more subdued feel (energy 0.35) if you want something even quieter, and **Midnight Coding** is a solid alternative with a similar lofi texture and a touch more valence if you need a subtle mood boost.

---

### Example 2 — Morning workout

**Input:** `"high energy upbeat song for a morning run"`

**RAG retrieved:** Gym Hero (pop/intense), Pulse Horizon (edm/euphoric), Iron Collapse (metal/angry), Storm Runner (rock/intense), Crown the Block (hip-hop/confident)

**Confidence:** High

**Claude's recommendation:**
> **Pulse Horizon** by Wavecraft is the perfect pick. It's an EDM track with euphoric mood and near-maximum energy (0.95), a driving 140 BPM tempo, and the highest danceability in the catalog (0.92) — exactly what you need to push through a run.
>
> Runner-ups: **Gym Hero** is a strong pop/intense alternative at 132 BPM if EDM isn't your style, and **Storm Runner** brings heavy rock energy (0.91) for a more aggressive feel.

---

### Example 3 — Rainy afternoon wind-down

**Input:** `"something peaceful and acoustic for a rainy Sunday afternoon"`

**RAG retrieved:** Old Porch Hymn (folk/nostalgic), Spacewalk Thoughts (ambient/chill), Coffee Shop Stories (jazz/relaxed), Library Rain (lofi/chill), Autumn Sonata No. 3 (classical/melancholic)

**Confidence:** Medium

**Claude's recommendation:**
> **Old Porch Hymn** by River Dust fits the mood perfectly. It's a folk track with a nostalgic feel, very high acousticness (0.94), and gentle energy (0.31) — it has the warm, unhurried quality that matches a slow rainy day.
>
> Runner-ups: **Coffee Shop Stories** brings a jazz/relaxed feel that pairs well with rain and coffee, and **Spacewalk Thoughts** is a quieter ambient option if you want something even more atmospheric.

---

## Design Decisions

**Why RAG instead of just passing all songs to Claude?**
The catalog is small enough that passing all 18 songs would technically work, but it defeats the purpose. RAG teaches the system to *retrieve before generating*, which is the pattern that scales to real-world applications with thousands of documents. The retrieval step also makes the system's reasoning transparent — the "RAG: Retrieved songs" expander shows exactly what Claude saw before making its pick.

**Why sentence-transformers instead of keyword matching?**
A keyword search for "peaceful" would miss "relaxed" or "chill". Semantic embeddings capture meaning, so a query like "music for a lazy Sunday" correctly retrieves acoustic low-energy tracks even though those words don't appear in the song descriptions. The `all-MiniLM-L6-v2` model is only ~80MB and runs locally with no API calls.

**Why keep the original Module 3 scoring algorithm?**
The weighted scoring system (`recommender.py`) was the foundation of the original project. Keeping it intact means the Module 3 logic is still present and testable, while the RAG + Claude layer adds natural language understanding on top. The two systems complement each other.

**Why show a confidence score?**
Recommendations without uncertainty signals can feel overconfident. When several songs closely match a vague query, the system should communicate that — it helps users understand that the result might vary and encourages them to look at the runner-ups. This is the reliability component required by the project spec.

**Trade-offs:**
- `sentence-transformers` adds a large dependency and ~1-2 second startup time. The trade-off is genuine semantic search.
- Claude API calls cost money per request. For a production system, caching repeated queries would reduce cost.
- The 18-song catalog is intentionally small for this project. A real system would use a proper vector database (Chroma, Pinecone) instead of in-memory numpy arrays.

---

## Testing Summary

**What was tested:**

| Test file | What it covers |
|---|---|
| `tests/test_recommender.py` | Genre matching boosts score, mood matching boosts score, top-k results returned, results sorted by score, reasons list is populated |
| `tests/test_reliability.py` | Clear winner gives high confidence, near-tie gives low confidence, single result returns 1.0, zero scores return 0.0, score never exceeds 1.0, label thresholds, detail strings |

All 12 tests pass.

**What worked well:**
The scoring algorithm from Module 3 was straightforward to test because it's a pure function — given the same inputs, it always returns the same output. The reliability scorer was similarly easy to unit test since it's just arithmetic on similarity values.

**What was harder:**
Testing the RAG and Claude components end-to-end requires a live API and the embedding model, which makes them unsuitable for fast unit tests. The approach taken was to test the pure logic components (scoring, confidence math) with pytest and leave the integration layer to manual testing through the UI.

**What I learned:**
Separating pure functions from side-effectful code (API calls, file I/O) makes testing significantly easier. The `score_song` and `retrieval_confidence` functions are trivially testable precisely because they take inputs and return outputs with no external dependencies.

---

## Reflection

Building this project changed how I think about what "adding AI" actually means. The original Module 3 recommender was deterministic — the same profile always returned the same songs in the same order. Adding RAG and Claude introduced a new dimension: the system now understands intent, not just structure. A user can say "I'm in a sad mood and want something that matches it" and the system retrieves tracks with low valence and melancholic mood without the user knowing those features exist.

The most important thing I learned is that **generation is only as good as retrieval**. When Claude was given the right songs, its explanations were specific, accurate, and genuinely useful. When the query was vague and the retrieval pulled in loosely-related songs, the recommendation was weaker — not because Claude failed, but because the context it received was ambiguous. This is why RAG systems invest heavily in retrieval quality, not just the language model.

I also learned that reliability and transparency matter as much as correctness. Showing the user *which songs were retrieved* and *how confident the system is* turns a black-box recommendation into something explainable and trustworthy. That shift — from "here's your answer" to "here's how I got there" — feels like the most important design principle I'll carry forward.

---

## Portfolio

**GitHub:** https://github.com/yarinacs/applied-ai-system-project

### What this project says about me as an AI engineer

This project shows that I care about building AI systems that are honest about what they're doing. I didn't just connect a language model to an input box — I built a retrieval layer that grounds every recommendation in real data, added a confidence score that tells users when the system is uncertain, and made the intermediate steps visible in the UI so anyone can see exactly what the AI was given before it answered. I also built the system to survive real-world failure: when the primary API ran out of credits mid-project, I added a Gemini fallback so the app kept working. Throughout this project I was consistently drawn to the questions around transparency and reliability — not just "does the AI answer?" but "does the user understand why, and can they trust it?" That instinct is what I want to bring to every AI system I build.

---
