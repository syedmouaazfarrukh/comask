"""Database connection and session management with pgvector support."""

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from typing import AsyncGenerator
import structlog

from app.config import settings

logger = structlog.get_logger()

# Create async engine for PostgreSQL
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Check connection health
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for getting database session (for use outside of FastAPI dependencies)."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """Initialize database (create tables and extensions)."""
    async with engine.begin() as conn:
        # Enable pgvector extension (uuid-ossp not needed - using Python uuid4)
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

        # Ensure new jurisdiction enum values exist (for upgrades)
        # SQLAlchemy uses enum member NAMES (uppercase) for PostgreSQL enum values
        try:
            await conn.execute(text("ALTER TYPE jurisdictiontype ADD VALUE IF NOT EXISTS 'TEXAS'"))
            await conn.execute(text("ALTER TYPE jurisdictiontype ADD VALUE IF NOT EXISTS 'ERCOT'"))
        except Exception:
            pass  # Values already exist or fresh database

    logger.info("Database initialized with pgvector extension")


async def close_db():
    """Close database connections."""
    await engine.dispose()
    logger.info("Database connections closed")


async def check_db_health() -> bool:
    """Check if database connection is healthy."""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return False


async def get_vector_search_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a session optimized for vector search operations.
    Uses the same session factory but with specific settings.
    """
    async with AsyncSessionLocal() as session:
        # Set search path and optimize for vector queries
        await session.execute(text("SET work_mem = '256MB'"))
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
