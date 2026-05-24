"""
InfraPilot - FastAPI Backend Entry Point
========================================
This is the main application file. FastAPI automatically generates
interactive API docs at /docs (Swagger UI) and /redoc (ReDoc UI).

DevOps concept: The 'main.py' is the entry point for the backend service.
In production, this would be run with: uvicorn app.main:app --host 0.0.0.0 --port 8000
"""

from contextlib import asynccontextmanager
import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_tables
from app.routers import health, services, deployments, incidents, environments
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.utils.logger import get_logger
from app.services.health_checker import run_health_checks_loop

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager - runs setup BEFORE the app starts
    and cleanup AFTER the app shuts down.

    This is the modern FastAPI replacement for @app.on_event("startup")
    """
    # --- STARTUP ---
    logger.info("🚀 InfraPilot backend starting up...")

    # Create database tables if they don't exist
    # In production you'd use Alembic migrations instead
    await create_tables()
    logger.info("✅ Database tables ready")

    # Start the background health checker loop
    # This runs as a background async task - checking services every N seconds
    health_check_task = asyncio.create_task(run_health_checks_loop())
    logger.info("✅ Background health checker started")

    yield  # App is running here

    # --- SHUTDOWN ---
    logger.info("🛑 InfraPilot backend shutting down...")
    health_check_task.cancel()
    try:
        await health_check_task
    except asyncio.CancelledError:
        pass
    logger.info("✅ Background tasks stopped cleanly")


# Create the FastAPI application instance
app = FastAPI(
    title="InfraPilot API",
    description="Cloud Deployment & Monitoring Platform API",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI - great for testing endpoints
    redoc_url="/redoc",     # Alternative API docs
    lifespan=lifespan,
)

# -------------------------------------------------------------------
# CORS Middleware
# -------------------------------------------------------------------
# CORS = Cross-Origin Resource Sharing
# Browsers block frontend JS from calling APIs on different domains/ports
# by default. We need to explicitly allow our frontend origin.
# In production, replace "*" with your actual frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware for request logging
app.add_middleware(RequestLoggingMiddleware)

# -------------------------------------------------------------------
# Register Routers
# -------------------------------------------------------------------
# Routers group related endpoints together (like blueprints in Flask)
# The prefix means all routes in that router start with /api/v1/...
app.include_router(health.router, tags=["Health"])
app.include_router(services.router, prefix="/api/v1/services", tags=["Services"])
app.include_router(deployments.router, prefix="/api/v1/deployments", tags=["Deployments"])
app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["Incidents"])
app.include_router(environments.router, prefix="/api/v1/environments", tags=["Environments"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - confirms the API is alive."""
    return {
        "message": "Welcome to InfraPilot API",
        "version": "1.0.0",
        "docs": "/docs",
    }
