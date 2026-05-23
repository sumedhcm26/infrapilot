"""Environment Pydantic schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EnvironmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: str = Field("#6366f1", description="Hex color code for UI display")


class EnvironmentResponse(BaseModel):
    id: str
    name: str
    display_name: str
    description: Optional[str] = None
    color: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
