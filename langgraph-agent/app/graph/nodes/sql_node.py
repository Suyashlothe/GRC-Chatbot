from loguru import logger
from app.graph.state import AgentState
from app.sql.sql_agent import sql_agent

# Natural language query → validated SQL → execute → rows.
async def sql_node(state: AgentState) -> AgentState:
    query = state['query']
    
    try:
        result = await sql_agent.run(query)
        logger.info(
            f"SQL node → {result['row_count']} rows | "
            f"sql: '{result['sql'][:60]}'"
            )
        
        return {
            **state,
            "sql_query":     result["sql"],
            "sql_results":   result["rows"],
            "sql_retrieved": True,
        }
    
    except Exception as e:
        logger.error(f'SQL node error: {e}')
        return {
            **state,
            "sql_query":     None,
            "sql_results":   [],
            "sql_retrieved": False,
            "errors": state.get("errors", []) + [f"SQL error: {e}"],
        }