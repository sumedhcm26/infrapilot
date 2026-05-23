"""Deployment Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DeploymentCreate(BaseModel):
    service_id: str
    service_name: str
    version: str = Field(..., min_length=1, max_length=100)
    environment: str = Field(..., description="dev | staging | production")
    triggered_by: Optional[str] = None
    commit_sha: Optional[str] = Field(None, max_length=40)
    branch: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class DeploymentUpdate(BaseModel):
    status: Optional[str] = Field(None, description="pending|running|success|failed|rolled_back")
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None


class DeploymentResponse(BaseModel):
    id: str
    service_id: str
    service_name: str
    version: str
    environment: str
    status: str
    triggered_by: Optional[str] = None
    commit_sha: Optional[str] = None
    branch: Optional[str] = None
    notes: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
