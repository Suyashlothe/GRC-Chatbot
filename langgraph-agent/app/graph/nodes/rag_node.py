from loguru import logger

from app.graph.state import AgentState
from app.rag.retriever import retrieve


async def rag_node(state: AgentState) -> AgentState:
    query = state["query"]

    try:
        # retriever seedha dicts return karta hai
        docs = retrieve(query)

        rag_context = [
            {
                "text":    doc["text"],
                "source":  doc["source"],
                "page":    doc["page"],
                "section": doc.get("section", "N/A"),
            }
            for doc in docs
        ]

        logger.info(f"RAG node → {len(rag_context)} chunks | '{query[:60]}'")

        return {
            **state,
            "rag_context":   rag_context,
            "rag_retrieved": True,
        }

    except Exception as e:
        logger.error(f"RAG node error: {e}")
        return {
            **state,
            "rag_context":   [],
            "rag_retrieved": False,
            "errors": state.get("errors", []) + [f"RAG error: {e}"],
        }