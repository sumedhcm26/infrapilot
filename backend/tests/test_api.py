"""
InfraPilot Backend Tests
========================
Basic integration tests for the API endpoints.
Run with: pytest tests/ -v

These tests use pytest-asyncio and httpx's AsyncClient to call
FastAPI endpoints without starting a real server.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import os

# Set test environment variables BEFORE importing the app
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_infrapilot.db"
os.environ["ENVIRONMENT"] = "testing"
os.environ["HEALTH_CHECK_INTERVAL"] = "99999"

from app.main import app  # noqa: E402
from app.database import create_tables  # noqa: E402


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create tables before each test, clean up after."""
    await create_tables()
    yield
    # Cleanup: delete test database
    import os
    if os.path.exists("test_infrapilot.db"):
        os.remove("test_infrapilot.db")


@pytest_asyncio.fixture
async def client():
    """Async HTTP client for testing FastAPI endpoints."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as c:
        yield c


# ----------------------------------------
# Health Check Tests
# ----------------------------------------

@pytest.mark.asyncio
async def test_health_check(client):
    """Test the /health endpoint returns 200."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
    assert "version" in data


@pytest.mark.asyncio
async def test_root(client):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    assert "InfraPilot" in response.json()["message"]


# ----------------------------------------
# Services Tests
# ----------------------------------------

@pytest.mark.asyncio
async def test_create_service(client):
    """Test creating a new service."""
    payload = {
        "name": "Test API",
        "url": "https://httpbin.org/status/200",
        "environment": "dev",
        "description": "Test service",
    }
    response = await client.post("/api/v1/services/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test API"
    assert data["url"] == "https://httpbin.org/status/200"
    assert data["environment"] == "dev"
    assert "id" in data
    return data["id"]


@pytest.mark.asyncio
async def test_list_services(client):
    """Test listing services."""
    # Create a service first
    await client.post("/api/v1/services/", json={
        "name": "List Test API",
        "url": "https://example.com",
        "environment": "staging",
    })
    response = await client.get("/api/v1/services/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_create_service_invalid_url(client):
    """Test that invalid URLs are rejected."""
    response = await client.post("/api/v1/services/", json={
        "name": "Bad Service",
        "url": "not-a-valid-url",
        "environment": "dev",
    })
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_service_not_found(client):
    """Test 404 for non-existent service."""
    response = await client.get("/api/v1/services/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_service(client):
    """Test deleting a service."""
    # Create first
    create_resp = await client.post("/api/v1/services/", json={
        "name": "To Delete",
        "url": "https://example.com",
        "environment": "dev",
    })
    service_id = create_resp.json()["id"]

    # Delete
    delete_resp = await client.delete(f"/api/v1/services/{service_id}")
    assert delete_resp.status_code == 204

    # Confirm gone
    get_resp = await client.get(f"/api/v1/services/{service_id}")
    assert get_resp.status_code == 404


# ----------------------------------------
# Deployments Tests
# ----------------------------------------

@pytest.mark.asyncio
async def test_create_deployment(client):
    """Test recording a deployment."""
    response = await client.post("/api/v1/deployments/", json={
        "service_id": "svc-123",
        "service_name": "Payment API",
        "version": "v1.2.3",
        "environment": "production",
        "triggered_by": "GitHub Actions",
        "branch": "main",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["version"] == "v1.2.3"
    assert data["status"] == "running"


# ----------------------------------------
# Incidents Tests
# ----------------------------------------

@pytest.mark.asyncio
async def test_create_incident(client):
    """Test manually creating an incident."""
    response = await client.post("/api/v1/incidents/", json={
        "service_id": "svc-abc",
        "service_name": "Auth Service",
        "title": "Auth service returning 503",
        "severity": "high",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "open"
    assert data["severity"] == "high"


@pytest.mark.asyncio
async def test_resolve_incident(client):
    """Test resolving an incident."""
    # Create
    create_resp = await client.post("/api/v1/incidents/", json={
        "service_id": "svc-xyz",
        "service_name": "DB Service",
        "title": "DB connection timeout",
        "severity": "critical",
    })
    inc_id = create_resp.json()["id"]

    # Resolve
    update_resp = await client.patch(f"/api/v1/incidents/{inc_id}", json={
        "status": "resolved",
        "resolution_notes": "Restarted DB connection pool",
    })
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "resolved"
    assert update_resp.json()["resolved_at"] is not None
