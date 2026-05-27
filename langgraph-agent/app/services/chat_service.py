from app.graph.graph import graph
from app.utils.logger import logger


class ChatService:
    """
    Main chatbot service.

    Flow:
        User Query
            ↓
        LangGraph Router
            ↓
        ┌───────────────┬───────────────┐
        │               │               │
       SQL             RAG           Direct
        │               │               │
        └────── Aggregator + LLM ──────┘
                        ↓
                Human-friendly response
    """

    async def process_message(self, message: str) -> dict:
        logger.info(f"ChatService → '{message[:100]}'")

        try:
            # Initial graph state
            initial_state = {
                "query": message,
                "messages": [],
                "route": None,

                # SQL
                "sql_query": None,
                "sql_results": [],
                "sql_retrieved": False,

                # RAG
                "rag_context": [],
                "rag_retrieved": False,

                # Final
                "full_context": "",
                "final_response": "",
                "errors": [],
            }

            # Execute LangGraph
            result = await graph.ainvoke(initial_state)

            logger.info(
                f"ChatService completed | "
                f"route={result.get('route')} | "
                f"errors={len(result.get('errors', []))}"
            )

            return {
                "success": True,
                "query": message,

                # Human-readable answer
                "response": result.get(
                    "final_response",
                    "No response generated."
                ),

                # Debug / Audit
                "route": result.get("route"),
                "sql_query": result.get("sql_query"),
                "sql_results": result.get("sql_results", []),
                "rag_sources": [
                    {
                        "source": chunk.get("source"),
                        "page": chunk.get("page"),
                        "section": chunk.get("section"),
                    }
                    for chunk in result.get("rag_context", [])
                ],

                "errors": result.get("errors", []),
            }

        except Exception as e:
            logger.exception(f"ChatService failed: {e}")

            return {
                "success": False,
                "query": message,
                "response": (
                    "I encountered an internal error while "
                    "processing your request."
                ),
                "errors": [str(e)],
            }


# Singleton instance
chat_service = ChatService()