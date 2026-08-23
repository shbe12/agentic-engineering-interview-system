# Sprint v1 — PRD: AI Mock Interview Agent

## Overview
A full AI-powered mock interview agent that takes a candidate's resume PDF, runs a five-phase adaptive interview (background, Socratic technical deep-dive, second project deep-dive, factual ML questions, behavioral) over text chat and voice, and produces a scored final report.

## Target Users
- Candidates practicing for machine learning engineer interviews.
- The interview creator/operator (running and reviewing sessions).

## Core Features (v1 only)
1. Resume upload + parsing via Claude (native document input, no third-party PDF library) into structured sections and a field classification (NLP / CV / other).
2. Supabase project created and provisioned automatically (via the Management API), with persistence for candidates, sessions, messages, evaluations, and reports.
3. All five interview phases over text chat: (1) background questions, (2) technical deep-dive on the primary project using a Russian-doll/Socratic drill-down, (3) same drill-down on a second project, (4) factual ML questions sourced from a retrieved question bank with a generated fallback, (5) behavioral questions.
4. ML questions bank: the MLQuestions GitHub repo ingested into a local markdown store, embedded with a 384-dim sentence-transformer model, retrieved by similarity search against the candidate's field.
5. Hints in phases 2/3 when the candidate is stuck, factored into evaluation.
6. A fixed "tone of the interviewer" system prompt applied across all phases: professional, concise, no over-enthusiasm.
7. Voice mode: browser mic capture → ElevenLabs Scribe speech-to-text → orchestrator; orchestrator reply → ElevenLabs text-to-speech (voice ID `onwK4e9ZLuTAKqWW03F9`, "Daniel" — a premade voice; the free ElevenLabs tier can't use Professional Voice Clones like the spec's originally-intended cloned voice) → playback.
8. Empathy/anxiety detection: a speaking-rate and disfluency heuristic on the candidate's voice input that triggers a pause-and-reassure turn.
9. Evaluation engine: per-phase scoring (phase 1 none; phases 2/3 a depth+hint-usage metric; phase 4 correctness count; phase 5 an LLM-judged visionary/grounded/team-player score with a penalty for asking no follow-up questions).
10. Final report: aggregated per-phase scores + narrative summary, persisted and rendered in the UI.

## Out of Scope (v2+)
- CI/CD pipeline (GitHub Actions → AWS deploy).
- Anti-cheating system.
- Video-based emotion detection (voice-only for v1).

## Tech Stack
| Component | Technology |
|---|---|
| LLM | Anthropic Claude, model configurable via `ANTHROPIC_MODEL` (default `claude-opus-5`, effort `medium`) — flexible, may change |
| Resume Parsing | Claude native document input (base64 PDF, not pymupdf/pdfplumber) — flexible, may change |
| Speech-to-Text | ElevenLabs Scribe (`scribe_v2`) — Claude has no STT, so this replaced Whisper |
| Text-to-Speech | ElevenLabs (voice ID `onwK4e9ZLuTAKqWW03F9`, "Daniel" — premade, free-tier compatible) |
| Database | Supabase (PostgreSQL), provisioned programmatically via the Management API |
| Embedding Model | 384-dimensional model (`sentence-transformers/all-MiniLM-L6-v2`), run locally |
| Backend | Python + FastAPI |
| Frontend | React (Vite) + Tailwind CSS |
| ML Questions Bank | GitHub: andrewekhalel/MLQuestions + self-generated fallback |
| Secrets | `.env` (git-ignored), sourced from `secrets.md` (also git-ignored) |

## Architecture
Browser (React) talks to the FastAPI backend over REST: resume upload, chat turns, and voice turns. The backend calls out to Claude (parsing, chat) and ElevenLabs (STT + TTS), and reads/writes session and evaluation state in Supabase. The ML question retriever runs in-process in the backend against a locally embedded copy of the MLQuestions repo — no external vector DB needed at this scale.

```
Browser (React) --REST--> FastAPI backend --> Claude (parse/chat)
                                           --> ElevenLabs (Scribe STT + TTS)
                                           --> Supabase (Postgres persistence)
                                           --> local MiniLM embeddings (ML question retrieval)
```

## Success Criteria
- A candidate can upload a real resume and complete a full 5-phase interview via text chat, end to end.
- The same flow works with voice: spoken answers are transcribed correctly and interviewer replies are heard in the configured voice.
- An anxious/fast/stuttering voice answer triggers a visible pause-and-reassure turn at least once during a full run.
- Phase 4 returns relevant retrieved questions when the resume's field matches the question bank, and sensible generated questions otherwise.
- A final report with per-phase scores is persisted in Supabase and renders in the UI after a completed session.
- No API keys or secrets appear in git history or tracked files.
