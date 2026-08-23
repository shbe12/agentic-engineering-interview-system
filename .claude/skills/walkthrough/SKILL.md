---
name: walkthrough
description: Generates a walkthrough document for a completed sprint, explaining what was built, how to set it up and run it, and how to verify the golden path end-to-end. Use when the user says a sprint/version is done and asks for a walkthrough, invokes /walkthrough, or asks "how do I run/test what was just built". Third of a three-skill workflow: /prd -> /dev -> /walkthrough.
license: MIT
---

# /walkthrough — Sprint Walkthrough Doc

Third step of the versioned-sprint workflow: **/prd → /dev → /walkthrough**. Once `/dev` has checked off `docs/TASKS.md` for a sprint (or the user otherwise says the sprint is done), this skill writes the doc that lets someone else — or future-you — actually run and verify what shipped.

## Output

Write to `docs/WALKTHROUGH_v<N>.md`, where `<N>` matches the sprint version in `docs/PRD.md` (`Sprint v<N> — PRD: ...`). Don't overwrite a prior version's walkthrough — each sprint gets its own file, so the history of what shipped when stays intact.

## Template

```markdown
# Walkthrough — Sprint v<N>: <Project Name>

## What shipped
<short recap of the Core Features delivered this sprint, cross-checked against docs/TASKS.md — flag anything in the PRD's Core Features that did NOT actually land, don't just restate the PRD as if everything landed>

## Setup
<concrete, copy-pasteable steps to get it running locally from a clean checkout: install deps, env vars/secrets needed (names only, never values), any provisioning already done for the user (e.g. "the Supabase project is already created — just fill in OPENAI_API_KEY") vs. what they still need to do themselves>

## Running it
<the actual commands to start each piece (backend, frontend, etc.) and the URLs/ports involved>

## Golden path walkthrough
<a numbered, step-by-step walk through the primary user flow end-to-end, written so someone unfamiliar with the code could follow it in a browser/terminal and know what "working" looks like at each step>

## Known limitations / not done
<anything left broken, stubbed, or explicitly out of scope for this version — pull from docs/PRD.md's "Out of Scope" plus anything discovered during /dev that didn't make it in>

## Next version
<a one-line pointer to what's expected in v<N+1>, if known>
```

## Workflow

1. **Verify before writing.** Don't transcribe the PRD's Core Features as "done" without checking — read `docs/TASKS.md` for what's actually checked off, and where feasible actually exercise the golden path (run the app, hit an endpoint, run the test suite) before describing it as working. If something can't be verified (e.g. blocked on a missing API key), say so plainly rather than describing it as functional.
2. **Write for a stranger.** Assume the reader has the repo but no memory of this conversation — concrete commands, concrete file paths, no "as discussed" references.
3. **Keep secret values out of it.** Reference env var *names*, never actual keys/tokens/passwords, even ones already provisioned.
4. **After writing**, tell the user the walkthrough is ready and where it lives, and suggest running `/prd` again when they're ready to scope the next version.
