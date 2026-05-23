"""
Service Schemas (Pydantic)
===========================
Schemas define the shape of data for API requests and responses.
They are separate from database models - this is intentional!

- Models = how data is stored in the DB
- Schemas = how data looks in API requests/responses

This separation lets you:
- Hide sensitive DB fields from API responses
- Validate input before it touches the DB
- Version your API independently of your DB schema
"""

from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional
from datetime import datetime


class ServiceBase(BaseModel):
    """Shared fields used in both Create and Update schemas."""
    name: str = Field(..., min_length=1, max_length=100, description="Service display name")
    url: str = Field(..., description="URL to monitor (must be a valid HTTP/HTTPS URL)")
    description: Optional[str] = Field(None, max_length=500)
    environment: str = Field("production", description="Environment: dev | staging | production")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v):
        """Ensure URL starts with http:// or https://"""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        allowed = {"dev", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v


class ServiceCreate(ServiceBase):
    """Schema for creating a new service (POST /services)."""
    pass


class ServiceUpdate(BaseModel):
    """Schema for updating a service (PATCH /services/{id}). All fields optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    url: Optional[str] = None
    description: Optional[str] = None
    environment: Optional[str] = None
    is_active: Optional[bool] = None


class ServiceResponse(ServiceBase):
    """Schema for API responses - includes DB fields like id, timestamps."""
    id: str
    is_active: bool
    is_healthy: Optional[bool] = None
    last_status_code: Optional[int] = None
    last_response_time_ms: Optional[float] = None
    last_checked_at: Optional[datetime] = None
    uptime_percentage: float
    total_checks: int
    successful_checks: int
    created_at: datetime

    # This tells Pydantic to read data from SQLAlchemy model attributes
    # (not just plain dicts). Required when using SQLAlchemy models.
    model_config = {"from_attributes": True}
