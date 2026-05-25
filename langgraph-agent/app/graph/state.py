from typing import Annotated, Any, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):

    # Input
    user_id:    str
    session_id: str
    query:      str

    # Routing 
    route: Literal["rag", "sql", "both", "direct"] | None

    # RAG 
    rag_context:   list[dict[str, Any]]
    rag_retrieved: bool

    # SQL 
    sql_query:     str | None
    sql_results:   list[dict[str, Any]]
    sql_retrieved: bool

    # Aggregated 
    full_context: str

    # LLM Output 
    final_response: str

    # Conversation History
    messages: Annotated[list, add_messages]

    # Meta 
    errors:      list[str]
    retry_count: int