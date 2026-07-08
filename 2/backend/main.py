from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from database import init_db
from routers import analyze, history, feedback, admin

app = FastAPI(
    title="PhishGuard AI API",
    description="ML-based phishing URL detection — BSc Final Year Project",
    version="1.0.0",
)

# Allow the frontend (any origin when opened as a local file)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(analyze.router,  prefix="/api")
app.include_router(history.router,  prefix="/api")
app.include_router(feedback.router, prefix="/api")
app.include_router(admin.router,    prefix="/api")

# Serve the frontend at /
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "../frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.on_event("startup")
def on_startup():
    init_db()
    print("\n✓ PhishGuard AI API running")
    print("  Docs:     http://localhost:8000/docs")
    print("  Frontend: http://localhost:8000/\n")


@app.get("/api/health")
def health():
    return {"status": "ok"}
