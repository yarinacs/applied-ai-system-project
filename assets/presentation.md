# VibeMatch AI — Presentation Slides & Script
**Duration:** 5–7 minutes | **6 slides**

---

## SLIDE 1 — Title

**Slide content:**
> # VibeMatch AI
> ### A Music Recommendation System Powered by RAG + Claude
>
> CodePath AI110 · Applied AI Systems Project
> [Your Name]

**Speaker script (30 sec):**
> "Hi everyone — I'm going to show you VibeMatch AI, a music recommendation system I built for this class. The idea is simple: instead of filling out a structured form to get a song suggestion, you just describe your mood in plain English, and the system finds your perfect match. Under the hood it uses a technique called RAG plus Claude. Let me walk you through how it works and then show you a live demo."

---

## SLIDE 2 — The Problem / What I Built

**Slide content:**
> **The problem with most recommenders:**
> - You fill in a form: genre ✓, mood ✓, energy level ✓
> - The system matches on exact labels
> - No understanding of *what you actually mean*
>
> **What VibeMatch AI does instead:**
> - You type: *"something chill for late-night studying"*
> - The system understands the *intent* and retrieves semantically relevant songs
> - Claude picks the best match and explains *why*

**Speaker script (45 sec):**
> "The original version of this project — from Module 3 — was a rule-based recommender. You gave it a structured profile: genre, mood, energy level — and it returned a ranked list. It worked, but it required the user to already know what they wanted in technical terms. Real people don't think in features. They think in feelings. So the goal of this project was to replace that structured form with a natural language interface, and use AI to bridge the gap between what someone says and what they actually want to hear."

---

## SLIDE 3 — System Architecture

**Slide content:**
> *(paste the diagram from assets/mermaid_diagram.jpg)*
>
> **4 key steps:**
> 1. Your query is converted to a vector embedding
> 2. RAG retrieves the 5 most semantically similar songs
> 3. Claude reads those songs and picks the best fit
> 4. A confidence score shows how decisive the result is

**Speaker script (1 min):**
> "Here's the full architecture. When you type a query, it gets converted into a vector — a list of numbers that captures the meaning of your words — using a model called sentence-transformers. That vector is compared against pre-built embeddings for all 18 songs in the catalog using cosine similarity, and the top 5 are retrieved. This is the RAG step — retrieval-augmented generation. Those 5 songs are passed to Claude as context, and Claude picks the single best match and explains why using specific features like energy, tempo, and mood. The confidence score is calculated from the similarity gap between the top result and the second result — a wide gap means a clear winner, a narrow gap means the query was ambiguous."

---

## SLIDE 4 — Live Demo

**Slide content:**
> **Demo queries:**
> 1. `"something chill and focused for late night studying"` → Focus Flow
> 2. `"high energy upbeat song for a morning run"` → Pulse Horizon
> 3. `"music"` (vague) → watch the confidence drop

**Speaker script (2 min — narrate while clicking through the app):**
> *(Query 1)* "I'll type something specific first — 'something chill and focused for late night studying.' While it's loading, notice the spinner — that's the embedding and retrieval step running. I'll open the RAG expander here — these are the 5 songs that were retrieved before Claude saw anything. Claude then picks from this list, not from the whole catalog, which is why the answer is grounded in real data. The confidence score came out High — you can see the top result stands clearly above the others. And the YouTube player autoplays the recommended song."
>
> *(Query 2)* "Let's try a very different mood — 'high energy upbeat song for a morning run.' Again, High confidence. Completely different songs retrieved, Claude picks Pulse Horizon — 0.95 energy, 140 BPM, euphoric mood. That's exactly what you'd want."
>
> *(Query 3)* "Now I'll type just the word 'music' — the most vague thing possible. Watch the confidence score. Low — because the similarity scores for all 5 retrieved songs are clustered together, there's no clear winner. The system is honestly telling you: I'm not very sure about this one."

---

## SLIDE 5 — What I Learned

**Slide content:**
> **3 things that surprised me:**
>
> 1. **Generation is only as good as retrieval**
>    → When Claude got the right songs, answers were great. Weak retrieval = weak recommendation.
>
> 2. **The confidence score was real signal, not decoration**
>    → Vague queries → clustered scores → Low confidence. Specific queries → spread scores → High.
>
> 3. **AI systems need graceful degradation**
>    → Anthropic credits ran out mid-project. Added a Gemini fallback. The app never went down.

**Speaker script (1 min):**
> "Three things surprised me building this. First — generation is only as good as retrieval. I expected Claude to be the hard part. It wasn't. When retrieval worked well, Claude's explanations were specific and accurate. When retrieval was weak — like for a vague query — the recommendation was weak too, even though Claude was doing its job. The bottleneck was always upstream. Second — the confidence score turned out to be a genuinely useful signal. I added it because the spec required a reliability feature. But testing showed it was actually capturing something true about query quality. And third — my Anthropic API account ran out of credits in the middle of the project. I had to build a Gemini fallback on the spot. That unplanned detour taught me more about production AI engineering than anything I planned to build."

---

## SLIDE 6 — Portfolio & What This Says About Me

**Slide content:**
> **GitHub:** github.com/yarinacs/applied-ai-system-project
>
> ---
>
> *"This project shows that I care about building AI systems that are honest about what they're doing. I didn't just connect a language model to an input box — I built a retrieval layer that grounds every recommendation in real data, added a confidence score that tells users when the system is uncertain, and made the intermediate steps visible so anyone can see what the AI was given before it answered. Throughout this project I was drawn to the questions around transparency and reliability — not just 'does the AI answer?' but 'does the user understand why, and can they trust it?' That instinct is what I want to bring to every AI system I build."*

**Speaker script (30 sec):**
> "The full code, README, model card, and system diagram are on GitHub at that link. If I had to summarize what this project says about me as an AI engineer: I care about transparency. It would have been easier to just show the recommendation and hide everything else. Instead I built in the RAG expander, the confidence score, and the logs — because I think AI systems should be explainable, not just correct. Thanks for listening — happy to answer questions."

---

## Timing Summary

| Slide | Topic | Time |
|---|---|---|
| 1 | Title | 30 sec |
| 2 | Problem / What I built | 45 sec |
| 3 | Architecture | 1 min |
| 4 | Live demo (3 queries) | 2 min |
| 5 | What I learned | 1 min |
| 6 | Portfolio + closing | 30 sec |
| **Total** | | **~5:45** |

---

## Tips

- Open the app **before** presenting so the embedding model is already loaded (first load takes ~5 sec)
- Keep the RAG expander **closed** before clicking — opening it during the demo is the visual payoff
- If the API is slow, narrate the architecture diagram while waiting
- Have a screenshot of the demo as a backup in case of network issues
