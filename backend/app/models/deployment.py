"""
Deployment Model
================
Tracks each deployment event for your services.
This is what you see in GitHub Actions or Heroku's "Activity" tab.

A deployment record captures:
- what was deployed (version/commit)
- where (environment)
- when
- who triggered it
- the result (success/failure/in-progress)
"""

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Deployment(Base):
    """
    Represents a single deployment event.

    Table: deployments
    """
    __tablename__ = "deployments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Which service was deployed
    service_id = Column(String, nullable=False, index=True)
    service_name = Column(String(100), nullable=False)

    # Deployment details
    version = Column(String(100), nullable=False)          # e.g. "v1.2.3" or commit SHA
    environment = Column(String(50), nullable=False)       # dev | staging | production
    status = Column(String(50), default="pending")         # pending|running|success|failed|rolled_back

    # Optional metadata
    triggered_by = Column(String(100), nullable=True)      # User or CI system name
    commit_sha = Column(String(40), nullable=True)         # Git commit hash
    branch = Column(String(100), nullable=True)            # Git branch
    notes = Column(Text, nullable=True)                    # Release notes or description

    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Deployment service={self.service_name} version={self.version} status={self.status}>"
