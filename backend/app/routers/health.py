"""
Health Check Router
===================
Every production service needs a /health endpoint.
Load balancers, Docker, and Kubernetes use this to check if the app is alive.

If /health returns non-200, the orchestrator will restart the container.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_db
from app.config import settings

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Basic health check endpoint.
    Returns 200 if the app is running and database is reachable.
    """
    # Check database connectivity
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
    }


@router.get("/health/live", tags=["Health"])
async def liveness():
    """
    Liveness probe - just checks if the process is alive.
    Kubernetes uses this to know if a container needs to be restarted.
    """
    return {"status": "alive"}


@router.get("/health/ready", tags=["Health"])
async def readiness(db: AsyncSession = Depends(get_db)):
    """
    Readiness probe - checks if the app is ready to receive traffic.
    Kubernetes uses this to decide if traffic should be routed to this pod.
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Database not ready")
