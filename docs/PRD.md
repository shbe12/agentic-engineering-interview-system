# Sprint v2 — PRD: AI Mock Interview Agent

## Overview
Lets a candidate supply their own Anthropic API key so their interview session's Claude usage bills to their own account instead of the host's shared server-side key, while the app keeps working unchanged for anyone who doesn't.

## Target Users
- Candidates who already hold an Anthropic API key and want to run interviews against their own billing/quota rather than a shared pool.
- The site operator, who wants to open the tool up to more users without the one shared key becoming a cost or rate-limit bottleneck.

## Core Features (v2 only)
1. Settings panel in the frontend where a user can enter and clear their own Anthropic API key. **Default storage is in-memory only** (React state) — the key lives for the current tab/session and is gone on reload or tab close; it is never sent anywhere but this backend and never written to Supabase.
2. Explicit opt-in "Remember on this device" toggle in the same panel — only when a user turns this on does the key additionally persist to browser `localStorage`, surviving a reload. Off by default.
3. Frontend attaches the key as an `X-Anthropic-Api-Key` request header (`frontend/src/api/client.js`) on every interview and resume-upload request whenever one is held in memory (restored from `localStorage` first only if the user opted to remember it).
4. Backend accepts the optional per-request header on `POST /resume/upload`, `POST /interview/start`, `POST /interview/message`, `POST /interview/voice` (`backend/app/routes/`).
5. `backend/app/llm.py` reworked to build a fresh Anthropic client per request from the supplied key — no caching of clients by API key, no global `lru_cache` singleton for the per-user path; `chat_text`/`chat_json` take an optional `api_key` param. Keeps the security model simple: no user secret is ever retained in a process-level cache.
6. The optional key threads through every Claude-calling path that currently calls into `app/llm.py`: `app/interview/orchestrator.py`, `app/evaluation/evaluator.py`, `app/evaluation/report.py`, `app/questions/retriever.py`, `app/resume/parser.py`.
7. Fallback to the host's `ANTHROPIC_API_KEY` (`backend/.env`, `app/config.py`) whenever no per-request key is supplied — default behavior is unchanged for existing users.
8. Lazy key validation: no separate validation call. The first real Claude request naturally validates the key; an Anthropic authentication/billing error (401/403, quota-exceeded) on a user-supplied key is caught and translated into a clear, distinct frontend error rather than a raw 500/stack trace.
9. Frontend indicator showing whether the current session is running on "your key" (and whether it's remembered on this device) or the shared host key.

## Out of Scope (v3+)
- Webcam/non-verbal video signal features — this was the prior v2 scope, now deferred to v3; see `docs/PRD_v3_webcam_backlog.md`.
- Persisting a user's key server-side against an account (this sprint never stores a key at rest in Supabase or anywhere on the backend, regardless of the client-side "remember" choice).
- Per-user usage/cost dashboards or spend tracking.
- Bring-your-own-key for ElevenLabs (voice STT/TTS) — Anthropic only this sprint.
- CI/CD pipeline (carried over from v1, still not addressed).

## Tech Stack
| Component | Technology |
|---|---|
| Key transport | Custom `X-Anthropic-Api-Key` HTTP request header, over HTTPS |
| Key storage (client) | React in-memory state by default (cleared on reload); browser `localStorage` only if the user opts into "Remember on this device" |
| Client construction (server) | Fresh `anthropic.Anthropic(api_key=...)` per request — no caching by key |
| Everything else (LLM, STT/TTS, DB, Backend, Frontend, Embeddings) | Unchanged from v1 — see `docs/WALKTHROUGH_v1.md` |

## Architecture
The browser's Settings panel holds the key in React state; if the user opts into "Remember on this device," it's also written to `localStorage` and restored into that same in-memory state on next load — otherwise the key exists only for the current tab. `frontend/src/api/client.js` reads the in-memory value and attaches it as an `X-Anthropic-Api-Key` header on every request when present. FastAPI route handlers extract the header and pass it down through the interview/evaluation/resume call chain into `app/llm.py`, which builds a fresh Anthropic client from the per-request key if given, falling back to the host's `ANTHROPIC_API_KEY` from `app/config.py` otherwise. No key is cached, persisted, or logged server-side. An auth/billing error from Anthropic on a bad user key is mapped to a clean error response on that same request — no separate validation round-trip.

```
Browser (React state, optionally mirrored to localStorage) --X-Anthropic-Api-Key header (HTTPS)--> FastAPI routes
        |                                                                                                |
        | never sent to Supabase, never logged                                                           v
        |                                                                            orchestrator/evaluator/retriever/parser --> app/llm.py
        |                                                                                                                          |
        +------------------------------------------------------- per-request key builds a fresh client, else fallback to host ANTHROPIC_API_KEY --> Anthropic API
```

## Success Criteria
- A candidate who enters their own key in Settings has that session's Claude calls billed to their key, verifiable in that key's Anthropic console usage.
- By default, the key lives only in browser memory and is gone after a reload; it persists across reloads only if the user explicitly opts into "Remember on this device."
- A candidate who sets no key gets identical behavior to today — same requests, same responses, no visible change.
- An invalid, revoked, or billing-blocked user-supplied key produces a clear, actionable error in the UI on the first real request, not a raw 500 or stack trace.
- No user-supplied key is ever written to Supabase, to server-side logs, or cached in a server-side process.
