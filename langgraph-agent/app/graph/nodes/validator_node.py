from loguru import logger

from app.graph.state import AgentState

MIN_RESPONSE_LENGTH = 10


def validator_node(state: AgentState) -> AgentState:
    
    # Checks LLM response quelity before final output.
    # Handle Empty responses or very short responses 
    # Log Error state if there were any errors in previous nodes.
    
    response = state.get("final_response", "").strip()
    errors   = state.get("errors", [])

    # Empty / too short 
    if not response or len(response) < MIN_RESPONSE_LENGTH:
        logger.warning("Validator → response too short or empty")
        return {
            **state,
            "final_response": (
                "I was unable to generate a meaningful response. "
                "Please rephrase your question."
            ),
        }
    if errors:
        logger.warning(f"Validator → response OK but {len(errors)} error(s): {errors}")

    logger.info(f"Validator -> response length: {len(response)} chars")
    return state