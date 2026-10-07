import logging
from typing import Optional
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings

logger = logging.getLogger(__name__)

_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker] = None


def get_engine() -> Engine:
    """
    Get or initialize the SQLAlchemy Engine connected to MySQL using PyMySQL.
    Configured with connection pooling, recycling, and pre-ping liveness checks.
    """
    global _engine
    if _engine is None:
        db_url = settings.DATABASE_URL
        _engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=5,
            max_overflow=10,
            echo=False
        )
    return _engine


def get_session() -> Session:
    """
    Produce a new SQLAlchemy Session bound to the MySQL engine.
    """
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
    return _session_factory()


def check_db_connection() -> bool:
    """
    Execute a lightweight connectivity ping (SELECT 1) against the database.
    Returns True if connection succeeds, False otherwise.
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning("Database connectivity check failed: %s", exc)
        return False


def verify_db_connection() -> None:
    """
    Verifies database connectivity. If connection fails, raises a descriptive RuntimeError
    explaining the host, port, database, and credential requirements without silent fallback.
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        error_msg = (
            f"Failed to connect to MySQL database '{settings.MYSQL_DATABASE}' "
            f"on {settings.MYSQL_HOST}:{settings.MYSQL_PORT} (user: '{settings.MYSQL_USER}'). "
            f"Underlying error: {exc}. "
            "Please check that the MySQL service is running and MYSQL_PASSWORD is correctly set in .env."
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from exc
