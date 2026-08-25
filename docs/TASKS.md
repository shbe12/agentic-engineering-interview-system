# Tasks — AI Mock Interview Agent v2

This is the task breakdown for `docs/PRD.md` Sprint v2 (bring your own API key). Confirmed decisions going in: no server-side caching of Anthropic clients by key (fresh client per request), lazy validation (the first real Claude call validates the key; no separate validation ping), and key storage defaults to in-memory only on the client, with `localStorage` used only behind an explicit "Remember on this device" opt-in.

- [ ] 1. Backend: accept optional `X-Anthropic-Api-Key` header on `/resume/upload`, `/interview/start`, `/interview/message`, `/interview/voice`.
      Test: `backend/tests/test_routes_byok.py` — hit each route with and without the header, assert both are accepted (200).
- [ ] 2. Rework `app/llm.py` — `get_anthropic_client()` takes an optional `api_key` and builds a fresh client per call (drop the global `lru_cache` singleton entirely — no caching by key); `chat_text`/`chat_json` accept and forward an optional `api_key`, falling back to `settings.anthropic_api_key` when absent.
      Test: `backend/tests/test_llm.py` — call `chat_text`/`chat_json` with a stubbed key and with none, assert the right key reaches the mocked Anthropic client in each case, and that two calls with different keys never share a cached client.
- [ ] 3. Thread the optional key through every caller: `app/interview/orchestrator.py`, `app/evaluation/evaluator.py`, `app/evaluation/report.py`, `app/questions/retriever.py`, `app/resume/parser.py`.
      Test: extend each module's existing tests to assert the key passed in reaches `app/llm.py` (mock/spy on the LLM call).
- [ ] 4. Invalid-key error handling — map an Anthropic auth/billing error (401/403, quota-exceeded) on a user-supplied key, encountered on the first real request, to a clean, distinct API error (not a raw 500/stack trace).
      Test: `backend/tests/test_routes_byok.py` — send a request with a bad key (mocked 401/403 from Anthropic), assert a clean error response with a recognizable error code/message, and confirm no separate validation call was made.
- [ ] 5. Frontend Settings panel — enter/clear a personal Anthropic API key held in React state (in-memory, cleared on reload) by default, plus a "Remember on this device" toggle that, when on, also persists it to `localStorage`.
      Test: Playwright — enter a key with "Remember" off, reload, confirm it's gone; enter a key with "Remember" on, reload, confirm it's still populated; clear it, confirm it's removed from both memory and `localStorage`.
- [ ] 6. Frontend: `frontend/src/api/client.js` attaches `X-Anthropic-Api-Key` from the in-memory key store on every interview/resume request when set, omits it otherwise.
      Test: Playwright/network assertion — with a key set, outgoing requests carry the header; with none set, they don't.
- [ ] 7. Frontend indicator showing "your key" (and remembered-on-this-device status) vs. shared host key for the current session.
      Test: Playwright — indicator reflects current state after setting/clearing the key and toggling "Remember."
- [ ] 8. Graceful-degradation pass — full interview flow works end-to-end with no user key set (host-key fallback), matching v1 behavior exactly.
      Test: rerun `e2e/e2e_test.py` with no key configured, confirm no regression to the v1 golden path.
- [ ] 9. End-to-end pass with a user-supplied key — full interview using a real (test) Anthropic key, confirm usage appears against that key's account, capture screenshots.
      Test: extend `e2e/e2e_test.py`, same live-verification pattern as v1 task 9; new screenshots added to `e2e/screenshots/`.
