from sqlalchemy import inspect
from loguru import logger

from app.sql.db import get_engine


class SchemaLoader:
# Loads the MySQL schema once at startup.
# The LLM does not inspect the DB on every request — it only uses the cached schema.
# 
# Flow:
#     main.py startup
#         -> SchemaLoader.load()
#         -> Schema string gets cached
#         -> sql_agent.py reads it using SchemaLoader.get()

    _schema: str | None = None
    _table_names: list[str] = []

    # ── Load (Startup pe ek baar) ─────────────────────────────────
    @classmethod
    async def load(cls) -> None:
        try:
            inspector = inspect(get_engine())
            tables = inspector.get_table_names()

            if not tables:
                logger.warning(" No tables found in MySQL database.")
                cls._schema = "No tables found."
                return

            lines = ["Database Schema:\n"]

            for table in tables:
                # Columns
                columns = inspector.get_columns(table)
                col_parts = []
                for col in columns:
                    nullable = "" if col.get("nullable", True) else " NOT NULL"
                    default  = f" DEFAULT {col['default']}" if col.get("default") else ""
                    col_parts.append(f"    {col['name']} {str(col['type'])}{nullable}{default}")

                # Primary Keys
                pk = inspector.get_pk_constraint(table)
                pk_info = ""
                if pk and pk.get("constrained_columns"):
                    pk_info = f"\n    PRIMARY KEY: {pk['constrained_columns']}"

                # Foreign Keys
                fks = inspector.get_foreign_keys(table)
                fk_lines = []
                for fk in fks:
                    fk_lines.append(
                        f"\n    FK: {fk['constrained_columns']} → "
                        f"{fk['referred_table']}.{fk['referred_columns']}"
                    )

                # Table block
                lines.append(f"TABLE: {table}")
                lines.append("\n".join(col_parts))
                if pk_info:
                    lines.append(pk_info)
                if fk_lines:
                    lines.append("".join(fk_lines))
                lines.append("")  # blank line between tables

            cls._schema      = "\n".join(lines)
            cls._table_names = tables

            logger.info(f" Schema loaded — {len(tables)} tables: {tables}")

        except Exception as e:
            logger.error(f" Schema loading failed: {e}")
            raise

    # ── Getters ───────────────────────────────────────────────────
    @classmethod
    def get(cls) -> str:
        #For query validation and prompt injection in sql_agent.py.
        if cls._schema is None:
            raise RuntimeError(
                "SchemaLoader not initialized. "
                "Call await SchemaLoader.load() in main.py startup."
            )
        return cls._schema

    @classmethod
    def get_table_names(cls) -> list[str]:
        # Available names for query validation and prompt injection.
        return cls._table_names

    @classmethod
    def is_loaded(cls) -> bool:
        return cls._schema is not None

    # ── Reload (Optional — admin endpoint ke liye) ────────────────
    @classmethod
    async def reload(cls) -> None:
    # Refresh the schema without a restart if a new table is added.
    # Can be called from a future admin endpoint.
        logger.info("Reloading schema...")
        cls._schema      = None
        cls._table_names = []
        await cls.load()
