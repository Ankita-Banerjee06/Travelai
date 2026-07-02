from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, trips

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Travel Planner",
    description="AI-powered travel planning with itinerary generation and budget optimization",
    version="1.0.0",
)

# CORS middleware — allow Vercel frontend and local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://travelai-ruby.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(trips.router)


@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Travel Planner API",
        "version": "1.0.0",
    }