from loguru import logger

from app.graph.state import AgentState


def aggregator_node(state: AgentState) -> AgentState:
    
    # Merge the  RAG chunks + SQL rows into a single context string for the LLM.
    parts: list[str] = []

    # RAG context 
    if state.get("rag_retrieved") and state.get("rag_context"):
        parts.append("=== DOCUMENT CONTEXT ===")
        for i, chunk in enumerate(state["rag_context"], 1):
            parts.append(
                f"[{i}] Source : {chunk['source']}\n"
                f"     Page   : {chunk['page']}\n"
                f"     Section: {chunk['section']}\n"
                f"     Content: {chunk['text']}"
            )

    # SQL context 
    if state.get("sql_retrieved") and state.get("sql_results"):
        parts.append("=== DATABASE RESULTS ===")
        parts.append(f"Query executed: {state.get('sql_query', 'N/A')}")
        for i, row in enumerate(state["sql_results"], 1):
            parts.append(f"[{i}] {row}")

    # Fallback
    if not parts:
        full_context = "No additional context retrieved."
    else:
        full_context = "\n\n".join(parts)

    logger.info(
        f"Aggregator -> "
        f"RAG: {len(state.get('rag_context', []))} chunks | "
        f"SQL: {len(state.get('sql_results', []))} rows"
    )

    return { "full_context": full_context}