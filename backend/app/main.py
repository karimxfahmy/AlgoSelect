"""
FastAPI entrypoint.

    uvicorn app.main:app --reload --port 8000

CORS is wide-open during development so the Vite dev server (5173) can hit
us without trouble. Lock this down before any real deployment.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router


app = FastAPI(
    title="AlgoSelect API",
    version="0.1.0",
    description="Multi-algorithm decision engine: selects DP, Greedy, "
                "Divide & Conquer, or Brute Force based on problem properties.",
)

# TODO: tighten allow_origins to the actual frontend URL before deploying
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "AlgoSelect",
        "docs": "/docs",
        "api_root": "/api",
    }
