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
