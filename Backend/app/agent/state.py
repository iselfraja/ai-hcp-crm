from typing import List, Dict, Any, Optional, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """State management for LangGraph agent workflow."""
    messages: Annotated[List[BaseMessage], add_messages]
    user_query: Optional[str]
    conversation_history: List[Dict[str, str]]
    hcp_id: Optional[int]
    hcp_name: Optional[str]
    interaction_id: Optional[int]
    current_form_data: Dict[str, Any]
    extracted_entities: Dict[str, Any]
    validation_errors: List[str]
    selected_tool: Optional[str]
    tool_result: Optional[str]
    tool_calls: List[Dict[str, Any]]
    intent: Optional[str]
    confidence: Optional[float]
    needs_clarification: bool
    clarification_question: Optional[str]
    final_response: str
    errors: List[str]
    
    # ✅ New flags for multi-step workflows
    needs_history: bool
    needs_summary: bool
    needs_followup: bool