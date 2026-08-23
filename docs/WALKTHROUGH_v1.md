# Walkthrough — Sprint v1: AI Mock Interview Agent

## What shipped

All 10 Core Features from `docs/PRD.md` landed and were live-verified against real services (Claude, Supabase, ElevenLabs) — not just unit tests:

1. Resume upload + parsing via Claude's native PDF document input — live-tested with a real resume (`/mnt/c/Users/Sherline/Downloads/cv.pdf`): correctly extracted name, field classification (`nlp`), 30 skills, 11 projects.
2. Supabase project provisioned programmatically via the Management API (project `skkubowbfwfmpkgqmxij`), all 5 tables (`candidates`, `interview_sessions`, `interview_messages`, `phase_evaluations`, `final_reports`) confirmed live.
3. All five interview phases over text chat, with the Russian-doll/Socratic drill-down for phases 2/3 — live-verified with a real multi-turn conversation that correctly referenced specific resume details and transitioned phase 1 → 2 on its own.
4. ML questions bank (MLQuestions GitHub repo → MiniLM embeddings → field-based retrieval, GPT-style fallback now via Claude) — live-verified, including a real bug fix (see below).
5. Hints in phases 2/3 when the candidate is stuck.
6. Fixed tone-of-interviewer system prompt across all phases.
7. Voice mode: ElevenLabs Scribe (STT) + ElevenLabs TTS — both live-verified against the real API.
8. Empathy/anxiety detection heuristic (speaking rate + disfluency) — unit-verified with real assertions, no deps needed.
9. Evaluation engine (per-phase scoring rules from the PRD) — live-verified against a real (partially incomplete) session; correctly distinguished a missing transcript (score `null`/`0`, honest note) from an actual answer (specific score + critique) rather than hallucinating.
10. Final report generation + persistence + retrieval via the real `GET /interview/{id}/report` endpoint.

**Provider swap mid-sprint (still v1 scope):** switched from OpenAI to **Claude** (chat + resume parsing) and **ElevenLabs Scribe** (STT, since Claude has none) per your request — see `docs/TASKS.md` for the full rationale.

**Nothing from Core Features was dropped.** Two real bugs were found only by actually running the app (not caught by unit tests) and are already fixed — see `docs/TASKS.md` for details: (1) unhandled backend errors were showing up in the browser as misleading CORS errors instead of the real message, (2) the whole server froze during every LLM call because blocking SDK calls ran inside `async def` routes.

## Setup

From a clean checkout:

**Already provisioned for you** — you don't need to do these:
- Supabase project + schema (created via Management API).
- `ELEVENLABS_API_KEY` (already in `secrets.md` / `backend/.env`).
- `ANTHROPIC_API_KEY` (already added — note: a Claude Pro/claude.ai subscription is a *separate* product from Anthropic API access; this needs a real `console.anthropic.com` key with its own billing).

**You still need to do:**

```bash
# Backend
cd backend
python3 -m venv .venv                        # if not already created
.venv/bin/pip install -r requirements.txt
# backend/.env already exists and is filled in — don't overwrite it blindly

# Frontend
cd ../frontend
npm install
# requires Node 22+ — this repo pins `nvm alias default 22`
```

If `data/ml_questions.md` is ever missing, regenerate it with:
```bash
cd backend && .venv/bin/python -m app.questions.fetch_ml_questions
```

## Running it

```bash
# Terminal 1 — backend
cd backend
.venv/bin/uvicorn app.main:app --reload --port 8000
# API docs: http://localhost:8000/docs
# Health check: http://localhost:8000/health

# Terminal 2 — frontend
cd frontend
npm run dev -- --port 5173
# App: http://localhost:5173
```

Both are running right now as part of writing this walkthrough:
- **Frontend:** http://localhost:5173
- **Backend API docs:** http://localhost:8000/docs

## Golden path walkthrough

1. Open **http://localhost:5173**. You should see "AI Mock Interview Agent" with a resume upload form.
2. Choose a PDF resume and click **Start**. This calls `POST /resume/upload`, which sends the PDF to Claude for parsing (structured sections + field classification) and stores the result in Supabase `candidates`. Takes a few seconds.
3. You'll land on a "Hi `<name>`" screen showing the detected field (`nlp` / `cv` / `other`). Click **Begin interview**.
4. You're now in the chat view. The interviewer opens with a background question grounded in your actual resume content. A **phase indicator** (1–5) shows progress across the top.
5. Type an answer and hit **Send** — or click **🎙 Answer by voice** to record and send a spoken answer instead (transcribed via ElevenLabs Scribe; the interviewer's replies play back via ElevenLabs TTS if "Play interviewer voice" is checked).
6. Keep answering. Phase 1 (background) runs 2–3 exchanges before moving to Phase 2 (Socratic drill-down on your primary project), then Phase 3 (second project), Phase 4 (factual ML questions pulled from the question bank or generated), then Phase 5 (behavioral questions).
7. If you speak too fast or with a lot of filler words/repetition, a yellow banner appears acknowledging it and the interviewer pauses to reassure you before continuing — that's the anxiety-detection heuristic.
8. After Phase 5 completes, the app automatically switches to the **report view** and polls until the final report is ready (a few seconds — it's evaluating all 5 phases via Claude in sequence). You'll see a narrative summary plus a score per phase.

Everything in steps 2–8 has been exercised against the real backend and real Claude/Supabase/ElevenLabs calls during development — see `docs/TASKS.md` for the specific verification evidence per step.

## Known limitations / not done

Out of scope for v1 (per `docs/PRD.md`):
- CI/CD pipeline (GitHub Actions → AWS deploy).
- Anti-cheating system.
- Video-based emotion detection (voice-only for v1).

Discovered during `/dev` that's worth knowing about, not blocking:
- The interviewer's TTS voice ("Daniel") is a premade ElevenLabs voice, not a personal clone — the free ElevenLabs tier can't use Professional Voice Clones via the API at all. Upgrading the ElevenLabs plan would unlock a cloned voice if wanted.
- ElevenLabs free tier caps at 10,000 TTS characters/month — worth watching if running several full interviews with voice replies enabled.
- There's minor redundant phrasing when a phase transitions (the closing line of one phase and the opening line of the next can both say something like "let's move into the technical portion") — cosmetic, not incorrect.

## Automated end-to-end suite

`e2e/e2e_test.py` (Playwright, driven against real Claude/Supabase/ElevenLabs — not mocked) now passes 10/10, including the browser → real audio fixture → `/interview/voice` → ElevenLabs Scribe STT path that was previously only unit-verified. Run it yourself with both servers up:

```bash
backend/.venv/bin/python e2e/e2e_test.py
```

Screenshots land in `e2e/screenshots/` (gitignored — regenerate by re-running). See `docs/TASKS.md` task 9 for what's covered and a selector bug that was found and fixed in the test script itself.

## Next version

Not yet scoped — run `/prd` when you're ready to define v2 (candidates: CI/CD, anti-cheating, or whatever's next on your list).
