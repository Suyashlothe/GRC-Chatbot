from app.graph.graph import grc_graph
from app.utils.logger import logger


class ChatService:

    async def process_message(self, message: str):

        logger.info(f"ChatService → '{message[:100]}'")

        initial_state = {
            # User query
            "query": message,

            # Routing
            "route": None,

            # RAG
            "rag_retrieved": False,
            "rag_context": [],

            # SQL
            "sql_retrieved": False,
            "sql_query": None,
            "sql_results": [],

            # Aggregation
            "full_context": "",

            # Final response
            "final_response": "",

            # Misc
            "messages": [],
            "errors": [],
        }

        try:
            # Run LangGraph
            result = await grc_graph.ainvoke(initial_state)

            logger.info(
                f"ChatService completed | route={result.get('route')}"
            )

            return {
                "success": True,
                "query": message,
                "response": result.get(
                    "final_response",
                    "No response generated."
                ),
                "route": result.get("route"),
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