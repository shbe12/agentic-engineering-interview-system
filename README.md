# AI Mock Interview Agent

Full-stack AI mock interview agent: resume-aware, five-phase adaptive interview (text + voice), with automated evaluation and a final report. See [`docs/PRD.md`](docs/PRD.md) for scope and [`docs/TASKS.md`](docs/TASKS.md) for build progress.

## Prerequisites

- Python 3.11+ with `pip`/`venv` available (`sudo apt-get install -y python3-pip python3.14-venv` on this box — not yet installed).
- Node.js 22+ (this repo pins `nvm alias default 22`).
- An OpenAI API key with access to the configured chat model + Whisper (fill into `backend/.env`, see `backend/.env.example` — **currently blank**, nothing that calls GPT or Whisper will work until this is set).
- ElevenLabs and Supabase are already provisioned (see `backend/.env`).

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
