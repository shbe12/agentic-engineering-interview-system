---
name: prd
description: Generates a project roadmap document (PRD) for a new project or a new versioned sprint of an existing one, following the team's "Sprint vN — PRD" template (Overview, Target Users, Core Features (vN only), Out of Scope (vN+1+), Tech Stack, Architecture, Success Criteria). Use when the user asks to plan a new project or sprint, write a PRD/roadmap doc, or invokes /prd, before any implementation work starts. First of a three-skill workflow: /prd -> /dev -> /walkthrough.
license: MIT
---

# /prd — Project Roadmap Document

First step of the versioned-sprint workflow: **/prd → /dev → /walkthrough**. `/prd` produces the plan and gets it approved; `/dev` executes it task by task; `/walkthrough` documents what shipped once the sprint is done. This mirrors: *"I don't want you to start building right away. First, create a project roadmap document. Once I approve it, execute the tasks step by step."*

## Template

Every PRD produced by this skill follows this exact structure:

```markdown
# Sprint v<N> — PRD: <Project Name>

## Overview
<1-2 sentence elevator pitch: what is being built and why>

## Target Users
- <persona 1>
- <persona 2>

## Core Features (v<N> only)
1. <feature>
2. <feature>
...

## Out of Scope (v<N+1>+)
- <deferred item>
- <deferred item>

## Tech Stack
| Component | Technology |
|---|---|
| <Component> | <Technology> |
| ... | (rows as relevant: LLM, Frontend, Backend, Database, Auth, Voice/STT/TTS, Embedding Model, Deployment, Secrets, etc.) |

## Architecture
<short prose description of how the pieces talk to each other, or an ASCII/mermaid diagram if it adds clarity — not just a placeholder>

## Success Criteria
- <testable, checkable outcome>
- <testable, checkable outcome>
```

## Workflow

1. **Determine the sprint number.** New project → `v1`. Existing project with a prior `docs/PRD.md` → read it, bump to the next version, and treat new work as that version's scope (previous versions' Core Features become historical context, not restated).
2. **Gather inputs.** From the user's request (and any spec/notes they've referenced), identify: project name, one-line purpose, target users, the features that belong in *this* version specifically, anything explicitly deferred, the tech stack, and how the major pieces fit together. If any of these is genuinely unclear (not just terse), ask — do not silently invent product scope, especially Core Features and Out of Scope.
3. **Draft the PRD** into `docs/PRD.md` (create `docs/` if missing; if revising, overwrite with the new version but keep it as a single current document, not an accumulating history file). Keep Core Features numbered and scoped tightly to the current version.
4. **Draft a matching task list** into `docs/TASKS.md` — one checklist item per unit of work needed to deliver the Core Features, roughly in build order (foundations/scaffolding first, integration/end-to-end pass last). Keep it short enough to track at a glance (roughly 8-10 items) — split further only if the user asks for more granularity. **Every task carries a `Test:` line** naming how `/dev` will verify it's actually done (a `pytest` test, a route hit via `/docs`, a scripted manual check, a verification query — whatever fits that task), e.g.:
   ```markdown
   - [ ] 3. Resume ingestion — POST /resume/upload, OpenAI parsing, stored in `candidates`.
         Test: `backend/tests/test_resume.py` — upload a sample PDF, assert 200 + a row lands in `candidates`.
   ```
   This file is what `/dev` executes against, and `/dev` won't check a task off without its test passing — so don't leave the `Test:` line vague or skip it.
5. **Get approval before building.** Present the PRD (or use plan mode if already mid-task) and confirm the user is happy with the scope before writing application code. Do not start implementation in the same turn the PRD is drafted unless the user has already approved it.
6. **Hand off to `/dev`.** Once approved, implementation proceeds via the `/dev` skill, which executes `docs/TASKS.md` and keeps `docs/PRD.md` as the scope source of truth (if scope changes mid-build, update the PRD first).

## Notes

- If regenerating a PRD for a project that already has one, read the existing `docs/PRD.md` first and treat this as a new version, not a blind overwrite of history — preserve decisions that are still valid, and note what changed from the prior version in Core Features / Out of Scope.
- The "Architecture" section should earn its place: a couple of sentences on data flow (e.g. "browser → API → DB → external LLM/voice APIs") is more useful than a placeholder bracket, unless the user specifically wants a diagram stub to fill in later.
