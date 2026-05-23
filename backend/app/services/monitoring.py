"""
Monitoring Service
==================
Business logic for fetching monitoring stats and dashboard data.
Keeping business logic in services (not routers) keeps code organized.
"""

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.service import Service
from app.models.deployment import Deployment
from app.models.incident import Incident


async def get_dashboard_stats(db: AsyncSession) -> dict:
    """
    Aggregate statistics for the main dashboard.
    Returns counts and summaries used by the frontend dashboard.
    """
    # Total services
    total_services_result = await db.execute(
        select(func.count(Service.id)).where(Service.is_active == True)  # noqa: E712
    )
    total_services = total_services_result.scalar() or 0

    # Healthy services count
    healthy_result = await db.execute(
        select(func.count(Service.id)).where(
            and_(Service.is_active == True, Service.is_healthy == True)  # noqa: E712
        )
    )
    healthy_count = healthy_result.scalar() or 0

    # Open incidents count
    open_incidents_result = await db.execute(
        select(func.count(Incident.id)).where(Incident.status == "open")
    )
    open_incidents = open_incidents_result.scalar() or 0

    # Recent deployments (last 10)
    recent_deployments_result = await db.execute(
        select(Deployment).order_by(Deployment.created_at.desc()).limit(10)
    )
    recent_deployments = recent_deployments_result.scalars().all()

    # Successful deployments in last 30 days
    successful_deployments_result = await db.execute(
        select(func.count(Deployment.id)).where(Deployment.status == "success")
    )
    successful_deployments = successful_deployments_result.scalar() or 0

    return {
        "total_services": total_services,
        "healthy_services": healthy_count,
        "unhealthy_services": total_services - healthy_count,
        "open_incidents": open_incidents,
        "successful_deployments": successful_deployments,
        "recent_deployments": recent_deployments,
    }
