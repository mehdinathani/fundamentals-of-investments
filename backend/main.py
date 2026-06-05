import os
from dotenv import load_dotenv

load_dotenv()

from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.database import init_db
from backend.routers import market, journal, macro, pipeline
from backend.auth import require_auth

app = FastAPI(
    title="PSX Investment System",
    version="1.0.0",
    description="Full-stack dashboard for the PSX investment pipeline.",
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["WWW-Authenticate"],
)


app.include_router(market.router)
app.include_router(journal.router)
app.include_router(macro.router)
app.include_router(pipeline.router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


# Expose auth check endpoint (frontend uses this to verify credentials)
@app.post("/api/auth/login")
def login(_: str = Depends(require_auth)):
    return {"user": _, "message": "Authenticated"}


# ─── Serve built frontend (SPA) ─────────────────────────────────────
STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="frontend")
