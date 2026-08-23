---
name: dev
description: Executes the approved task list in docs/TASKS.md, one task at a time, writing and running a test for each task before checking it off. Use when the user says to start building, continue building, invokes /dev, or asks to pick up where implementation left off, after a PRD (docs/PRD.md) has already been approved. Second of a three-skill workflow: /prd -> /dev -> /walkthrough.
license: MIT
---

# /dev — Execute the Task List

Second step of the versioned-sprint workflow: **/prd → /dev → /walkthrough**. `/dev` turns an approved `docs/PRD.md` + `docs/TASKS.md` into working code, task by task — and **every task is checked off by a passing test, not by eyeballing the code.**

## Preconditions

- `docs/PRD.md` exists and has been approved by the user (if it doesn't exist yet, run `/prd` first — don't invent scope here).
- `docs/TASKS.md` exists with a checklist (`- [ ] N. ...` / `- [x] N. ...`).

## Task format — every task carries a test

Each task in `docs/TASKS.md` must have a `Test:` line naming how it's verified. If a task doesn't have one yet (e.g. an older task list from before this rule), add one before starting that task rather than skipping straight to implementation:

```markdown
- [ ] 3. Resume ingestion — POST /resume/upload, OpenAI parsing, stored in `candidates`.
      Test: `backend/tests/test_resume.py` — upload a sample PDF, assert 200 + a row lands in `candidates`.
```

Pick the right kind of test for the task, don't force everything into one mold:
- Backend logic (parsers, orchestrators, evaluators, retrievers) → a `pytest` unit/integration test, mocking external services (LLM/DB/third-party APIs) at the boundary the way the rest of the suite does.
- API routes → an integration test hitting the route (`httpx`/`TestClient`, or exercised via `/docs`) asserting status + shape.
- Frontend components/flows → a component test if the project has a test runner configured, otherwise a scripted manual check (exact steps + expected result) recorded in the task's `Test:` line — don't silently skip frontend verification just because there's no test framework wired up yet.
- Infra/scaffolding tasks (schema, provisioning, config) → a concrete verification command (e.g. a query confirming tables exist), not a unit test.

## Workflow

1. **Read `docs/PRD.md` and `docs/TASKS.md`** to load current scope and find the next unchecked task.
2. **Work one task at a time**, in order, unless a task is blocked (e.g. missing credentials) — in that case, say so explicitly, skip to the next unblocked task, and come back to the blocked one once unblocked.
3. **Write or update that task's test first (or alongside the code)** — the `Test:` line in `docs/TASKS.md` is a commitment, not documentation written after the fact.
4. **Run the test and see it pass** before touching the checklist. A test you wrote but never ran, or ran and didn't see pass, does not justify a checkmark. If the task is genuinely un-runnable right now (e.g. blocked on a missing API key/credential), leave it unchecked, say so explicitly, and note what's blocking it — don't check it off on code-reading confidence alone.
5. **Check it off in `docs/TASKS.md`** (`- [ ]` → `- [x]`) only once its test has actually passed, then move to the next task — this keeps progress resumable and honest across sessions.
6. **Keep scope changes flowing back to the PRD, not around it.** If mid-task you discover the approved scope needs to change, update `docs/PRD.md` (and `docs/TASKS.md` if the task breakdown changes) and flag it to the user — don't silently drift from what was approved.
7. **When all tasks are checked off (and thus all tests pass)**, tell the user the sprint's implementation is done and that `/walkthrough` can now generate the walkthrough doc — don't generate it yourself from this skill.

## Notes

- This skill assumes an already-approved plan; it does not re-litigate scope. If the user's request implies new scope not in `docs/PRD.md`, point that out and suggest running `/prd` again for the next version rather than quietly expanding the current one.
- If `docs/TASKS.md` doesn't exist, don't guess a task breakdown from scratch — that's `/prd`'s job.
- A task blocked on something outside your control (missing secret, no `pip`/`sudo` access, etc.) stays unchecked with the blocker named in `docs/TASKS.md`, not silently marked done "because the code looks right."
