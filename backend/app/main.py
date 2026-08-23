from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import interview, resume

app = FastAPI(title="AI Mock Interview Agent")

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
