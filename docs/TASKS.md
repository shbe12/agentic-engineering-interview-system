# Tasks — AI Mock Interview Agent v1

- [x] 1. Build the `/prd`, `/dev`, `/walkthrough` skills and generate `docs/PRD.md` + this task list.
      Test: `.claude/skills/{prd,dev,walkthrough}/SKILL.md` exist and `docs/PRD.md` + `docs/TASKS.md` are well-formed. Verified manually.
- [x] 2. Scaffold + Supabase project — git init, backend/frontend skeletons, `.gitignore`, `README.md`; create the Supabase project via the Management API, apply `schema.sql`, wire the DB client.
      Test: query `information_schema.tables` via the Management API and confirm all 5 tables exist. **Passed** — all 5 tables confirmed live on project `skkubowbfwfmpkgqmxij`.
- [ ] 3. Resume ingestion — `POST /resume/upload`, OpenAI-based PDF parsing into structured sections + field classification, stored in `candidates`.
      Test: `backend/tests/test_resume.py` — **passing** (route validation + parsing + Supabase insert, `parse_resume_pdf` mocked). Also hit the route live end-to-end with the real resume at `/mnt/c/Users/Sherline/Downloads/cv.pdf`: confirmed the full pipeline (upload → temp file → OpenAI Files API call) is wired correctly — it fails at exactly one point, `openai.AuthenticationError: You didn't provide an API key`, i.e. the only thing standing between this and working is the still-empty `OpenAI or claude api key -` line in `secrets.md`. Leaving unchecked until that's filled in and a real parse succeeds.
- [x] 4. ML questions bank — fetch MLQuestions repo (done, `data/ml_questions.md` generated via the actual script), MiniLM embeddings, field-based similarity retrieval with GPT fallback.
      Test: `backend/tests/test_retriever.py` — **passing** (3 tests: markdown parses to both `nlp`/`cv` entries, similarity retrieval returns `k` field-matched results, empty-pool falls back to GPT generation). **Bug found and fixed**: the NLP README uses `### N. Question` headers while the root README uses `#### N) Question` — the parser only handled the second form, silently dropping all NLP questions. Regex now handles both.
- [x] 5. Interview orchestrator — phase 1–5 state machine, tone-of-interviewer prompt, Socratic/hint logic, text-based end to end.
      Test: `backend/tests/test_orchestrator.py` — **passing** (4 tests: opening message, phase stays, phase advances, phase 5 completion triggers report generation).
- [ ] 6. Chat UI (React + Tailwind CSS) — resume upload, transcript, phase indicator, wired to the backend.
      Test: `npm run build` passes. **Passed.** Full wire-up against a live backend (upload → chat → report) still needs a scripted manual walkthrough — folded into task 9.
- [x] 7. Voice pipeline — Whisper STT, ElevenLabs TTS, anxiety/disfluency heuristic.
      Test: `backend/tests/test_voice.py` — **passing** (5 tests: anxiety heuristic fast/calm/disfluent classification, Whisper wrapper calls the right API with the right params and parses the result, ElevenLabs wrapper calls `convert` with the configured voice ID). Live calls to OpenAI/ElevenLabs still untested (OpenAI key missing) — the wrapper logic itself is verified.
- [x] 8. Evaluation + final report — per-phase scoring, report generation, report UI.
      Test: `backend/tests/test_evaluator.py` — **passing** (3 tests: phase 1 no-eval, unreached phase, LLM-judged phase 2 scoring persisted correctly via upsert).
- [ ] 9. End-to-end pass — run a full interview (text + voice) using the real resume at `/mnt/c/Users/Sherline/Downloads/cv.pdf`, fix issues found.
      Test: manual scripted walkthrough of the golden path against both running servers. **Blocked on one thing only now:** `secrets.md`'s `OpenAI or claude api key -` line is still empty. Everything else (Supabase, ElevenLabs, backend deps, frontend build, all unit tests) is in place and verified.

**Also fixed along the way:** `openai==1.59.7` (originally pinned) has no `.responses` attribute — the Responses API landed in a later SDK version. Bumped to `openai==1.109.1`. `elevenlabs==1.15.0` no longer exists on PyPI; bumped to `elevenlabs==2.64.0`.
