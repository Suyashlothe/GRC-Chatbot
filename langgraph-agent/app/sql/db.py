from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger
from typing import Generator

from app.config import get_settings

settings = get_settings()

# ── Engine ────────────────────────────────────────────────────────
engine = create_engine(
    settings.mysql_url,
    pool_pre_ping=True,    # stale connection auto-detect
    pool_size=5,           # 5 persistent connections
    max_overflow=10,       # peak pe 10 extra
    pool_timeout=30,       # 30s wait karo agar pool full ho
    pool_recycle=1800,     # 30 min baad recycle (MySQL timeout se pehle)
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# Only main.py is called once at startup. It verifies the connection — it does not create any tables
def init_db() -> None:
 
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(" MySQL connected.")
    except Exception as e:
        logger.error(f" MySQL connection failed: {e}")
        raise

# FastAPI routes dependency injection.
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"DB session error: {e}")
        raise
    finally:
        db.close()



# Only used by sql_agent.py.
# The query is already validated by validate_sql() beforehand.
# Returns: list of row dicts
def execute_raw(sql: str) -> list[dict]:

    with engine.connect() as conn:
        result = conn.execute(
            text(sql).execution_options(
                timeout=settings.sql_query_timeout
            )
        )
        rows = [dict(row._mapping) for row in result.fetchall()]

    logger.debug(f"execute_raw -> {len(rows)} rows | '{sql[:80]}'")
    return rows