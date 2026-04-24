# Model Card — VibeMatch AI

## 1. Model Overview

**Name:** VibeMatch AI  
**Version:** 2.0  
**Type:** Retrieval-Augmented Generation (RAG) recommendation system  
**Built for:** CodePath AI110 Applied AI Systems Project  

VibeMatch AI takes a natural language description of a user's mood and returns a personalized song recommendation from a local 18-song catalog. It combines semantic retrieval using sentence embeddings with Claude Sonnet 4.6 (primary) or Gemini 2.0 Flash (fallback) to generate a recommendation with an explanation.

---

## 2. Intended Use

**Primary use:** Demonstrating a full RAG pipeline — retrieval that actively informs generation — in a music recommendation context.

**Intended users:** Students learning about applied AI systems, developers exploring RAG architecture.

**Out of scope:**
- Production music streaming services
- Recommendations over large catalogs (this system is designed for 18 songs)
- Music discovery for commercial or licensing purposes

---

## 3. How It Works

```
User query (natural language)
        ↓
sentence-transformers/all-MiniLM-L6-v2 embeds the query
        ↓
Cosine similarity retrieves Top 5 songs from songs.csv
        ↓
Claude Sonnet 4.6 reads retrieved songs + picks best match
        ↓
Confidence score = similarity gap between rank-1 and rank-2
        ↓
Result: recommendation text + YouTube autoplay + confidence label
```

**Key components:**

| Component | Technology |
|---|---|
| Semantic retrieval | `sentence-transformers/all-MiniLM-L6-v2` |
| Language model (primary) | Claude Sonnet 4.6 (`claude-sonnet-4-6`) |
| Language model (fallback) | Gemini 2.0 Flash (`gemini-2.0-flash`) |
| UI | Streamlit |
| Logging | Python `logging` → `logs/app.log` |

---

## 4. Training Data and Catalog

The system does **not** train a custom model. It uses:

- **Pre-trained embedding model:** `all-MiniLM-L6-v2` from the `sentence-transformers` library, trained on general English text.
- **Song catalog:** `data/songs.csv` — 18 fictional songs with structured metadata: title, artist, genre, mood, energy (0–1), tempo BPM, valence (0–1), danceability (0–1), acousticness (0–1), and a YouTube video ID.

Song embeddings are built at startup from a text description of each song's features (genre + mood + energy level).

---

## 5. Performance

### What was tested

| Test suite | Coverage |
|---|---|
| `tests/test_recommender.py` | Genre/mood scoring, top-k selection, result ordering, explanation text |
| `tests/test_reliability.py` | High/low confidence cases, single-result edge case, zero-score edge case, label thresholds, detail strings |

**All 12 tests pass.**

### Observed behavior on sample queries

| Query | Top retrieval | Confidence |
|---|---|---|
| "chill focused for studying" | Focus Flow (lofi/focused) | High |
| "upbeat morning run" | Pulse Horizon (edm/euphoric) | High |
| "peaceful acoustic Sunday" | Old Porch Hymn (folk/nostalgic) | Medium |
| "music" (vague) | Results clustered, low gap | Low |

Specific queries produce high-confidence results. Vague one-word queries cause similarity scores to cluster, which correctly produces Low confidence.

---

## 6. Limitations

**Catalog size:** 18 songs is far too small for a real recommender. Users with niche preferences will receive poor-fit results.

**Energy bias (inherited from Module 3):** The original scoring algorithm weights energy at 2× compared to mood and genre. This was preserved but not used in the RAG path — however, the scored catalog was shaped by it when choosing representative songs.

**Flat genre/mood labels:** "lofi" and "ambient" score as completely different genres even though they share acoustic qualities. There is no genre hierarchy or similarity.

**No diversity mechanism:** Multiple closely-matching songs of the same genre will all appear in the top results. There is no logic to surface variety.

**General-purpose embeddings:** `all-MiniLM-L6-v2` was trained on general text, not music. It understands words semantically but has no knowledge of what music actually sounds like.

**Prompt injection risk:** User queries are passed directly into the Claude prompt without sanitization. A crafted input could attempt to manipulate the model's output.

---

## 7. Ethical Considerations

**Privacy:** Every user query is logged to `logs/app.log`. In any public deployment, queries should be anonymized or not retained.

**Transparency:** The UI shows the retrieved songs in an expandable section so users can see exactly what context the AI was given before it answered. The confidence score surfaces uncertainty rather than hiding it.

**AI fallback disclosure:** When Claude is unavailable, the system silently falls back to Gemini. A production system should disclose which model is responding.

**Bias acknowledgment:** The catalog of 18 songs reflects the choices of one developer and does not represent diverse musical cultures, languages, or traditions. Any real system would need deliberate curation for diversity.

---

## 8. Reflection on Engineering Process

Building VibeMatch AI taught me that the hardest part of a RAG system is not the language model — it is getting retrieval right. When Claude received well-matched songs, its explanations were specific and useful. When the retrieval was weak, the recommendation was weak too, even though Claude was working correctly. The bottleneck was always upstream.

I also learned that real systems fail in unexpected ways. My Anthropic API account ran out of credits mid-project. Adding a Gemini fallback was a pragmatic fix, but it also taught me something important: production AI systems need graceful degradation, not just a happy path. The error handling I wrote early (a generic "check your API key" message) was wrong because it conflated three different failure modes — missing key, invalid key, and no credits. Precision in error handling matters because it's the only signal the user has when something goes wrong.

The confidence score was the feature I was most skeptical about. I expected it to be a cosmetic addition. Instead, it turned out to be a genuine signal: vague queries produced clustered similarity scores → Low confidence; specific queries spread the scores out → High confidence. The score was correctly capturing something real about query quality.

---

## 9. Responsible AI Checklist

- [x] Limitations are documented
- [x] Potential biases are identified
- [x] User-facing uncertainty is communicated (confidence score)
- [x] Intermediate reasoning is visible (RAG expander shows retrieved songs)
- [x] Logs are written locally (not to external services)
- [x] Input length is bounded by the text input component
- [ ] Input sanitization against prompt injection (not yet implemented)
- [ ] Model identity disclosed when fallback is used (not yet implemented)
