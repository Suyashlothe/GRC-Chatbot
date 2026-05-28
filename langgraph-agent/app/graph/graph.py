from langgraph.graph import StateGraph, END
from loguru import logger

from app.graph.state import AgentState
from app.graph.router import router_node, routing_condition

from app.graph.nodes.rag_node import rag_node
from app.graph.nodes.sql_node import sql_node
from app.graph.nodes.aggregator_node import aggregator_node
from app.graph.nodes.llm_node import llm_node
from app.graph.nodes.validator_node import validator_node


def build_graph() -> StateGraph:
    g = StateGraph(AgentState)

    # -------------------------
    # Nodes
    # -------------------------
    g.add_node("router_node", router_node)
    g.add_node("rag_node", rag_node)
    g.add_node("sql_node", sql_node)
    g.add_node("aggregator_node", aggregator_node)
    g.add_node("llm_node", llm_node)
    g.add_node("validator_node", validator_node)

    # -------------------------
    # Entry Point
    # -------------------------
    g.set_entry_point("router_node")

    # -------------------------
    # Router → First Split
    # -------------------------
    g.add_conditional_edges(
        "router_node",
        routing_condition,
        {
            "rag_node": "rag_node",
            "sql_node": "sql_node",
            "both": "rag_node",     # BOTH starts with RAG
            "llm_node": "llm_node",
        },
    )

    # -------------------------
    # RAG flow
    # -------------------------
    

    # If BOTH → go from RAG → SQL → aggregator
    g.add_conditional_edges(
        "rag_node",
        lambda state: "sql_node" if state.get("route") == "both" else "aggregator_node",
        {
            "sql_node": "sql_node",
            "aggregator_node": "aggregator_node",
        },
    )

    # -------------------------
    # SQL flow
    # -------------------------
    g.add_edge("sql_node", "aggregator_node")

    # -------------------------
    # Aggregator → LLM
    # -------------------------
    g.add_edge("aggregator_node", "llm_node")

    # -------------------------
    # LLM → Validator
    # -------------------------
    g.add_edge("llm_node", "validator_node")

    # -------------------------
    # End
    # -------------------------
    g.add_edge("validator_node", END)

    return g.compile()


# -------------------------
# Compiled singleton
# -------------------------
grc_graph = build_graph()
logger.info("LangGraph compiled successfully (FIXED DAG).")