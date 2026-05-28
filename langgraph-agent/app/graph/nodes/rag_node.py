from loguru import logger

from app.graph.state import AgentState
from app.rag.retriever import retrieve


async def rag_node(state: AgentState) -> AgentState:
    query = state["query"]

    try:
        # retriever seedha dicts return karta hai
        docs = retrieve(query)

        blocked_terms = [
            "77 tables",
            "InnoDB",
            "ACID",
            "storage engine",
            "referential integrity"
            "database schema",
            "Identity & Access Management",
            "permissions",
            "permission groups",
            "sessions",
        ]

        rag_context = []

        for doc in docs:
            clean_text = doc["text"]

            for term in blocked_terms:
                clean_text = clean_text.replace(term, "")

            rag_context.append(
                {
                    "text": clean_text,
                    "source": doc["source"],
                    "page": doc["page"],
                    "section": doc.get("section", "N/A"),
                }
            )

        logger.info(f"RAG node → {len(rag_context)} chunks | '{query[:60]}'")

        return {
            "rag_context": rag_context,
            "rag_retrieved": True,
        }

    except Exception as e:
        logger.error(f"RAG node error: {e}")

        return {
            "rag_context": [],
            "rag_retrieved": False,
            "errors": state.get("errors", []) + [f"RAG error: {e}"],
        }