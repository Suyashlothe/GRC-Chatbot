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

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    ollama_base_url: str = "http://157.20.214.158:11434"
    ollama_model: str = "minimax-m2.1:cloud"
    ollama_temperature: float = 0.1
    ollama_timeout: int = 120

    chroma_path: str = str(BASE_DIR / "data" / "chroma")
    chroma_collection_grc: str = "grc_documents"

    mysql_host: str | None = None
    mysql_port: int = 3306
    mysql_user: str | None = None
    mysql_password: str | None = None
    mysql_db: str | None = None
    mysql_ssl: bool = False

    rag_chunk_size: int = 500
    rag_chunk_overlap: int = 100
    rag_top_k: int = 3

    sql_max_rows: int = 100
    sql_query_timeout: int = 30

    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_device: str = "cpu"

    log_level: str = "INFO"

    @property
    def mysql_configured(self) -> bool:
        return all(
            [
                self.mysql_host,
                self.mysql_user,
                self.mysql_password,
                self.mysql_db,
            ]
        )

    @property
    def mysql_url(self) -> str:
        if not self.mysql_configured:
            raise ValueError(
                "MySQL is not fully configured. Set mysql_host, mysql_user, "
                "mysql_password, and mysql_db in the environment or .env."
            )

        password = quote_plus(self.mysql_password or "")
        ssl = "?ssl=true" if self.mysql_ssl else ""

        return (
            f"mysql+pymysql://{self.mysql_user}:{password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}{ssl}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
