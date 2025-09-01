# app/core/db.py
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
import os
import logging
from typing import Generator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# SQLAlchemy 2.0+ engine configuration
engine_kwargs = {
    "pool_pre_ping": True,
    "pool_recycle": 300,  # Recycle connections after 5 minutes
    "pool_size": 10,      # Connection pool size
    "max_overflow": 20,   # Max overflow connections
    "echo": os.getenv("SQL_ECHO", "false").lower() == "true",  # Log SQL queries
}


# Create engine
engine = create_engine(DATABASE_URL, **engine_kwargs)

# SQLAlchemy 2.0+ sessionmaker configuration
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,  # Use modern Session class
    autoflush=False,  # Don't auto-flush (better control)
    autocommit=False,  # Explicit commits (SQLAlchemy 2.0+ default)
    expire_on_commit=False,  # Keep objects usable after commit
)


# Database dependency for FastAPI 
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Context manager for database sessions (useful for scripts/background tasks)
def get_db_session() -> Session:
    """
    Context manager for database sessions.

    """
    return SessionLocal()


# Database health check
async def check_database_health() -> bool:
    """
    Check if database connection is healthy.
    Useful for health check endpoints.
    """
    try:
        with SessionLocal() as db:
            # Simple query to test connection
            db.execute("SELECT 1")
            return True
    except Exception as e:
        logging.error(f"Database health check failed: {e}")
        return False


# Database initialization (for testing or setup scripts)
def init_db():
    """
    Initialize database tables.
    Only use this for initial setup or testing.
    In production, use Alembic migrations instead.
    """
    from app.models.base import Base  # Import your Base class
    Base.metadata.create_all(bind=engine)


# Database cleanup (useful for testing)
def drop_all_tables():
    """
    Drop all database tables.
    ⚠️ DANGEROUS: Only use in testing environments!
    """
    if os.getenv("ENVIRONMENT") != "testing":
        raise RuntimeError("drop_all_tables can only be used in testing environment")
    
    from app.models.base import Base
    Base.metadata.drop_all(bind=engine)