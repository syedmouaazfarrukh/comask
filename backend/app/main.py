"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.config import settings
from app.api import queries, data_collection, conversations, auth
from app.db.database import init_db, close_db, check_db_health
from app.db import models  # Import models to register them with Base.metadata
from app.middleware.auth import AuthMiddleware

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Energy Compliance Assistant", environment=settings.app_env)
    try:
        await init_db()
        logger.info("Database initialized successfully with pgvector")
    except Exception as e:
        logger.warning("Database initialization failed - some features may not work", error=str(e))
        logger.info("Application started (database connection will be retried on first use)")

    logger.info("Application started", llm_provider=settings.llm_provider)

    yield

    # Shutdown
    logger.info("Shutting down application")
    await close_db()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Energy Compliance Assistant API - Providing defensible answers with exact sources for energy compliance attorneys.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware - configure based on environment
if settings.app_env == "production":
    # In production, specify exact origins
    allowed_origins = [
        "https://comask-frontend-app.azurewebsites.net",
    ]
else:
    # In development, allow localhost
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:8000",
    ]

# Auth middleware first (runs second due to middleware ordering)
app.add_middleware(AuthMiddleware)

# CORS middleware last (runs first - handles preflight requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["X-Request-ID", "X-Processing-Time"],
)

# Include routers
app.include_router(auth.router)  # Auth endpoints
app.include_router(queries.router)
app.include_router(data_collection.router)
app.include_router(conversations.router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "description": "Energy Compliance Assistant API",
        "status": "running",
        "llm_provider": settings.llm_provider,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """
    Health check endpoint.

    Returns database connectivity status.
    """
    db_healthy = await check_db_health()

    return {
        "status": "healthy" if db_healthy else "degraded",
        "database": "connected" if db_healthy else "disconnected",
        "environment": settings.app_env,
    }
