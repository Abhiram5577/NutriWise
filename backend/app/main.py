"""NutriWise FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine, check_db_connection
from app.routers import auth, food_diary, health_profile, symptom, lab_result, nutrition

logger = logging.getLogger("nutriwise")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — create tables on startup if DB is available."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created / verified.")
    except Exception as e:
        logger.warning("Could not connect to database on startup: %s", e)
        logger.warning("The server will start, but DB-dependent endpoints will fail.")
    yield


app = FastAPI(
    title="NutriWise API",
    description="AI-Powered Nutrition Intelligence System",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow the Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Health-check endpoints ──────────────────────────────────────────────

@app.get("/api/health", tags=["Health"])
def health_check():
    """Basic health check — always returns healthy if the server is up."""
    return {"status": "healthy", "service": "NutriWise API", "version": "0.1.0"}


@app.get("/api/health/db", tags=["Health"])
def health_check_db():
    """Database connectivity check."""
    connected = check_db_connection()
    return {
        "status": "connected" if connected else "disconnected",
        "database": "PostgreSQL",
    }


# ── Register routers ────────────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(food_diary.router)
app.include_router(health_profile.router)
app.include_router(symptom.router)
app.include_router(lab_result.router)
app.include_router(nutrition.router)


@app.get("/", tags=["Root"])
def root():
    """API root — redirect users to the docs."""
    return {
        "message": "Welcome to NutriWise API",
        "docs": "/docs",
        "health": "/api/health",
    }

