"""
Services Router
===============
CRUD endpoints for managing monitored services.

REST conventions used here:
- GET /services           -> list all services
- POST /services          -> create a service
- GET /services/{id}      -> get a single service
- PATCH /services/{id}    -> partial update
- DELETE /services/{id}   -> delete
- POST /services/{id}/check -> trigger manual health check
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse
from app.services.health_checker import check_single_service
from app.utils.logger import get_logger
import aiohttp

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=List[ServiceResponse])
async def list_services(
    environment: str = None,
    db: AsyncSession = Depends(get_db),
):
    """List all registered services. Optionally filter by environment."""
    query = select(Service).order_by(Service.created_at.desc())

    if environment:
        query = query.where(Service.environment == environment)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    service_data: ServiceCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new service for monitoring."""
    service = Service(**service_data.model_dump())
    db.add(service)
    await db.commit()
    await db.refresh(service)

    logger.info(f"New service registered: {service.name} ({service.url})")
    return service


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: str, db: AsyncSession = Depends(get_db)):
    """Get details for a specific service."""
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()

    if not service:
        raise HTTPException(status_code=404, detail=f"Service {service_id} not found")

    return service


@router.patch("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: str,
    update_data: ServiceUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Partially update a service."""
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()

    if not service:
        raise HTTPException(status_code=404, detail=f"Service {service_id} not found")

    # Only update fields that were provided (not None)
    update_dict = update_data.model_dump(exclude_none=True)
    for key, value in update_dict.items():
        setattr(service, key, value)

    await db.commit()
    await db.refresh(service)
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(service_id: str, db: AsyncSession = Depends(get_db)):
    """Remove a service from monitoring."""
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()

    if not service:
        raise HTTPException(status_code=404, detail=f"Service {service_id} not found")

    await db.delete(service)
    await db.commit()
    logger.info(f"Service deleted: {service.name}")


@router.post("/{service_id}/check", response_model=ServiceResponse)
async def trigger_health_check(service_id: str, db: AsyncSession = Depends(get_db)):
    """
    Manually trigger an immediate health check for a service.
    Useful for testing or after making changes.
    """
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()

    if not service:
        raise HTTPException(status_code=404, detail=f"Service {service_id} not found")

    # Import here to avoid circular imports
    from app.services.health_checker import check_single_service, update_service_health

    async with aiohttp.ClientSession() as http_session:
        check_result = await check_single_service(http_session, service)

    await update_service_health(db, service, check_result)
    await db.refresh(service)

    return service


@router.get("/stats/summary")
async def get_services_summary(db: AsyncSession = Depends(get_db)):
    """Get a summary of service health across all environments."""
    from app.services.monitoring import get_dashboard_stats
    return await get_dashboard_stats(db)
