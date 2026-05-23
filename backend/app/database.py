"""
Database Setup
==============
We use SQLAlchemy with async support for non-blocking database operations.

Key concepts:
- Engine: The connection to the database
- Session: A unit of work (like a transaction) with the database
- AsyncSession: The async version, so our API doesn't block while waiting for DB

For local dev: SQLite (file-based, no installation needed)
For production: Switch DATABASE_URL to PostgreSQL
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Database Engine
# -------------------------------------------------------------------
# The engine manages the connection pool to the database.
# connect_args={"check_same_thread": False} is required for SQLite
# because SQLite has thread restrictions by default.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,   # Set to True to log all SQL queries (helpful for learning)
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

# -------------------------------------------------------------------
# Session Factory
# -------------------------------------------------------------------
# AsyncSessionLocal creates new database sessions.
# expire_on_commit=False means we can still access object attributes after commit.
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# -------------------------------------------------------------------
# Base Model Class
# -------------------------------------------------------------------
# All our database models will inherit from this Base class.
# SQLAlchemy uses this to know which classes map to database tables.
class Base(DeclarativeBase):
    pass


# -------------------------------------------------------------------
# Dependency Injection for FastAPI
# -------------------------------------------------------------------
async def get_db():
    """
    FastAPI Dependency - provides a database session to route handlers.

    Usage in a router:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...

    The 'yield' makes this a context manager - the session is automatically
    closed after the request finishes, even if an error occurs.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """
    Create all database tables defined in our models.
    This is called once at startup.

    In production, you'd use Alembic migrations instead of this,
    which tracks schema changes over time (like Git for your database).
    """
    # Import all models so SQLAlchemy knows about them
    from app.models import service, deployment, incident, environment  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified successfully")
