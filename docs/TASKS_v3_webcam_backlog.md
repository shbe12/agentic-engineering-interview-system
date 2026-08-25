# Tasks — AI Mock Interview Agent v3 (backlog)

**Planning only — not being implemented yet.** This is the task breakdown for `docs/PRD_v3_webcam_backlog.md` Sprint v3 (video features / communicative & anxiety-pressure patterns), deferred behind v2 (bring your own API key) and captured for when `/dev` is picked up later. The two Open Decisions in the PRD (analysis approach, video storage) should be confirmed before task 1 starts.

- [ ] 1. Webcam capture UI — opt-in toggle (mirrors v1's voice toggle) + `getUserMedia` periodic frame sampling in `ChatWindow`.
      Test: Playwright — toggle renders, camera permission requested, no regression to the flow when declined.
- [ ] 2. Backend endpoint to receive sampled frames per turn/phase (batched, not a raw stream).
      Test: `backend/tests/test_video.py` — POST a sample frame fixture, assert 200 + a signal recorded.
- [ ] 3. Frame analysis — composure/engagement/body-language read via Claude Vision on sampled frames (per Open Decision default).
      Test: unit test against a fixture image, assert structured output shape.
- [ ] 4. Combine v1's audio anxiety heuristic with the new video-derived signal into one multimodal pressure score; extend the existing reassurance-trigger logic.
      Test: `backend/tests/test_anxiety_multimodal.py` — combined heuristic test cases, including audio-only fallback when video is declined.
- [ ] 5. New Supabase table for derived per-turn video signals (not raw video) — schema migration.
      Test: query `information_schema.tables` to confirm the table exists; roundtrip an insert.
- [ ] 6. Extend the evaluator/report generator to produce a non-verbal communication narrative section from accumulated video signals.
      Test: `backend/tests/test_evaluator.py` extension — a session with video signals produces the new report section; a session without still works as in v1.
- [ ] 7. Extend the Report UI to render the non-verbal communication section when present.
      Test: Playwright — report view shows the new section for a video-enabled session, omits it otherwise.
- [ ] 8. Graceful degradation pass — full interview flow still works end-to-end with video declined/unavailable.
      Test: rerun `e2e/e2e_test.py` (or a variant) with camera permission denied, confirm no regression to the v1 golden path.
- [ ] 9. End-to-end pass with video enabled — full interview via webcam, verify the combined report, capture screenshots.
      Test: extend `e2e/e2e_test.py`, same live-verification pattern as v1 task 9; new screenshots added to `e2e/screenshots/`.
