from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage  # ✅ Added import
from ..database import get_db
from ..schemas import ChatRequest, ChatResponse
from ..agent.graph import agent_graph
from ..agent.state import AgentState
from .interaction import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Chat with the AI assistant."""
    logger.info(f"💬 Chat request: {request.message[:50]}...")
    
    try:
        if not agent_graph:
            return ChatResponse(
                reply="Error: Agent graph not initialized. Please check server logs.",
                extracted_data=None,
                suggested_followups=[],
                interaction_id=None
            )
        
        # ✅ Create the initial state with proper HumanMessage
        initial_state: AgentState = {
            "messages": [HumanMessage(content=request.message)],
            "user_query": request.message,
            "conversation_history": [],
            "hcp_id": None,
            "hcp_name": None,
            "interaction_id": request.interaction_id,
            "current_form_data": {},
            "extracted_entities": {},
            "validation_errors": [],
            "selected_tool": None,
            "tool_result": None,
            "tool_calls": [],
            "intent": None,
            "confidence": None,
            "needs_clarification": False,
            "clarification_question": None,
            "final_response": "",
            "errors": []
        }
        
        # Invoke the agent graph
        logger.info("🔄 Invoking agent graph...")
        result = agent_graph.invoke(initial_state)
        logger.info("✅ Agent graph execution completed")
        
        # ✅ Extract final response safely
        final_response = result.get("final_response", "No response from AI")
        
        # ✅ If final_response is an AIMessage, extract content
        if isinstance(final_response, AIMessage):
            final_response = final_response.content if final_response.content else "No response from AI"
        elif isinstance(final_response, dict):
            final_response = final_response.get("content", "No response from AI")
        
        logger.info(f"✅ Chat response: {final_response[:100] if final_response else 'None'}...")
        
        return ChatResponse(
            reply=final_response,
            extracted_data=result.get("extracted_entities"),
            suggested_followups=[],
            interaction_id=result.get("interaction_id")
        )
        
    except Exception as e:
        logger.error(f"❌ Chat error: {str(e)}", exc_info=True)
        return ChatResponse(
            reply=f"Error: {str(e)}",
            extracted_data=None,
            suggested_followups=[],
            interaction_id=None
        )