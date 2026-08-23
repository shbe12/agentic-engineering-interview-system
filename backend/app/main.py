import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routes import interview, resume

logger = logging.getLogger("app")

app = FastAPI(title="AI Mock Interview Agent")


@app.middleware("http")
async def catch_unhandled_exceptions(request: Request, call_next):
    # A `@app.exception_handler(Exception)` runs in Starlette's ServerErrorMiddleware,
    # which always sits OUTSIDE CORSMiddleware — so that response never gets CORS
    # headers, and the browser reports a misleading "CORS policy" error instead of
    # the real one. Catching it here, in a middleware registered before CORSMiddleware
    # is added (making it the inner layer), means CORSMiddleware sees a normal
    # response and adds its headers as usual.
    try:
        return await call_next(request)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unhandled exception")
        return JSONResponse(status_code=500, content={"detail": f"{type(exc).__name__}: {exc}"})


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(resume.router)
app.include_router(interview.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
