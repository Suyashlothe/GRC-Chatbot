from pathlib import Path

from langchain_ollama import ChatOllama
from loguru import logger

from app.config import get_settings
from app.sql.db import execute_raw
from app.sql.query_validator import validate_sql, SQLValidationError
from app.sql.schema_loader import SchemaLoader
from app.utils.helpers import strip_markdown_fences

settings = get_settings()

# ── Prompt ────────────────────────────────────────────────────────
_PROMPT_PATH = (
    Path(__file__).parent.parent / "graph" / "prompts" / "sql_prompt.txt"
)
_PROMPT_TEMPLATE = _PROMPT_PATH.read_text(encoding="utf-8")

# ── LLM ───────────────────────────────────────────────────────────
_llm = ChatOllama(
    base_url=settings.ollama_base_url,
    model=settings.ollama_model,
    temperature=0,                   
    timeout=settings.ollama_timeout,
)


class SQLAgent:
# Natural Language → SQL → Validate → Execute → Results
# Flow:
#     1. Pass Schema + user query → to Ollama
#     2. LLM generates the SQL query
#     3. validate_sql() checks the generated query
#     4. execute_raw() executes it against the database
#     5. Returns the structured results

    async def run(self, user_query: str) -> dict:
        logger.info(f"SQLAgent → '{user_query[:80]}'")

        # ── Step 1: Prompt injecting Schema ──────────────
        schema = SchemaLoader.get()
        prompt = _PROMPT_TEMPLATE.format(
            schema=schema,
            query=user_query,
            max_rows=settings.sql_max_rows,
        )

        # ── Step 2: SQL Generation from LLM ─────────────────────
        try:
            response = await _llm.ainvoke(prompt)
            raw_sql  = strip_markdown_fences(response.content)
            logger.debug(f"LLM generated SQL: {raw_sql}")

        except Exception as e:
            logger.error(f"LLM SQL generation failed: {e}")
            raise RuntimeError(f"LLM failed to generate SQL: {e}") from e

        # ── Step 3: Validation ─────────────────────────────────
        try:
            safe_sql = validate_sql(raw_sql)
            logger.debug(f"Validated SQL: {safe_sql}")

        except SQLValidationError as e:
            logger.warning(f"SQL blocked by validator: {e}")
            raise RuntimeError(f"SQL validation failed: {e}") from e

        # ── Step 4: Execution ──────────────────────────────────
        try:
            rows = execute_raw(safe_sql)
            logger.info(f"SQLAgent → {len(rows)} rows returned")

        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            raise RuntimeError(f"SQL execution error: {e}") from e

        # ── Step 5: Return result ────────────────────────────
        return {
            "sql":       safe_sql,    # For Audit log and user feedback
            "rows":      rows,
            "row_count": len(rows),
            "query":     user_query,  # For original user query reference
        }


# ── Singleton ─────────────────────────────────────────────────────
sql_agent = SQLAgent()