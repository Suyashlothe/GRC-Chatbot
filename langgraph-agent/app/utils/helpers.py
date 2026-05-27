import re
from typing import Any


# ─────────────────────────────────────────────
# MARKDOWN / SQL HELPERS
# ─────────────────────────────────────────────

def strip_markdown_fences(text: str) -> str:
    """
    Remove markdown code fences from LLM responses.

    Example:
    ```sql
    SELECT * FROM users;
    ```

    becomes:
    SELECT * FROM users;
    """

    if not text:
        return ""

    text = text.strip()

    # Remove opening fence
    text = re.sub(
        r"^```[\w]*\s*",
        "",
        text,
        flags=re.MULTILINE,
    )

    # Remove closing fence
    text = re.sub(
        r"\s*```$",
        "",
        text,
        flags=re.MULTILINE,
    )

    return text.strip()


def clean_sql_query(query: str) -> str:
    """
    Clean and normalize SQL query before execution.
    """

    query = strip_markdown_fences(query)

    # Remove trailing semicolons
    query = query.strip().rstrip(";")

    return query + ";"


# ─────────────────────────────────────────────
# SAFE TYPE CONVERSIONS
# ─────────────────────────────────────────────

def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to int.
    """

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float.
    """

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# ─────────────────────────────────────────────
# TEXT UTILITIES
# ─────────────────────────────────────────────

def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate long text safely.
    """

    if not text:
        return ""

    text = str(text)

    if len(text) <= max_length:
        return text

    return text[:max_length].rstrip() + "..."


def normalize_whitespace(text: str) -> str:
    """
    Normalize spaces/newlines/tabs.
    """

    if not text:
        return ""

    return re.sub(r"\s+", " ", str(text)).strip()