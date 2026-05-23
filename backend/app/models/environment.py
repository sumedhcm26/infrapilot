"""
Environment Model
=================
Environments represent deployment targets: dev, staging, production.
This helps organize services and deployments by environment.
"""

from sqlalchemy import Column, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Environment(Base):
    """
    Represents a deployment environment (dev/staging/production).

    Table: environments
    """
    __tablename__ = "environments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    name = Column(String(50), nullable=False, unique=True)  # dev | staging | production
    display_name = Column(String(100), nullable=False)       # Human-readable name
    description = Column(Text, nullable=True)
    color = Column(String(20), default="#6366f1")            # UI color for this env
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Environment name={self.name}>"
