# Sprint v2 — PRD: AI Mock Interview Agent

## Overview
Extends the v1 text/voice interview agent with an optional webcam feed, reading non-verbal communication and anxiety/pressure patterns (eye contact, posture, facial tension, fidgeting) alongside the existing audio-based anxiety heuristic, and folding both into the final report.

## Target Users
- Candidates practicing for machine learning engineer interviews (same as v1), now optionally over video.
- The interview creator/operator, who gets a richer report including non-verbal communication signals.

## Core Features (v2 only)
1. Optional webcam capture, opt-in per session — mirrors v1's existing voice toggle; a candidate who declines still gets the exact v1 text/voice flow with no regression.
2. Periodic frame sampling from the browser feed, sent to the backend during the interview (not a continuous video stream).
3. Video-derived signal extraction per sampled frame/batch: eye contact/engagement with the camera, posture, facial tension, fidgeting — read via **Claude Vision on sampled frames** (proposed default, consistent with v1's all-Claude approach; see Open Decisions).
4. Combined multimodal anxiety/pressure detection: extends v1's speaking-rate/disfluency audio heuristic with the video-derived signal into one pressure score, still driving the existing pause-and-reassure turn.
5. Non-verbal communication section in the final report: a narrative summary of composure/eye-contact/body-language trends across the session, alongside v1's existing per-phase scores.
6. New persistence for derived (non-raw) per-turn video signals — proposed as a `video_signals` table (session_id, phase, timestamp, notes/scores); no raw video stored by default (see Open Decisions).
7. Report UI extended to render the new non-verbal communication section when a session used video.

## Out of Scope (v3+)
- Storing/replaying the raw video recording (transient-only processing is the v2 default — see Open Decisions).
- Video-based cheating/identity detection (distinct from v1's already-deferred general anti-cheating system).
- Multi-person/panel interview video.
- CI/CD pipeline (carried over from v1's Out of Scope, still not addressed).

## Open Decisions (confirm before `/dev` starts)
These were intentionally left open at planning time — not implementing yet — but will need a call before build starts:
- **Analysis approach**: periodic frames to Claude Vision (simplest, consistent with v1, adds per-frame API cost/latency) vs. a client-side face/pose model like MediaPipe (fully local, cheaper, less semantically rich) vs. a hybrid of both. PRD assumes Claude Vision as the default.
- **Video storage**: transient processing only (derived scores persisted, no raw video — PRD's default, simplest privacy story) vs. storing the full recording for candidate/interviewer review later (adds Supabase Storage cost, retention policy, consent scope).

## Tech Stack
| Component | Technology |
|---|---|
| Video Capture | Browser `getUserMedia` (same pattern as v1's mic capture), sampled frames — not a continuous stream |
| Video/Vision Analysis | Claude Vision, multimodal image input on sampled frames (proposed default — see Open Decisions) |
| Everything else (LLM, STT/TTS, DB, Backend, Frontend, Embeddings) | Unchanged from v1 — see `docs/WALKTHROUGH_v1.md` |

## Architecture
Extends the v1 flow: the browser optionally samples webcam frames alongside the existing mic capture and posts them to the backend during a turn. The backend sends sampled frames to Claude Vision for a composure/engagement read, combines that with the existing audio anxiety heuristic into one multimodal pressure signal (feeding the same reassurance-trigger path as v1), and persists only the derived signal (not raw video) alongside the turn. The evaluator/report generator picks up accumulated video signals when producing the final report.

```
Browser (React) --webcam frames (sampled)--> FastAPI backend --> Claude Vision (composure/engagement read)
               --mic audio (as in v1)------->                --> combined with v1 audio anxiety heuristic
                                                               --> Supabase (derived video_signals, not raw video)
                                                               --> evaluator (non-verbal section in final report)
```

## Success Criteria
- A candidate who enables video gets composure/engagement notes reflected in their final report's non-verbal communication section.
- A candidate who declines webcam access completes the full interview exactly as in v1, with no regression to the existing text/voice flow.
- Combined audio+video anxiety detection triggers the reassurance turn at least as reliably as v1's audio-only heuristic on the same anxious-input test cases.
- No raw video is persisted to Supabase (per the transient-only default above) unless the storage Open Decision is revisited and confirmed otherwise.
