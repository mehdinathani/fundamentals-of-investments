from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db
from backend.routers import market, journal, macro, pipeline

app = FastAPI(
    title="PSX Investment System",
    version="1.0.0",
    description="Full-stack dashboard for the PSX investment pipeline.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
