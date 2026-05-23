"""
Health Checker Service
======================
This is the core monitoring engine. It runs as a background async task,
periodically checking all registered services and recording results.

Key concepts:
- asyncio: Python's async framework for concurrent code
- aiohttp: Async HTTP client (doesn't block while waiting for responses)
- Background task: A coroutine that runs indefinitely alongside the web server
"""

import asyncio
import logging
from datetime import datetime, timezone

import aiohttp
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.service import Service
from app.models.incident import Incident

logger = logging.getLogger(__name__)


async def check_single_service(session: aiohttp.ClientSession, service: Service) -> dict:
    """
    Perform a health check on a single service URL.
    Returns a dict with the check results.

    We measure response time by recording timestamps before/after the request.
    """
    start_time = asyncio.get_event_loop().time()
    result = {
        "is_healthy": False,
        "status_code": None,
        "response_time_ms": None,
        "error": None,
    }

    try:
        async with session.get(
            service.url,
            timeout=aiohttp.ClientTimeout(total=settings.HEALTH_CHECK_TIMEOUT),
            ssl=False,  # Allow self-signed certs for internal services
        ) as response:
            elapsed_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            result["status_code"] = response.status
            result["response_time_ms"] = round(elapsed_ms, 2)
            # Consider 2xx and 3xx as healthy
            result["is_healthy"] = response.status < 400

    except asyncio.TimeoutError:
        result["error"] = "Request timed out"
        logger.warning(f"Health check timeout for service: {service.name} ({service.url})")

    except aiohttp.ClientConnectionError as e:
        result["error"] = f"Connection error: {str(e)}"
        logger.warning(f"Health check connection error for {service.name}: {e}")

    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
        logger.error(f"Health check unexpected error for {service.name}: {e}")

    return result


async def update_service_health(db: AsyncSession, service: Service, check_result: dict):
    """
    Update the service record in the database with the latest health check results.
    Also creates an incident if the service just went down.
    """
    was_healthy = service.is_healthy
    is_now_healthy = check_result["is_healthy"]

    # Update counts for uptime percentage calculation
    new_total = (service.total_checks or 0) + 1
    new_successful = (service.successful_checks or 0) + (1 if is_now_healthy else 0)
    uptime_pct = (new_successful / new_total) * 100

    # Update the service record
    await db.execute(
        update(Service)
        .where(Service.id == service.id)
        .values(
            is_healthy=is_now_healthy,
            last_status_code=check_result["status_code"],
            last_response_time_ms=check_result["response_time_ms"],
            last_checked_at=datetime.now(timezone.utc),
            total_checks=new_total,
            successful_checks=new_successful,
            uptime_percentage=round(uptime_pct, 2),
        )
    )

    # If service just went DOWN (was healthy/unknown, now unhealthy) -> create incident
    # was_healthy=None means first check; we don't create incident on first failure
    if was_healthy is True and not is_now_healthy:
        incident = Incident(
            service_id=service.id,
            service_name=service.name,
            title=f"Service {service.name} is unreachable",
            description=f"Health check failed. Error: {check_result.get('error', 'HTTP ' + str(check_result.get('status_code', 'unknown')))}",
            severity="high",
            status="open",
            trigger_status_code=check_result["status_code"],
            trigger_response_time_ms=check_result["response_time_ms"],
        )
        db.add(incident)
        logger.warning(f"🚨 INCIDENT CREATED: {service.name} is DOWN!")

    # If service came back UP, auto-resolve open incidents for it
    elif was_healthy is False and is_now_healthy:
        await db.execute(
            update(Incident)
            .where(
                Incident.service_id == service.id,
                Incident.status == "open"
            )
            .values(
                status="resolved",
                resolved_at=datetime.now(timezone.utc),
                resolution_notes="Service automatically recovered - health check passed",
            )
        )
        logger.info(f"✅ Service {service.name} recovered - incidents resolved")

    await db.commit()


async def run_health_checks_once():
    """
    Run health checks on all active services once.
    Uses aiohttp for concurrent HTTP requests (much faster than sequential).
    """
    async with AsyncSessionLocal() as db:
        # Fetch all active services
        result = await db.execute(
            select(Service).where(Service.is_active == True)  # noqa: E712
        )
        services = result.scalars().all()

        if not services:
            logger.debug("No active services to check")
            return

        logger.info(f"Running health checks on {len(services)} services...")

        # Use a single aiohttp session for all requests (more efficient)
        async with aiohttp.ClientSession() as http_session:
            # Run all health checks concurrently (at the same time)
            # asyncio.gather runs multiple coroutines simultaneously
            tasks = [check_single_service(http_session, svc) for svc in services]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for service, result in zip(services, results):
            if isinstance(result, Exception):
                logger.error(f"Unexpected error checking {service.name}: {result}")
                continue

            # Re-fetch service to get latest state before updating
            async with AsyncSessionLocal() as update_db:
                fresh_service_result = await update_db.execute(
                    select(Service).where(Service.id == service.id)
                )
                fresh_service = fresh_service_result.scalar_one_or_none()
                if fresh_service:
                    await update_service_health(update_db, fresh_service, result)

        logger.info(f"Health check cycle complete for {len(services)} services")


async def run_health_checks_loop():
    """
    The main background loop. Runs health checks every N seconds indefinitely.
    This runs alongside the FastAPI server as an async background task.
    """
    logger.info(f"Health check loop starting (interval: {settings.HEALTH_CHECK_INTERVAL}s)")

    while True:
        try:
            await run_health_checks_once()
        except Exception as e:
            # Don't let one bad cycle crash the whole loop
            logger.error(f"Health check cycle error: {e}", exc_info=True)

        # Wait before the next check cycle
        await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL)
