"""Incident Pydantic schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class IncidentCreate(BaseModel):
    service_id: str
    service_name: str
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    severity: str = Field("medium", description="low | medium | high | critical")
    trigger_status_code: Optional[int] = None
    trigger_response_time_ms: Optional[float] = None


class IncidentUpdate(BaseModel):
    status: Optional[str] = Field(None, description="open | acknowledged | resolved")
    severity: Optional[str] = None
    resolution_notes: Optional[str] = None


class IncidentResponse(BaseModel):
    id: str
    service_id: str
    service_name: str
    title: str
    description: Optional[str] = None
    severity: str
    status: str
    trigger_status_code: Optional[int] = None
    trigger_response_time_ms: Optional[float] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
