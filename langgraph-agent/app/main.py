from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware.logging_middleware import logging_middleware
from app.api.routes import chat
from app.config import settings
from app.graph.graph import grc_graph
from app.rag.chroma_client import get_collection
from app.rag.embeddings import get_embedding
from app.sql.db import test_connection
from app.sql.schema_loader import SchemaLoader
from app.utils.logger import logger


APP_VERSION = "1.0.0"


def _build_startup_status() -> dict[str, Any]:
    return {
        "langgraph": {
            "ready": False,
            "detail": "",
        },
        "embeddings": {
            "ready": False,
            "detail": "",
        },
        "chroma": {
            "ready": False,
            "detail": "",
            "collection": settings.chroma_collection_grc,
        },
        "mysql": {
            "ready": False,
            "detail": "",
        },
        "schema": {
            "ready": False,
            "detail": "",
            "tables": [],
        },
    }


def _overall_status(components: dict[str, Any]) -> str:
    if all(component["ready"] for component in components.values()):
        return "healthy"

    if any(component["ready"] for component in components.values()):
        return "degraded"

    return "unhealthy"


@asynccontextmanager
async def lifespan(app: FastAPI):
    startup_status = _build_startup_status()
    app.state.startup_status = startup_status
    app.state.langgraph = grc_graph

    logger.info("=" * 60)
    logger.info("GRC Chatbot - LangGraph Agent")
    logger.info("=" * 60)

    logger.info("[1/5] Initializing LangGraph...")
    try:
        app.state.langgraph = grc_graph
        startup_status["langgraph"]["ready"] = True
        startup_status["langgraph"]["detail"] = "Graph compiled and attached to app state."
        logger.info("[1/5] LangGraph is ready.")
    except Exception as exc:
        startup_status["langgraph"]["detail"] = str(exc)
        logger.error(f"[1/5] LangGraph initialization failed: {exc}")

    logger.info("[2/5] Loading embeddings model...")
    try:
        get_embedding("startup health check")
        startup_status["embeddings"]["ready"] = True
        startup_status["embeddings"]["detail"] = f"Loaded embedding model '{settings.embedding_model}'."
        logger.info("[2/5] Embeddings loaded successfully.")
    except Exception as exc:
        startup_status["embeddings"]["detail"] = str(exc)
        logger.error(f"[2/5] Embeddings failed: {exc}")

    logger.info("[3/5] Connecting to Chroma...")
    try:
        collection = get_collection()
        app.state.chroma_collection = collection
        startup_status["chroma"]["ready"] = True
        startup_status["chroma"]["detail"] = (
            f"Collection '{collection.name}' is available at '{settings.chroma_path}'."
        )
        logger.info(f"[3/5] Chroma collection ready: {collection.name}")
    except Exception as exc:
        startup_status["chroma"]["detail"] = str(exc)
        logger.error(f"[3/5] Chroma initialization failed: {exc}")

    logger.info("[4/5] Connecting to MySQL...")
    try:
        mysql_ready = test_connection()
        startup_status["mysql"]["ready"] = mysql_ready
        startup_status["mysql"]["detail"] = (
            "MySQL connection verified." if mysql_ready else "MySQL connection test failed."
        )

        if mysql_ready:
            logger.info("[4/5] MySQL connected successfully.")
        else:
            logger.warning("[4/5] MySQL connection failed.")
    except Exception as exc:
        startup_status["mysql"]["detail"] = str(exc)
        logger.error(f"[4/5] MySQL error: {exc}")

    logger.info("[5/5] Loading schema cache...")
    if startup_status["mysql"]["ready"]:
        try:
            await SchemaLoader.load()
            tables = SchemaLoader.get_table_names()
            startup_status["schema"]["ready"] = True
            startup_status["schema"]["tables"] = tables
            startup_status["schema"]["detail"] = f"Loaded schema for {len(tables)} tables."
            logger.info(f"[5/5] Schema cached successfully with {len(tables)} tables.")
        except Exception as exc:
            startup_status["schema"]["detail"] = str(exc)
            logger.error(f"[5/5] Schema loading failed: {exc}")
    else:
        startup_status["schema"]["detail"] = "Skipped because MySQL is unavailable."
        logger.warning("[5/5] Schema loading skipped because MySQL is unavailable.")

    logger.info("-" * 60)
    logger.info(f"Server running on {settings.api_host}:{settings.api_port}")
    logger.info(f"Docs: http://localhost:{settings.api_port}/docs")
    logger.info(f"Startup status: {_overall_status(startup_status)}")
    logger.info("-" * 60)

    yield

    logger.info("GRC Chatbot shutting down...")


app = FastAPI(
    title="GRC Chatbot - LangGraph Agent",
    description=(
        "Hybrid GRC chatbot powered by LangGraph with RAG over Chroma and SQL over MySQL."
    ),
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.middleware("http")
async def log_requests(request, call_next):
    return await logging_middleware(request, call_next)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    chat.router,
    prefix="/api/v1",
    tags=["Chat"],
)

@app.get("/", tags=["Root"])
async def root(request: Request):
    components = getattr(request.app.state, "startup_status", _build_startup_status())

    return {
        "service": "GRC Chatbot",
        "architecture": "LangGraph + RAG + SQL",
        "vector_db": "Chroma",
        "status": _overall_status(components),
        "version": APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health",
        "chat": "/api/v1/chat",
        "components": components,
    }


@app.get("/api/v1/health", tags=["Health"])
async def health_check(request: Request):
    components = getattr(request.app.state, "startup_status", _build_startup_status())
    overall = _overall_status(components)

    return {
        "service": "GRC Chatbot",
        "status": overall,
        "components": components,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
