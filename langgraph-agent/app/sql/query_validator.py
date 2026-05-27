import re
from loguru import logger
from app.config import get_settings

settings = get_settings()


# ── Blocked SQL Keywords ──────────────────────────────────────────
# Even though views are used — keep this for defense in depth.
BLOCKED_KEYWORDS = [
    r"\bDROP\b",
    r"\bDELETE\b",
    r"\bUPDATE\b",
    r"\bINSERT\b",
    r"\bALTER\b",
    r"\bTRUNCATE\b",
    r"\bCREATE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bEXEC\b",
    r"\bEXECUTE\b",
    r"\bCALL\b",
    r"\bLOAD_FILE\b",
    r"\bOUTFILE\b",
    r"\bINFORMATION_SCHEMA\b",   # Restricted schema leak as well as access to metadata
    r"\bSYS\b",                  # Restricted system tables and potential access to metadata 
    r"--",                       # SQL comment injection
    r"/\*",                      # block comment
    r";\s*\w",                   # stacked queries — SELECT 1; DROP TABLE
    r"\bSLEEP\b",                # time-based blind injection
    r"\bBENCHMARK\b",            # load-based injection
    r"\bWAITFOR\b",
]

_BLOCKED_RE = [re.compile(p, re.IGNORECASE) for p in BLOCKED_KEYWORDS]

# ── Allowed Views ─────────────────────────────────────────────────
# Only these views can be queried. No direct table access allowed.
# SQL Views names
ALLOWED_VIEWS = {
    "vw_risk_summary",
    "vw_assessment_summary",
    "vw_assessment_scoring",
    "vw_asset_inventory",
    "vw_risk_history",
    "vw_mitigation_summary",
    "vw_framework_compliance",
    "vw_control_test_status",
    "vw_document_summary",
    "vw_open_risks",
    "vw_risk_trend",
    "vw_overdue_items",
    "vw_user_activity",
}


class SQLValidationError(Exception):
    pass


def _check_blocked_keywords(sql: str) -> None:
# Scan Dengarous Keywords 
    for pattern in _BLOCKED_RE:
        if pattern.search(sql):
            raise SQLValidationError(
                f"Blocked SQL pattern detected: '{pattern.pattern}'"
            )


def _check_only_select(sql: str) -> None:
# Only SELECT statements allowed. 
    first_word = sql.strip().split()[0].upper()
    if first_word != "SELECT":
        raise SQLValidationError(
            f"Only SELECT is allowed. Got: '{first_word}'"
        )



#Ensure the query only reference allowed views.
#Real table names are completely restricted.
#Example:
#    SELECT * FROM risks     <- BLOCKED (real table)
#    SELECT * FROM vw_risks  <- ALLOWED (view)

def _check_allowed_views(sql: str) -> None:

    # FROM aur JOIN ke baad table names extract karo
    table_pattern = re.compile(
        r"\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        re.IGNORECASE,
    )
    found_tables = table_pattern.findall(sql)

    for table in found_tables:
        table_lower = table.lower()
        if table_lower not in ALLOWED_VIEWS:
            raise SQLValidationError(
                f"Table/View '{table}' is not allowed. "
                f"Only these views are accessible: {sorted(ALLOWED_VIEWS)}"
            )


# Inject a LIMIT if it is missing.
# Cap the LIMIT if it exceeds the maximum allowed value.
def _enforce_limit(sql: str) -> str:

    sql = sql.rstrip(";").strip()

    if not re.search(r"\bLIMIT\b", sql, re.IGNORECASE):
        sql = f"{sql} LIMIT {settings.sql_max_rows}"
        logger.debug(f"LIMIT injected: {settings.sql_max_rows}")
    else:
        match = re.search(r"\bLIMIT\s+(\d+)", sql, re.IGNORECASE)
        if match:
            requested = int(match.group(1))
            if requested > settings.sql_max_rows:
                sql = re.sub(
                    r"\bLIMIT\s+\d+",
                    f"LIMIT {settings.sql_max_rows}",
                    sql,
                    flags=re.IGNORECASE,
                )
                logger.debug(
                    f"LIMIT capped: {requested} → {settings.sql_max_rows}"
                )

    return sql


# Main validation function — called by sql_agent.py.
# 
# Checks (order matters):
#     1. Only SELECT statements allowed
#     2. Dangerous keywords blocked
#     3. Only allowed views can be accessed
#     4. LIMIT clause enforced
# 
# Returns: safe, ready-to-execute SQL string
# Raises:  SQLValidationError if anything suspicious is found
def validate_sql(sql: str) -> str:

    if not sql or not sql.strip():
        raise SQLValidationError("Empty SQL query.")

    # Step 1
    _check_only_select(sql)

    # Step 2
    _check_blocked_keywords(sql)

    # Step 3 — Views check
    _check_allowed_views(sql)

    # Step 4 — LIMIT
    safe_sql = _enforce_limit(sql)

    logger.info(f"SQL validated | '{safe_sql[:80]}'")
    return safe_sql