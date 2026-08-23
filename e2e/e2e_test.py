"""Full end-to-end Playwright test for the AI Mock Interview Agent.

Drives the REAL frontend against the REAL backend and REAL Claude / Supabase /
ElevenLabs services — this is not a mocked unit test (those live in
backend/tests/ and run under plain `pytest`; this script is intentionally kept
out of that tree so a normal `pytest` run never tries to launch a browser or
hit live services).

Covers the golden path: resume upload -> parse -> start interview -> text
answer -> voice answer (a synthesized WAV fed in as a fake microphone, so the
real MediaRecorder -> Scribe STT path is exercised, not just curl) -> fast
-forward to phase 5 (same DB mechanism used during manual verification, so we
don't re-burn many real LLM turns on phases 2-4 already proven by the natural
flow above) -> final report renders.

Prerequisites:
  - Backend running on http://localhost:8000 (uvicorn app.main:app)
  - Frontend running on http://localhost:5173 (npm run dev)
  - backend/.env filled in (ANTHROPIC_API_KEY, ELEVENLABS_API_KEY, SUPABASE_*)
  - e2e/fixtures/sample_answer.wav present (regenerate with
    backend/.venv/bin/python e2e/generate_fixture.py if missing)

Run:
    backend/.venv/bin/python e2e/e2e_test.py

Exits 0 if every check passed, 1 otherwise.
"""

import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests
from playwright.sync_api import sync_playwright

FRONTEND_URL = os.environ.get("E2E_FRONTEND_URL", "http://localhost:5173")
RESUME_PATH = os.environ.get("E2E_RESUME_PATH", "/mnt/c/Users/Sherline/Downloads/cv.pdf")
AUDIO_FIXTURE = Path(__file__).parent / "fixtures" / "sample_answer.wav"
SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

SUPABASE_PROJECT_REF = "skkubowbfwfmpkgqmxij"
SECRETS_PATH = Path(__file__).parent.parent / "secrets.md"


class Check:
    """Records pass/fail per assertion instead of raising immediately, so one
    failure doesn't prevent the rest of the run from being reported."""

    def __init__(self):
        self.results: list[tuple[str, bool]] = []

    def that(self, description: str, condition: bool) -> None:
        status = "PASS" if condition else "FAIL"
        print(f"[{status}] {description}")
        self.results.append((description, condition))

    def summarize(self) -> bool:
        passed = sum(1 for _, ok in self.results if ok)
        total = len(self.results)
        print(f"\n{passed}/{total} checks passed")
        return passed == total and total > 0


def _management_token() -> str:
    text = SECRETS_PATH.read_text()
    match = re.search(r"sbp_[a-f0-9]+", text)
    if not match:
        raise RuntimeError("Could not find the Supabase management token in secrets.md")
    return match.group(0)


def _fast_forward_phase(session_id: str, phase: int) -> None:
    token = _management_token()
    resp = requests.post(
        f"https://api.supabase.com/v1/projects/{SUPABASE_PROJECT_REF}/database/query",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"query": f"update interview_sessions set current_phase = {phase} where id = '{session_id}';"},
        timeout=30,
    )
    resp.raise_for_status()


def _session_status(session_id: str) -> str:
    token = _management_token()
    resp = requests.post(
        f"https://api.supabase.com/v1/projects/{SUPABASE_PROJECT_REF}/database/query",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"query": f"select status from interview_sessions where id = '{session_id}';"},
        timeout=30,
    )
    resp.raise_for_status()
    rows = resp.json()
    return rows[0]["status"] if rows else "unknown"


def run() -> bool:
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    check = Check()
    console_errors: list[str] = []
    session_id_holder: dict[str, str] = {}

    if not AUDIO_FIXTURE.exists():
        print(f"Missing fixture: {AUDIO_FIXTURE} — run e2e/generate_fixture.py first.")
        return False
    if not Path(RESUME_PATH).exists():
        print(f"Missing resume at {RESUME_PATH} — set E2E_RESUME_PATH to a real PDF.")
        return False

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--use-fake-ui-for-media-stream",
                "--use-fake-device-for-media-stream",
                f"--use-file-for-fake-audio-capture={AUDIO_FIXTURE}",
            ],
        )
        context = browser.new_context(viewport={"width": 1000, "height": 900}, permissions=["microphone"])
        page = context.new_page()
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        def capture_start_response(response):
            if response.url.endswith("/interview/start") and response.request.method == "POST":
                try:
                    session_id_holder["id"] = response.json()["session_id"]
                except Exception:
                    pass

        page.on("response", capture_start_response)

        # Per-turn / per-phase-transition screenshot trail, in addition to the
        # named milestone screenshots below. "phase_N_start.png" is written
        # the first time phase N is observed; "turn_NN_phase_N.png" is
        # written after every turn (candidate message + interviewer reply).
        # This test still fast-forwards phase 1 -> 5 via direct DB write (see
        # below) rather than burning real LLM calls on phases 2-4, so only
        # phase_1_start.png and phase_5_start.png will ever be produced —
        # phases 2-4 are covered by the live manual testing in TASKS.md task 5,
        # not by this automated trail.
        turn_state: dict = {"count": 0, "last_phase": None}
        phase_holder: dict = {"phase": None}

        def capture_phase_response(response):
            if response.request.method != "POST":
                return
            path = urlparse(response.url).path
            if path.endswith(("/interview/start", "/interview/message", "/interview/voice")):
                try:
                    phase_holder["phase"] = response.json()["phase"]
                except Exception:
                    pass

        page.on("response", capture_phase_response)

        def snap_turn(page):
            phase = phase_holder["phase"]
            if phase is None:
                return
            turn_state["count"] += 1
            page.screenshot(
                path=str(SCREENSHOT_DIR / f"turn_{turn_state['count']:02d}_phase_{phase}.png")
            )
            if phase != turn_state["last_phase"]:
                page.screenshot(path=str(SCREENSHOT_DIR / f"phase_{phase}_start.png"))
                turn_state["last_phase"] = phase

        try:
            # 1. Load
            page.goto(FRONTEND_URL, wait_until="networkidle")
            check.that("page loads with title", page.locator("h1").inner_text() == "AI Mock Interview Agent")
            page.screenshot(path=str(SCREENSHOT_DIR / "1-upload.png"))

            # 2. Upload + parse resume
            page.set_input_files("input[type=file]", RESUME_PATH)
            page.click('button:has-text("Start")')
            page.wait_for_selector("text=Begin interview", timeout=150000)
            ready_text = page.locator("body").inner_text()
            check.that("resume parsed and field detected", "Field detected" in ready_text)
            page.screenshot(path=str(SCREENSHOT_DIR / "2-ready.png"))

            # 3. Start interview
            page.click('button:has-text("Begin interview")')
            page.wait_for_selector("text=Interviewer", timeout=150000)
            opening = page.locator("p.whitespace-pre-wrap").first.inner_text()
            check.that("interviewer opens with a real question", len(opening) > 10)
            page.screenshot(path=str(SCREENSHOT_DIR / "3-chat-start.png"))
            snap_turn(page)

            # 4. Text answer
            page.fill(
                'input[placeholder="Type your answer…"]',
                "I did my PhD in computational biology, then moved into NLP and speech "
                "research, and now work at DeepMind on Gemini multimodal capabilities.",
            )
            page.click('button:has-text("Send")')
            page.wait_for_function("document.querySelectorAll('p.whitespace-pre-wrap').length >= 3", timeout=150000)
            check.that("text answer produced a follow-up reply", True)
            snap_turn(page)

            # 5. Voice answer — real MediaRecorder -> blob -> /interview/voice ->
            # ElevenLabs Scribe STT, using a synthesized WAV as the fake mic input.
            before_count = page.locator("p.whitespace-pre-wrap").count()
            page.click('button:has-text("Answer by voice")')
            page.wait_for_timeout(4000)  # let MediaRecorder actually capture the fake input
            page.click('button:has-text("Stop & send")')
            page.wait_for_function(
                f"document.querySelectorAll('p.whitespace-pre-wrap').length > {before_count + 1}",
                timeout=150000,
            )
            check.that("voice answer transcribed and produced a reply", True)
            page.screenshot(path=str(SCREENSHOT_DIR / "4-after-voice.png"))
            snap_turn(page)

            # 6. Fast-forward to phase 5 via the DB — same mechanism used during
            # manual verification, so we don't re-burn many real LLM turns on
            # phases 2-4 already proven correct by the natural flow above. Phase
            # 5 itself still runs its real multi-turn flow (4 behavioral
            # questions, one at a time) — jumping straight to phase_complete
            # isn't realistic, so answer in a loop until the session actually
            # completes, same as a real candidate would experience it.
            check.that("captured session_id from /interview/start response", "id" in session_id_holder)
            if "id" in session_id_holder:
                session_id = session_id_holder["id"]
                _fast_forward_phase(session_id, 5)

                phase5_answers = [
                    "In five years I'd like to be leading a research team working on "
                    "multimodal reasoning systems deployed at scale.",
                    "The biggest challenge has been aligning cross-modal representations "
                    "at scale while keeping latency acceptable for production.",
                    "I work closely with infra and product teams, and I favor a lot of "
                    "early written design docs so disagreements surface before code does.",
                    "Yes — what does success look like for this role after the first six months?",
                ]
                completed = False
                for answer in phase5_answers:
                    # The answer input disappears entirely once the interview
                    # completes (the view switches to the report screen), so
                    # wait for EITHER the input re-enabling OR the report
                    # heading appearing — waiting only for the input would
                    # hang forever on the turn that actually finishes it.
                    page.fill('input[placeholder="Type your answer…"]', answer)
                    page.click('button:has-text("Send")')
                    page.wait_for_timeout(500)
                    input_ready = page.locator('input[placeholder="Type your answer…"]:not([disabled])')
                    report_heading = page.get_by_text("Final report")
                    input_ready.or_(report_heading).first.wait_for(timeout=150000)
                    snap_turn(page)
                    if _session_status(session_id) == "completed":
                        completed = True
                        break
                check.that("phase 5 reached completion within the scripted Q&A", completed)

                # 7. App should auto-switch to the report view once phase 5 completes.
                # Report generation runs ~6 sequential Claude calls (5 phase
                # evals + 1 summary) — give it real headroom.
                page.wait_for_selector("text=Final report", timeout=240000)
                page.screenshot(path=str(SCREENSHOT_DIR / "5-report.png"))
                report_text = page.locator("body").inner_text()
                check.that("report view rendered a summary", "Final report" in report_text)
                check.that(
                    "report view rendered phase scores",
                    "/100" in report_text or "—" in report_text,
                )

            check.that("no browser console errors", len(console_errors) == 0)
            if console_errors:
                print("Console errors:", console_errors)

        except Exception as exc:  # noqa: BLE001
            check.that(f"unhandled exception during test: {exc!r}", False)
            page.screenshot(path=str(SCREENSHOT_DIR / "FAILURE.png"))

        browser.close()

    return check.summarize()


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
