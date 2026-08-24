# AI Mock Interview Agent — Frontend

React (Vite) + Tailwind CSS frontend for the AI Mock Interview Agent. Handles resume upload, the five-phase interview chat (text + voice), and the final report view.

## Setup

```bash
npm install
```

Requires Node 22+ (`nvm alias default 22`).

## Configuration

Copy `.env.example` to `.env` and point `VITE_API_BASE_URL` at the backend:

```
VITE_API_BASE_URL=http://localhost:8000
```

In production this is set as a Vercel environment variable instead, pointing at the deployed backend's URL.

## Running

```bash
npm run dev -- --port 5173
```

## Building

```bash
npm run build
```

See `docs/WALKTHROUGH_v1.md` in the repo root for the full golden-path walkthrough (resume → chat → voice → report) against a running backend.
