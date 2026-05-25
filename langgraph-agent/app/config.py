from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── API ───────────────────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    # ── Ollama ────────────────────────────────────────────────────
    ollama_base_url: str = "http://157.20.214.158:11434"
    ollama_model: str = "minimax-m2.1:cloud"
    ollama_temperature: float = 0.1
    ollama_timeout: int = 120

    # ── Chroma ────────────────────────────────────────────────────
    chroma_path: str = str(BASE_DIR / "data" / "chroma")
    chroma_collection_grc: str = "grc_documents"

    # ── MySQL ─────────────────────────────────────────────────────
    mysql_host: str
    mysql_port: int = 3306
    mysql_user: str
    mysql_password: str
    mysql_db: str
    mysql_ssl: bool = False

    # ── RAG ───────────────────────────────────────────────────────
    rag_chunk_size: int = 500
    rag_chunk_overlap: int = 100
    rag_top_k: int = 3

    # ── SQL ───────────────────────────────────────────────────────
    sql_max_rows: int = 100
    sql_query_timeout: int = 30

    # ── Embeddings ────────────────────────────────────────────────
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_device: str = "cpu"

    # ── Logging ───────────────────────────────────────────────────
    log_level: str = "INFO"

    # ── Computed ──────────────────────────────────────────────────
    @property
    def mysql_url(self) -> str:
        password = quote_plus(self.mysql_password)

        ssl = "?ssl=true" if self.mysql_ssl else ""

        return (
            f"mysql+pymysql://{self.mysql_user}:{password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}{ssl}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()