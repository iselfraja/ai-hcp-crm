from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage
from ..database import get_db
from ..agent.graph import agent_graph
from ..agent.state import AgentState
from .interaction import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["agent"])

class AgentRequest(BaseModel):
    message: str
    interaction_id: Optional[int] = None
    hcp_id: Optional[int] = None
    conversation_id: Optional[str] = None
    current_form_data: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    message: str
    tool_calls: List[Dict[str, Any]] = []
    interaction_data: Optional[Dict[str, Any]] = None
    interaction_id: Optional[int] = None
    conversation_id: Optional[str] = None
    suggested_followups: Optional[List[str]] = None
    errors: List[str] = []

@router.post("/chat", response_model=AgentResponse)
async def agent_chat(
    request: AgentRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Send a message to the AI agent for processing."""
    logger.info(f"💬 Agent chat request: {request.message[:50]}...")
    
    try:
        if not agent_graph:
            raise HTTPException(
                status_code=500,
                detail="Agent graph not initialized"
            )
        
        # Prepare initial state
        state: AgentState = {
            "messages": [HumanMessage(content=request.message)],
            "user_query": request.message,
            "conversation_history": [],
            "hcp_id": request.hcp_id,
            "hcp_name": None,
            "interaction_id": request.interaction_id,
            "current_form_data": request.current_form_data or {},
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
            "errors": [],
            "needs_history": False,
            "needs_summary": False,
            "needs_followup": False
        }
        
        # Run the agent graph
        logger.info("🔄 Invoking agent graph...")
        result = agent_graph.invoke(state)
        logger.info("✅ Agent graph execution completed")
        
        # Extract final response
        final_response = result.get("final_response", "No response from AI")
        
        # If final_response is an AIMessage, extract content
        if hasattr(final_response, 'content'):
            final_response = final_response.content
        
        logger.info(f"✅ Agent response: {final_response[:100] if final_response else 'None'}...")
        
        return AgentResponse(
            message=final_response,
            tool_calls=result.get("tool_calls", []),
            interaction_data=result.get("extracted_entities"),
            interaction_id=result.get("interaction_id"),
            errors=result.get("errors", [])
        )
        
    except Exception as e:
        logger.error(f"❌ Agent error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent processing failed: {str(e)}"
        )