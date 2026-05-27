"""
Global constants for GRC Chatbot
"""


# ─────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────

APP_NAME = "GRC Chatbot"
APP_VERSION = "1.0.0"


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

API_PREFIX = "/api/v1"

CHAT_ROUTE = "/chat"
HEALTH_ROUTE = "/health"


# ─────────────────────────────────────────────
# RAG
# ─────────────────────────────────────────────

DEFAULT_TOP_K = 3

SUPPORTED_DOCUMENT_EXTENSIONS = [
    ".pdf",
    ".docx",
    ".txt",
    ".md",
]


# ─────────────────────────────────────────────
# SQL SAFETY
# ─────────────────────────────────────────────

ALLOWED_SQL_KEYWORDS = [
    "SELECT",
    "FROM",
    "WHERE",
    "GROUP BY",
    "ORDER BY",
    "LIMIT",
    "COUNT",
    "AVG",
    "SUM",
    "MIN",
    "MAX",
    "JOIN",
    "LEFT JOIN",
    "RIGHT JOIN",
]


BLOCKED_SQL_KEYWORDS = [
    "DROP",
    "DELETE",
    "TRUNCATE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "CREATE",
    "REPLACE",
]


# ─────────────────────────────────────────────
# CHAT ROUTING
# ─────────────────────────────────────────────

SQL_ROUTE = "sql"
RAG_ROUTE = "rag"
GENERAL_ROUTE = "general"


# ─────────────────────────────────────────────
# STATUS
# ─────────────────────────────────────────────

STATUS_SUCCESS = "success"
STATUS_ERROR = "error"


# ─────────────────────────────────────────────
# DEFAULT MESSAGES
# ─────────────────────────────────────────────

MSG_NO_RESULTS = "No results found."
MSG_INVALID_QUERY = "Invalid query."
MSG_INTERNAL_ERROR = "Internal server error."
MSG_RAG_EMPTY = "No relevant documents found."
MSG_SQL_BLOCKED = "Unsafe SQL query blocked."


# ─────────────────────────────────────────────
# DATABASE VIEWS
# ─────────────────────────────────────────────

IMPORTANT_VIEWS = [
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
]