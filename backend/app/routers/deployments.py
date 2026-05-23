"""Deployments Router - CRUD for deployment tracking."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timezone

from app.database import get_db
from app.models.deployment import Deployment
from app.schemas.deployment import DeploymentCreate, DeploymentUpdate, DeploymentResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=List[DeploymentResponse])
async def list_deployments(
    service_id: str = None,
    environment: str = None,
    status: str = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List deployments with optional filters."""
    query = select(Deployment).order_by(Deployment.created_at.desc()).limit(limit)

    if service_id:
        query = query.where(Deployment.service_id == service_id)
    if environment:
        query = query.where(Deployment.environment == environment)
    if status:
        query = query.where(Deployment.status == status)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=DeploymentResponse, status_code=status.HTTP_201_CREATED)
async def create_deployment(
    deployment_data: DeploymentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Record a new deployment."""
    deployment = Deployment(
        **deployment_data.model_dump(),
        status="running",
        started_at=datetime.now(timezone.utc),
    )
    db.add(deployment)
    await db.commit()
    await db.refresh(deployment)

    logger.info(f"Deployment started: {deployment.service_name} {deployment.version} -> {deployment.environment}")
    return deployment


@router.get("/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(deployment_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific deployment by ID."""
    result = await db.execute(select(Deployment).where(Deployment.id == deployment_id))
    deployment = result.scalar_one_or_none()

    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    return deployment


@router.patch("/{deployment_id}", response_model=DeploymentResponse)
async def update_deployment(
    deployment_id: str,
    update_data: DeploymentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update deployment status (e.g., mark as success or failed)."""
    result = await db.execute(select(Deployment).where(Deployment.id == deployment_id))
    deployment = result.scalar_one_or_none()

    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    update_dict = update_data.model_dump(exclude_none=True)

    # Auto-set completed_at when status changes to terminal state
    if update_dict.get("status") in ("success", "failed", "rolled_back"):
        update_dict["completed_at"] = datetime.now(timezone.utc)

    for key, value in update_dict.items():
        setattr(deployment, key, value)

    await db.commit()
    await db.refresh(deployment)
    logger.info(f"Deployment {deployment_id} updated: status={deployment.status}")
    return deployment
