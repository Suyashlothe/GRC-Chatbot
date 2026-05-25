from pathlib import Path

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger

from app.config import get_settings
from app.graph.state import AgentState

settings = get_settings()

_SYSTEM_PROMPT = (
    Path(__file__).parent.parent / "prompts" / "responce_prompt.txt"
).read_text(encoding="utf-8")

_llm = ChatOllama(
    base_url=settings.ollama_base_url,
    model=settings.ollama_model,
    temperature=settings.ollama_temperature,
    timeout=settings.ollama_timeout,
)


async def llm_node(state: AgentState) -> AgentState:
    
    # Aggregated context + user query → Ollama → final response.
    
    context  = state.get("full_context", "No context available.")
    query    = state["query"]
    route    = state.get("route", "direct")

    user_message = (
        f"Context:\n{context}\n\n"
        f"User Question: {query}"
    )

    messages = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]

    try:
        response = await _llm.ainvoke(messages)
        answer   = response.content.strip()

        logger.info(
            f"LLM node → {len(answer)} chars | route: {route}"
        )

        return {
            **state,
            "final_response": answer,
            "messages": [
                HumanMessage(content=query),
                response,
            ],
        }

    except Exception as e:
        logger.error(f"LLM node error: {e}")
        return {
            **state,
            "final_response": (
                "I encountered an error generating a response. "
                "Please try again."
            ),
            "errors": state.get("errors", []) + [f"LLM error: {e}"],
        }