# Tasks — AI Mock Interview Agent v1

- [x] 1. Build the `/prd`, `/dev`, `/walkthrough` skills and generate `docs/PRD.md` + this task list.
      Test: `.claude/skills/{prd,dev,walkthrough}/SKILL.md` exist and `docs/PRD.md` + `docs/TASKS.md` are well-formed. Verified manually.
- [x] 2. Scaffold + Supabase project — git init, backend/frontend skeletons, `.gitignore`, `README.md`; create the Supabase project via the Management API, apply `schema.sql`, wire the DB client.
      Test: query `information_schema.tables` via the Management API and confirm all 5 tables exist. **Passed** — `candidates`, `interview_sessions`, `interview_messages`, `phase_evaluations`, `final_reports` all confirmed live on project `skkubowbfwfmpkgqmxij`.
- [ ] 3. Resume ingestion — `POST /resume/upload`, OpenAI-based PDF parsing into structured sections + field classification, stored in `candidates`.
      Test: `backend/tests/test_resume.py` — mock `parse_resume_pdf` + Supabase, hit the route via `TestClient`, assert 200 and a `candidates` row is inserted with the right shape. *(not yet written — needs `httpx`/`fastapi.testclient`, blocked on pip)*
- [ ] 4. ML questions bank — fetch MLQuestions repo (done, `data/ml_questions.md` generated), MiniLM embeddings, field-based similarity retrieval with GPT fallback.
      Test: `backend/tests/test_retriever.py` — `_parse_markdown` on the real fetched file returns non-empty `nlp`/`cv` entries; `retrieve_questions` (embedder mocked or real, TBD) returns `k` results without raising. *(not yet written — needs `numpy`, blocked on pip)*
- [ ] 5. Interview orchestrator — phase 1–5 state machine, tone-of-interviewer prompt, Socratic/hint logic, text-based end to end.
      Test: `backend/tests/test_orchestrator.py` — written (phase stays/advances/completes, report triggered on phase 5). *(written, not yet run — blocked on pip for `pytest`/`fastapi`/`openai`/`supabase` imports)*
- [ ] 6. Chat UI (React + Tailwind CSS) — resume upload, transcript, phase indicator, wired to the backend.
      Test: `npm run build` passes. **Passed.** Full wire-up (upload → chat → report against a live backend) still needs a scripted manual walkthrough once the backend can run.
- [ ] 7. Voice pipeline — Whisper STT, ElevenLabs TTS, anxiety/disfluency heuristic.
      Test: `app.voice.anxiety.detect_anxiety` — fast speech, calm speech, and disfluent speech each classified correctly. **Passed** (ran directly with plain `python3`, no deps needed — see below). STT/TTS wrappers themselves still need `openai`/`elevenlabs` installed to test.
- [ ] 8. Evaluation + final report — per-phase scoring, report generation, report UI.
      Test: `backend/tests/test_evaluator.py` — written (phase 1 no-eval, unreached phase, LLM-judged phase 2 scoring persisted). *(written, not yet run — blocked on pip)*
- [ ] 9. End-to-end pass — run a full interview (text + voice) using the real resume at `/mnt/c/Users/Sherline/Downloads/cv.pdf`, fix issues found.
      Test: manual scripted walkthrough of the golden path against both running servers. *(blocked until 3–8 can run)*

**Blocker on 3, 4, 5, 8, 9 and full verification of 6:** this machine has no `pip`/`venv` for Python and installing needs `sudo` (password required). Run once, then these can proceed:
```
sudo apt-get update && sudo apt-get install -y python3-pip python3.14-venv
```
