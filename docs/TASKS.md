# Tasks — AI Mock Interview Agent v1

- [x] 1. Build the `/prd`, `/dev`, `/walkthrough` skills and generate `docs/PRD.md` + this task list.
      Test: `.claude/skills/{prd,dev,walkthrough}/SKILL.md` exist and `docs/PRD.md` + `docs/TASKS.md` are well-formed. Verified manually.
- [x] 2. Scaffold + Supabase project — git init, backend/frontend skeletons, `.gitignore`, `README.md`; create the Supabase project via the Management API, apply `schema.sql`, wire the DB client.
      Test: query `information_schema.tables` via the Management API and confirm all 5 tables exist. **Passed** — all 5 tables confirmed live on project `skkubowbfwfmpkgqmxij`.
- [x] 3. Resume ingestion — `POST /resume/upload`, Claude-based PDF parsing (base64 document input) into structured sections + field classification, stored in `candidates`.
      Test: `backend/tests/test_resume.py` + `backend/tests/test_resume_parser.py` — passing. **Live-verified with the real resume** (`/mnt/c/Users/Sherline/Downloads/cv.pdf`): correctly extracted name, field (`nlp`), 30 skills, 11 projects; row confirmed in Supabase (`resume_len: 7266`).
- [x] 4. ML questions bank — fetch MLQuestions repo, MiniLM embeddings, field-based similarity retrieval with Claude-generated fallback.
      Test: `backend/tests/test_retriever.py` — passing (3 tests). **Bug found and fixed**: the NLP README uses `### N. Question` headers while the root README uses `#### N) Question` — the parser only handled the second form, silently dropping all NLP questions.
- [x] 5. Interview orchestrator — phase 1–5 state machine, tone-of-interviewer prompt, Socratic/hint logic, text-based end to end.
      Test: `backend/tests/test_orchestrator.py` — passing (4 tests). **Live-verified**: ran a real multi-turn conversation grounded in the actual resume (correctly referenced "kernel methods for permutations and graphs applied to cancer survival prediction", DeepMind/Gemini work, etc.), phase 1→2 transition fired correctly.
- [x] 6. Chat UI (React + Tailwind CSS) — resume upload, transcript, phase indicator, wired to the backend.
      Test: `npm run build` passes; driven with Playwright against the real dev server (renders correctly, no console errors).
- [x] 7. Voice pipeline — ElevenLabs Scribe STT, ElevenLabs TTS, anxiety/disfluency heuristic.
      Test: `backend/tests/test_voice.py` — passing (5 tests). **Live TTS verified**: switched the configured voice from `tAtHhBlA3E0eKZJKNSKE` ("Margot", a Professional Voice Clone — free tier's `professional_voice_limit` is `0`, so it can never work there) to `onwK4e9ZLuTAKqWW03F9` ("Daniel", premade — confirmed working with a real 200 + audio bytes on this account). STT not live-tested (no real audio sample on hand); wrapper logic is unit-verified against the actual installed SDK's response shape.
- [x] 8. Evaluation + final report — per-phase scoring, report generation, report UI.
      Test: `backend/tests/test_evaluator.py` — passing (3 tests). **Live-verified**: ran real evaluation + report generation against a genuine (partially-anomalous) session — correctly identified an empty Phase 2 transcript (score 0, honest note about missing candidate response) vs. a real Phase 5 answer (score 25, specific critique), and produced a well-reasoned "re-interview required" summary rather than hallucinating a plausible score for missing data. Retrieved successfully via the real `GET /interview/{id}/report` endpoint.
- [x] 9. End-to-end pass — run a full interview using the real resume, fix issues found.
      **Text flow fully verified live**: resume upload → parse → start session → multi-turn chat with real phase transition → evaluation → final report, all working against real Claude + Supabase. Two real bugs found and fixed along the way (see below). Voice flow verified at the code/wrapper level; live TTS blocked by an ElevenLabs account limitation (not a code issue — see Known Issues).

## Bugs found and fixed via live testing (not caught by unit tests alone)

1. **CORS headers missing on unhandled exceptions.** `@app.exception_handler(Exception)` runs in Starlette's `ServerErrorMiddleware`, which always sits outside `CORSMiddleware` — so any backend error showed up in the browser as a misleading "CORS policy" error instead of the real one. Fixed with a `@app.middleware("http")` try/except placed before `CORSMiddleware` is added. Test: `test_main.py`.
2. **Interview turns truncated at `effort: "high"`.** Claude Opus 5's adaptive thinking at high effort consumed most of the 4096/16000 token budget on reasoning, truncating the actual JSON reply mid-string. Bumped `MAX_TOKENS` to 16000 (Claude API guidance default) and lowered the default effort to `"medium"` for conversational turns — plenty of quality for interview questions without starving the output.
3. **Event loop blocked during every LLM/DB/voice call.** Route handlers were `async def` but called blocking SDK clients (Anthropic, Supabase, ElevenLabs) directly — found live when `/health` went unresponsive for the full duration of a single `/interview/message` call. Sync-only routes (`start`, `message`, `speak`, `report`) converted to plain `def` (FastAPI runs those in a thread pool automatically); routes needing `await` (file uploads) now run their blocking calls via `run_in_threadpool` instead of inline. Regression test: `test_concurrency.py` (asserts the right routes stay non-async, and that the async ones actually use `run_in_threadpool`) plus live re-verification (`/health` stayed `200` throughout an in-flight message call).

## Resolved issues

- **ElevenLabs TTS 402 on the configured voice** — was pointed at a Professional Voice Clone (`tAtHhBlA3E0eKZJKNSKE`, "Margot"), which this account's free tier can never use via the API (`professional_voice_limit: 0`), regardless of "My Voices" slots. Fixed by switching to a premade voice, `onwK4e9ZLuTAKqWW03F9` ("Daniel") — confirmed working live. The account's free tier also caps at 10,000 TTS characters/month, worth keeping in mind for how many full interviews (with voice replies) fit before hitting the monthly reset.

## Provider swap (mid-sprint change, still v1 scope)

Switched the LLM/parsing provider from OpenAI to **Claude** (default model `claude-opus-5`, configurable via `ANTHROPIC_MODEL`), and STT from OpenAI Whisper to **ElevenLabs Scribe** (Claude has no STT) — TTS was already ElevenLabs. `orchestrator.py`, `evaluator.py`, and `retriever.py` needed no changes — they only call the provider-agnostic `chat_text`/`chat_json` helpers in `llm.py`.

**Note on credentials:** Claude Pro (claude.ai) is a separate product from Anthropic API access — confirmed the key added to `secrets.md` is a real `console.anthropic.com` API key (format `sk-ant-api03-...`), and it works.
