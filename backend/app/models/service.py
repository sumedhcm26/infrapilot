"""
Service Model
=============
A "Service" represents any backend API or URL that InfraPilot monitors.
For example: your payment API, user service, etc.

SQLAlchemy models define the structure of database tables.
Each class attribute maps to a column in the table.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, Text
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Service(Base):
    """
    Represents a monitored service/API endpoint.

    Table: services
    """
    __tablename__ = "services"

    # Primary key using UUID for uniqueness across distributed systems
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Service metadata
    name = Column(String(100), nullable=False, index=True)
    url = Column(String(500), nullable=False)                # The URL to monitor
    description = Column(Text, nullable=True)
    environment = Column(String(50), default="production")  # dev/staging/production

    # Health status - updated by the background health checker
    is_active = Column(Boolean, default=True)
    is_healthy = Column(Boolean, nullable=True)              # None = never checked yet
    last_status_code = Column(Integer, nullable=True)        # HTTP status code
    last_response_time_ms = Column(Float, nullable=True)     # Response time in milliseconds
    last_checked_at = Column(DateTime(timezone=True), nullable=True)

    # Uptime tracking
    uptime_percentage = Column(Float, default=100.0)
    total_checks = Column(Integer, default=0)
    successful_checks = Column(Integer, default=0)

    # Timestamps - func.now() uses the database server time
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Service name={self.name} url={self.url} healthy={self.is_healthy}>"
