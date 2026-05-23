"""Incidents Router - manage service incidents/outages."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timezone

from app.database import get_db
from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=List[IncidentResponse])
async def list_incidents(
    status: str = None,
    service_id: str = None,
    severity: str = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List incidents with optional filters."""
    query = select(Incident).order_by(Incident.created_at.desc()).limit(limit)

    if status:
        query = query.where(Incident.status == status)
    if service_id:
        query = query.where(Incident.service_id == service_id)
    if severity:
        query = query.where(Incident.severity == severity)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_data: IncidentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Manually create an incident."""
    incident = Incident(**incident_data.model_dump())
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    logger.warning(f"Manual incident created: {incident.title}")
    return incident


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: str,
    update_data: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update incident status (acknowledge or resolve)."""
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    update_dict = update_data.model_dump(exclude_none=True)
    if update_dict.get("status") == "resolved":
        update_dict["resolved_at"] = datetime.now(timezone.utc)

    for key, value in update_dict.items():
        setattr(incident, key, value)

    await db.commit()
    await db.refresh(incident)
    return incident
