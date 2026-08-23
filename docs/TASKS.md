# Tasks — AI Mock Interview Agent v1

- [x] 1. Build the `/prd`, `/dev`, `/walkthrough` skills and generate `docs/PRD.md` + this task list.
- [x] 2. Scaffold + Supabase project — git init, backend/frontend skeletons, `.gitignore`, `README.md`; Supabase project created via the Management API (`skkubowbfwfmpkgqmxij`), `schema.sql` applied and verified (5 tables confirmed), DB client wired.
- [ ] 3. Resume ingestion — `POST /resume/upload`, OpenAI-based PDF parsing into structured sections + field classification, stored in `candidates`. *(code written, syntax-checked; not yet runtime-verified — blocked on backend deps, see below)*
- [ ] 4. ML questions bank — fetch MLQuestions repo (done, `data/ml_questions.md` generated), MiniLM embeddings, field-based similarity retrieval with GPT fallback. *(code written; retrieval not yet runtime-verified)*
- [ ] 5. Interview orchestrator — phase 1–5 state machine, tone-of-interviewer prompt, Socratic/hint logic, text-based end to end. *(code written + unit tests written; tests not yet run)*
- [ ] 6. Chat UI (React) — resume upload, transcript, phase indicator, wired to the backend. *(code written, `npm run build` passes; not yet exercised against a running backend)*
- [ ] 7. Voice pipeline — Whisper STT, ElevenLabs TTS, anxiety/disfluency heuristic. *(code written; not yet runtime-verified)*
- [ ] 8. Evaluation + final report — per-phase scoring, report generation, report UI. *(code written + unit tests written; tests not yet run)*
- [ ] 9. End-to-end pass with the real resume, fix issues found. *(blocked until 3–8 can actually run)*

**Blocker on 3–9:** this machine has no `pip`/`venv` for Python and installing needs `sudo` (password required). Run once, then tasks 3–9 can proceed:
```
sudo apt-get update && sudo apt-get install -y python3-pip python3.14-venv
```
