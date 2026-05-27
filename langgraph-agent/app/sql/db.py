from typing import Generator

from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings


settings = get_settings()

_engine: Engine | None = None
_session_factory: sessionmaker | None = None


def get_engine() -> Engine:
    global _engine

    if _engine is not None:
        return _engine

    if not settings.mysql_configured:
        raise RuntimeError(
            "MySQL is not configured. Set mysql_host, mysql_user, "
            "mysql_password, and mysql_db in the environment or .env."
        )

    _engine = create_engine(
        settings.mysql_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        echo=False,
    )
    return _engine


def get_session_factory() -> sessionmaker:
    global _session_factory

    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
        )

    return _session_factory


def test_connection() -> bool:
    if not settings.mysql_configured:
        logger.warning("MySQL connection skipped because configuration is missing.")
        return False

    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))

        logger.info("MySQL connected.")
        return True
    except Exception as exc:
        logger.error(f"MySQL connection failed: {exc}")
        return False


def get_db() -> Generator[Session, None, None]:
    db = get_session_factory()()
    try:
        yield db
    except Exception as exc:
        db.rollback()
        logger.error(f"DB session error: {exc}")
        raise
    finally:
        db.close()


def execute_raw(sql: str) -> list[dict]:
    with get_engine().connect() as conn:
        result = conn.execute(
            text(sql).execution_options(
                timeout=settings.sql_query_timeout
            )
        )
        rows = [dict(row._mapping) for row in result.fetchall()]

    logger.debug(f"execute_raw -> {len(rows)} rows | '{sql[:80]}'")
    return rows
