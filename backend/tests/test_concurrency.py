import inspect

from app.routes import interview, resume

# Regression test: these route handlers call blocking SDK clients (Anthropic,
# Supabase, ElevenLabs) directly. Declaring them `async def` without offloading
# that work blocks the whole event loop for the call's duration — found live,
# where /health became unresponsive during a single /interview/message call.
# Handlers with no `await` in their body must stay plain `def` (FastAPI runs
# those in a thread pool automatically); handlers that do need `await` must run
# their blocking calls through `run_in_threadpool` instead of calling them inline.


def test_sync_only_routes_are_plain_functions_not_coroutines():
    for fn in (interview.start, interview.message, interview.speak, interview.report):
        assert not inspect.iscoroutinefunction(fn), (
            f"{fn.__name__} calls a blocking SDK client directly — it must be a "
            "plain `def`, not `async def`, or it will block the event loop"
        )


def test_file_upload_routes_offload_blocking_work_to_threadpool():
    for fn in (resume.upload_resume, interview.voice_message):
        assert inspect.iscoroutinefunction(fn)
        source = inspect.getsource(fn)
        assert "run_in_threadpool" in source, (
            f"{fn.__name__} is async (needs `await file.read()`) but must run its "
            "blocking SDK calls via run_in_threadpool, not inline, or it will "
            "block the event loop"
        )
