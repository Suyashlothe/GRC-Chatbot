import json
from pathlib import Path

from langchain_ollama import ChatOllama
from loguru import logger

from app.config import get_settings
from app.graph.state import AgentState

settings = get_settings()

_PROMPT = (
    Path(__file__).parent / "prompts" / "router_prompt.txt"
).read_text(encoding="utf-8")

_llm = ChatOllama(
    base_url=settings.ollama_base_url,
    model=settings.ollama_model,
    temperature=0,
    timeout=settings.ollama_timeout,
)

VALID_ROUTES = {"rag", "sql", "both", "direct"}


async def router_node(state: AgentState) -> AgentState:
    
    # rag | sql | both | direct
    query  = state["query"]
    prompt = _PROMPT.format(query=query)

    try:
        response = await _llm.ainvoke(prompt)
        raw      = response.content.strip()

        # Sometimes LLM can wrap the markdown, so clean it
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        parsed = json.loads(raw)
        route  = parsed.get("route", "direct").lower()

        if route not in VALID_ROUTES:
            logger.warning(f"Unknown route '{route}' → fallback: direct")
            route = "direct"

        logger.info(f"Router -> [{route}] | query: '{query[:60]}'")
        return {**state, "route": route}

    except json.JSONDecodeError as e:
        logger.warning(f"Router JSON parse failed: {e} → fallback: direct")
        return {
            **state,
            "route":  "direct",
            "errors": state.get("errors", []) + [f"Router parse error: {e}"],
        }
    except Exception as e:
        logger.error(f"Router failed: {e} → fallback: direct")
        return {
            **state,
            "route":  "direct",
            "errors": state.get("errors", []) + [f"Router error: {e}"],
        }


def routing_condition(state: AgentState) -> str:

    # LangGraph conditional edge function.

    # Decide which node to run after router:
    # RAG -> rag_node  
    # SQL -> sql_node
    # Both -> first RAG, then _after_rag  SQL
    # Nothing -> direct LLM
    
    route = state.get("route", "direct")

    mapping = {
        "rag":    "rag_node",
        "sql":    "sql_node",
        "both":   "rag_node",    # RAG is running first, then _after_rag will route to SQL
        "direct": "llm_node",    # No any retrieval, direct to LLM
    }

    next_node = mapping.get(route, "llm_node")
    logger.debug(f"routing_condition → {next_node}")
    return next_node