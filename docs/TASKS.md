# Tasks — AI Mock Interview Agent v1

- [x] 1. Build the `/prd`, `/dev`, `/walkthrough` skills and generate `docs/PRD.md` + this task list.
      Test: `.claude/skills/{prd,dev,walkthrough}/SKILL.md` exist and `docs/PRD.md` + `docs/TASKS.md` are well-formed. Verified manually.
- [x] 2. Scaffold + Supabase project — git init, backend/frontend skeletons, `.gitignore`, `README.md`; create the Supabase project via the Management API, apply `schema.sql`, wire the DB client.
      Test: query `information_schema.tables` via the Management API and confirm all 5 tables exist. **Passed** — all 5 tables confirmed live on project `skkubowbfwfmpkgqmxij`.
- [ ] 3. Resume ingestion — `POST /resume/upload`, Claude-based PDF parsing (base64 document input) into structured sections + field classification, stored in `candidates`.
      Test: `backend/tests/test_resume.py` (route) + `backend/tests/test_resume_parser.py` (document-block shape sent to Claude) — **both passing**. Also hit the route live end-to-end with the real resume at `/mnt/c/Users/Sherline/Downloads/cv.pdf`: confirmed the full pipeline (upload → temp file → base64 → Claude Messages API call) is wired correctly — fails at exactly one point, `Could not resolve authentication method`, i.e. the only thing standing between this and working is `ANTHROPIC_API_KEY`. Leaving unchecked until that's filled in and a real parse succeeds.
- [x] 4. ML questions bank — fetch MLQuestions repo (done, `data/ml_questions.md` generated via the actual script), MiniLM embeddings, field-based similarity retrieval with GPT-style fallback (now via Claude).
      Test: `backend/tests/test_retriever.py` — **passing** (3 tests). **Bug found and fixed**: the NLP README uses `### N. Question` headers while the root README uses `#### N) Question` — the parser only handled the second form, silently dropping all NLP questions. Regex now handles both.
- [x] 5. Interview orchestrator — phase 1–5 state machine, tone-of-interviewer prompt, Socratic/hint logic, text-based end to end.
      Test: `backend/tests/test_orchestrator.py` — **passing** (4 tests). Unaffected by the LLM provider swap — it calls the provider-agnostic `chat_json`/`chat_text` helpers, not Claude/OpenAI directly.
- [ ] 6. Chat UI (React + Tailwind CSS) — resume upload, transcript, phase indicator, wired to the backend.
      Test: `npm run build` passes. **Passed.** Also drove it with Playwright against the real dev server: initial screen renders correctly styled (Tailwind confirmed working), no console errors. Full wire-up against a live backend (upload → chat → report) still needs a scripted manual walkthrough — folded into task 9.
- [x] 7. Voice pipeline — ElevenLabs Scribe STT (switched from Whisper — Claude has no STT), ElevenLabs TTS, anxiety/disfluency heuristic.
      Test: `backend/tests/test_voice.py` — **passing** (5 tests: anxiety heuristic fast/calm/disfluent classification, Scribe wrapper calls the right API with the right params and parses the result — including filtering non-word `audio_event`/`spacing` tokens out of the word count, ElevenLabs TTS wrapper calls `convert` with the configured voice ID).
- [x] 8. Evaluation + final report — per-phase scoring, report generation, report UI.
      Test: `backend/tests/test_evaluator.py` — **passing** (3 tests).
- [ ] 9. End-to-end pass — run a full interview (text + voice) using the real resume at `/mnt/c/Users/Sherline/Downloads/cv.pdf`, fix issues found.
      Test: manual scripted walkthrough of the golden path against both running servers. **Blocked on one thing only now:** `ANTHROPIC_API_KEY` is still empty in `backend/.env`. Everything else (Supabase, ElevenLabs, backend deps, frontend build + render, all unit tests) is in place and verified.

## Provider swap (mid-sprint change, still v1 scope)

Switched the LLM/parsing/STT provider from OpenAI to **Claude + ElevenLabs Scribe** (ElevenLabs TTS was already in place) per explicit request — not a new feature, a substitution across `llm.py`, `resume/parser.py`, `voice/stt.py` (+ new shared `voice/client.py`), `config.py`, `requirements.txt`, `.env.example`/`.env`, and the PRD's Tech Stack/Architecture sections. `orchestrator.py`, `evaluator.py`, and `retriever.py` needed **no changes** — they only call the provider-agnostic `chat_text`/`chat_json` helpers.

**Note on credentials:** Claude Pro (claude.ai) is a separate product from Anthropic API access — a Pro subscription does not by itself grant `ANTHROPIC_API_KEY` access. A key needs to come from `console.anthropic.com/settings/keys`, with its own billing.

**Also fixed along the way (found by actually running the app, not just unit tests):**
- Unhandled backend exceptions were bypassing `CORSMiddleware` entirely (Starlette's `@app.exception_handler(Exception)` runs in `ServerErrorMiddleware`, which always sits outside CORS), so the browser reported a misleading "CORS policy" error instead of the real one for *any* backend error. Fixed with a proper `@app.middleware("http")` try/except placed before `CORSMiddleware` is added. Regression test: `backend/tests/test_main.py`.
- `openai==1.59.7` (used before the provider swap) had no `.responses` attribute — the Responses API landed in a later SDK version; had bumped to `1.109.1` before removing OpenAI entirely.
- `elevenlabs==1.15.0` no longer exists on PyPI; bumped to `elevenlabs==2.64.0`.
