---
name: dev
description: Executes the approved task list in docs/TASKS.md, one task at a time, checking each off as it lands. Use when the user says to start building, continue building, invokes /dev, or asks to pick up where implementation left off, after a PRD (docs/PRD.md) has already been approved. Second of a three-skill workflow: /prd -> /dev -> /walkthrough.
license: MIT
---

# /dev — Execute the Task List

Second step of the versioned-sprint workflow: **/prd → /dev → /walkthrough**. `/dev` turns an approved `docs/PRD.md` + `docs/TASKS.md` into working code, task by task.

## Preconditions

- `docs/PRD.md` exists and has been approved by the user (if it doesn't exist yet, run `/prd` first — don't invent scope here).
- `docs/TASKS.md` exists with a checklist (`- [ ] N. ...` / `- [x] N. ...`).

## Workflow

1. **Read `docs/PRD.md` and `docs/TASKS.md`** to load current scope and find the next unchecked task.
2. **Work one task at a time**, in order, unless a task is blocked (e.g. missing credentials) — in that case, say so explicitly, skip to the next unblocked task, and come back to the blocked one once unblocked.
3. **After a task's changes are in place**, check it off in `docs/TASKS.md` (`- [ ]` → `- [x]`) before moving to the next one, so progress is visible at a glance and resumable across sessions.
4. **Keep scope changes flowing back to the PRD, not around it.** If mid-task you discover the approved scope needs to change, update `docs/PRD.md` (and `docs/TASKS.md` if the task breakdown changes) and flag it to the user — don't silently drift from what was approved.
5. **Prefer small, verifiable increments** over one giant unreviewable change: get each task to a state where it can actually be exercised (a route hit via `/docs`, a component rendered, a test run) before moving on.
6. **When all tasks are checked off**, tell the user the sprint's implementation is done and that `/walkthrough` can now generate the walkthrough doc — don't generate it yourself from this skill.

## Notes

- This skill assumes an already-approved plan; it does not re-litigate scope. If the user's request implies new scope not in `docs/PRD.md`, point that out and suggest running `/prd` again for the next version rather than quietly expanding the current one.
- If `docs/TASKS.md` doesn't exist, don't guess a task breakdown from scratch — that's `/prd`'s job.
