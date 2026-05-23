"""
Incident Model
==============
An incident is created automatically when a service health check fails.
This is similar to how PagerDuty or OpsGenie works.

Incident lifecycle: open -> acknowledged -> resolved
"""

from sqlalchemy import Column, String, DateTime, Text, Integer, Float
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Incident(Base):
    """
    Represents a service outage or degradation event.

    Table: incidents
    """
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Which service triggered this incident
    service_id = Column(String, nullable=False, index=True)
    service_name = Column(String(100), nullable=False)

    # Incident details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), default="medium")        # low | medium | high | critical
    status = Column(String(20), default="open")            # open | acknowledged | resolved

    # What triggered it
    trigger_status_code = Column(Integer, nullable=True)   # HTTP status code that caused this
    trigger_response_time_ms = Column(Float, nullable=True)

    # Resolution
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Incident service={self.service_name} severity={self.severity} status={self.status}>"
