# AI Mock Interview Agent

Full-stack AI mock interview agent: resume-aware, five-phase adaptive interview (text + voice), with automated evaluation and a final report. See [`docs/PRD.md`](docs/PRD.md) for scope and [`docs/TASKS.md`](docs/TASKS.md) for build progress.

## Prerequisites

- Python 3.11+ with `pip`/`venv` available (installed via `sudo apt-get install -y python3-pip python3.14-venv`).
- Node.js 22+ (this repo pins `nvm alias default 22`).
- An Anthropic API key (fill into `backend/.env`, see `backend/.env.example` — **currently blank**, nothing that calls Claude will work until this is set). Note: a Claude Pro (claude.ai) subscription does **not** grant this — get a key with its own billing from `console.anthropic.com/settings/keys`.
- ElevenLabs (used for both speech-to-text via Scribe and text-to-speech) and Supabase are already provisioned (see `backend/.env`).

## Backend

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # already pre-filled for this project — don't overwrite blindly
python -m app.questions.fetch_ml_questions   # only needed if data/ml_questions.md is missing
.venv/bin/uvicorn app.main:app --reload
```

API docs at http://localhost:8000/docs.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

App at http://localhost:5173.

## Tests

```bash
cd backend
.venv/bin/pytest
```

## Planned: bring your own API key

Right now every call to Claude runs off one server-side key (`ANTHROPIC_API_KEY` in `backend/.env`), shared by all users via a cached singleton client (`get_anthropic_client()` in `backend/app/llm.py`). The plan is to let a user supply their own Anthropic key instead, so their usage bills to their own account rather than the host's.

1. **Transport** — accept the key as an `X-Anthropic-Api-Key` request header on the interview endpoints (`backend/app/routes/interview.py`: `/start`, `/message`, `/voice`) and resume upload (`backend/app/routes/resume.py`: `/upload`). Never accept it as a query param or persist it in Supabase.
2. **Backend plumbing** — thread the per-request key from the route handler down through `app/interview/orchestrator.py`, `app/evaluation/evaluator.py`, `app/evaluation/report.py`, `app/questions/retriever.py`, and `app/resume/parser.py` into `app/llm.py`. `chat_text`/`chat_json`/`get_anthropic_client` need an optional `api_key` param — `lru_cache` on `get_anthropic_client` has to go (or be keyed by the caller's key) since it currently assumes one global client. Fall back to `settings.anthropic_api_key` when no per-request key is present, so the app still works out of the box.
3. **Validation** — on first use of a user-supplied key, make a cheap Anthropic call (or catch the 401) and surface a clear error back through the API rather than a raw exception.
4. **Frontend** — add a settings entry (e.g. a small "Use your own API key" panel) that stores the key in `localStorage` only, never sends it anywhere but this backend, and attaches it as a header from `frontend/src/api/client.js` on every request when present.
5. **Cost/rate-limit isolation** — once BYOK exists, usage on a user-supplied key no longer needs to count against the host's rate limits or budget alerts, if any exist.

Not started — no code changes yet, this is a planning note for the next sprint.
