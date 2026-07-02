import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import engine, Base
from app.routers import auth, trips

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Travel Planner",
    description="AI-powered travel planning with itinerary generation and budget optimization",
    version="1.0.0",
)

# CORS middleware — allow local dev and HF Spaces origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:7860",
        "https://travelai-ruby.vercel.app",
        "https://*.hf.space",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router)
app.include_router(trips.router)


# --- Serve React Frontend (production) ---
# In the Docker container, the built React app is at /app/frontend/dist
STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"


@app.get("/")
def root():
    """Serve React app index.html at root, or health check if no build exists."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "status": "healthy",
        "service": "AI Travel Planner API",
        "version": "1.0.0",
    }


# Mount static assets (JS, CSS, images) AFTER API routes so /api/* takes priority
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="static-assets")
    # Catch-all for client-side routing (e.g. /dashboard, /plan, /trip/1)
    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        """Serve index.html for all non-API, non-asset routes (SPA client-side routing)."""
        file_path = STATIC_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")