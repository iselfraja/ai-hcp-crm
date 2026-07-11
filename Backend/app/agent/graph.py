from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage, BaseMessage
from .state import AgentState
from .tools import (
    log_interaction, edit_interaction, summarize_interaction,
    extract_interaction_details, generate_followup_recommendations,
    search_hcp, get_interaction_history
)
from .prompts import SYSTEM_PROMPT
from ..core.groq_client import get_llm
import json
import re
import logging

logger = logging.getLogger(__name__)

# Initialize LLM
try:
    llm = get_llm(model="llama-3.1-8b-instant")
    logger.info("✅ LLM initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize LLM: {str(e)}")
    llm = None

# Define tools
tools = [
    log_interaction, 
    edit_interaction, 
    summarize_interaction, 
    extract_interaction_details,
    generate_followup_recommendations,
    search_hcp,
    get_interaction_history
]

# Bind tools to LLM
if llm:
    llm_with_tools = llm.bind_tools(tools)
    logger.info("✅ Tools bound to LLM")
else:
    llm_with_tools = None


def get_tool_calls_from_message(message):
    """Safely extract tool_calls from AIMessage or dict."""
    if isinstance(message, AIMessage):
        return message.tool_calls if hasattr(message, "tool_calls") else []
    if isinstance(message, dict):
        return message.get("tool_calls", [])
    return []


def get_message_content(message):
    """Safely extract content from message."""
    if isinstance(message, BaseMessage):
        return message.content if hasattr(message, "content") else ""
    if isinstance(message, dict):
        return message.get("content", "")
    return str(message) if message else ""


def generate_success_response(tool_name: str, result: str, state: AgentState, user_message: str) -> str:
    """Generate a professional response after tool execution."""
    
    logger.info(f"📝 Generating response for tool: {tool_name}")
    
    if tool_name == "log_interaction":
        hcp_name = state.get("hcp_name") or "the HCP"
        extracted = state.get("extracted_entities", {})
        date = extracted.get("date", "today")
        sentiment = extracted.get("sentiment", "Positive")
        
        return f"""✅ Interaction logged successfully! The details (HCP Name: {hcp_name}, Date: {date}, Sentiment: {sentiment}) have been automatically populated based on your summary. Would you like me to suggest a specific follow-up action, such as scheduling a meeting?"""
    
    elif tool_name == "edit_interaction":
        return f"""✅ I've updated the interaction successfully. The changes have been saved to the database. Is there anything else you'd like to modify?"""
    
    elif tool_name == "summarize_interaction":
        return f"""📝 Here's the summary of your interaction:\n\n{result}\n\nWould you like me to log this interaction or suggest follow-up actions?"""
    
    elif tool_name == "extract_interaction_details":
        try:
            data = json.loads(result)
            hcp_name = data.get("hcp_name", "the HCP")
            topics = data.get("topics_discussed", "the meeting")
            sentiment = data.get("sentiment", "Neutral")
            date = data.get("date", "today")
            
            return f"""✅ I've extracted the interaction details from your summary. Here's what I found:
• HCP: {hcp_name}
• Topics: {topics}
• Sentiment: {sentiment}
• Date: {date}

I can log this interaction for you. Would you like me to proceed?"""
        except:
            return f"""✅ I've extracted the interaction details. Would you like me to log this interaction for you?"""
    
    elif tool_name == "generate_followup_recommendations":
        return f"""📋 Based on your meeting, here are the recommended follow-up actions:

{result}

Would you like me to schedule any of these follow-ups for you?"""
    
    elif tool_name == "search_hcp":
        try:
            hcps = json.loads(result)
            if hcps and len(hcps) > 0:
                hcp_list = "\n".join([f"• {h.get('name')} - {h.get('specialty', 'N/A')} at {h.get('hospital', 'N/A')}" for h in hcps[:5]])
                return f"""🔍 I found these HCPs matching your search:

{hcp_list}

Would you like to view interactions for any of these HCPs?"""
            else:
                return "🔍 No HCPs found matching your search. Would you like to create a new HCP?"
        except:
            return "🔍 Search completed. Would you like to refine your search?"
    
    elif tool_name == "get_interaction_history":
        try:
            interactions = json.loads(result)
            if interactions and len(interactions) > 0:
                interaction_list = "\n".join([f"• {i.get('date', 'N/A')} - {i.get('type', 'Meeting')} - {i.get('topics', 'No topics')[:50]}" for i in interactions[:5]])
                return f"""📋 I found {len(interactions)} previous interactions:

{interaction_list}

Would you like more details about any of these interactions?"""
            else:
                return "📋 No previous interactions found for this HCP."
        except:
            return "📋 Interaction history retrieved. Would you like to see more details?"
    
    else:
        # Try to generate a response using LLM
        try:
            prompt = f"""
            Based on this tool result, generate a friendly response to the user.
            
            Tool used: {tool_name}
            Result: {result[:500]}
            User said: {user_message}
            
            Return a natural, conversational response that:
            1. Acknowledges what was done
            2. Provides relevant information
            3. Asks a follow-up question
            """
            response = llm.invoke(prompt)
            return response.content
        except:
            return f"✅ {result[:200]}\n\nIs there anything else I can help you with?"


def agent_node(state: AgentState) -> dict:
    """Agent node that processes the state and returns AIMessage."""
    logger.info("🤖 Agent node called")
    
    if not llm_with_tools:
        return {
            "messages": [AIMessage(content="Error: LLM not initialized.")],
            "final_response": "Error: LLM not initialized.",
            "selected_tool": None,
            "tool_calls": [],
            "errors": ["LLM not initialized"]
        }
    
    messages = state.get("messages", [])
    
    # Get user message
    user_message = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_message = msg.content
            break
        elif isinstance(msg, dict) and msg.get("role") == "user":
            user_message = msg.get("content", "")
            break
    
    # Check for tool results
    has_tool_result = False
    tool_result_content = None
    tool_name = state.get("selected_tool")
    
    for msg in messages:
        if isinstance(msg, ToolMessage):
            has_tool_result = True
            tool_result_content = msg.content
            break
    
    if has_tool_result:
        logger.info(f"📝 Generating response for tool: {tool_name}")
        final_message = generate_success_response(
            tool_name or "unknown",
            tool_result_content or "",
            state,
            user_message
        )
        
        return {
            "messages": [AIMessage(content=final_message)],
            "final_response": final_message,
            "selected_tool": None,
            "tool_calls": [],
            "errors": []
        }
    
    # Find last user message
    last_user_message = None
    for msg in messages:
        if isinstance(msg, HumanMessage):
            last_user_message = msg
        elif isinstance(msg, dict) and msg.get("role") == "user":
            last_user_message = HumanMessage(content=msg.get("content", ""))
    
    if not last_user_message:
        error_msg = "Please provide a message."
        return {
            "messages": [AIMessage(content=error_msg)],
            "final_response": error_msg,
            "selected_tool": None,
            "tool_calls": [],
            "errors": ["No user message found"]
        }
    
    logger.info(f"📝 User message: {get_message_content(last_user_message)[:50]}...")
    
    # Prepare messages for LLM
    llm_messages = [SystemMessage(content=SYSTEM_PROMPT)]
    
    for msg in messages:
        if isinstance(msg, HumanMessage):
            llm_messages.append(msg)
        elif isinstance(msg, AIMessage):
            if not hasattr(msg, "tool_calls") or not msg.tool_calls:
                llm_messages.append(msg)
    
    last_user_found = False
    for msg in llm_messages:
        if isinstance(msg, HumanMessage) and msg.content == last_user_message.content:
            last_user_found = True
            break
    if not last_user_found:
        llm_messages.append(last_user_message)
    
    # ✅ Add interaction_id context for summarize and followup
    context_parts = []
    if state.get("hcp_id"):
        context_parts.append(f"Current HCP ID: {state['hcp_id']}")
    if state.get("interaction_id"):
        context_parts.append(f"Current Interaction ID: {state['interaction_id']}")
        logger.info(f"📝 Context: Interaction ID {state['interaction_id']} available")
    
    if context_parts:
        context_message = f"\nCurrent Context:\n{chr(10).join(context_parts)}"
        llm_messages.append(HumanMessage(content=context_message))
    
    try:
        logger.info("🔄 Invoking LLM...")
        response = llm_with_tools.invoke(llm_messages)
        response_content = get_message_content(response)
        logger.info(f"📝 LLM response: {response_content[:100] if response_content else 'None'}...")
        
        tool_calls = get_tool_calls_from_message(response)
        
        if tool_calls:
            tool_names = [tc.get('name') for tc in tool_calls]
            logger.info(f"🔧 Tool calls: {tool_names}")
            
            # ✅ Fix: Ensure interaction_id is passed correctly for summarize and followup
            for tc in tool_calls:
                if tc.get('name') in ['summarize_interaction', 'generate_followup_recommendations']:
                    # If no interaction_id in args, use state's interaction_id
                    if 'interaction_id' not in tc.get('args', {}):
                        if state.get('interaction_id'):
                            tc['args']['interaction_id'] = state['interaction_id']
                            logger.info(f"📝 Added interaction_id {state['interaction_id']} to {tc.get('name')}")
            
            return {
                "messages": [response],
                "final_response": response_content if response_content else "Processing...",
                "selected_tool": tool_names[0] if tool_names else None,
                "tool_calls": tool_calls,
                "errors": []
            }
        else:
            logger.info("📝 No tool calls - returning direct response")
            return {
                "messages": [response],
                "final_response": response_content if response_content else "I'm here to help!",
                "selected_tool": None,
                "tool_calls": [],
                "errors": []
            }
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "messages": [AIMessage(content=error_msg)],
            "final_response": error_msg,
            "selected_tool": None,
            "tool_calls": [],
            "errors": [error_msg]
        }


def should_continue(state: AgentState) -> str:
    """Determine if we should continue to tools or end."""
    messages = state.get("messages", [])
    
    if not messages:
        return END
    
    for msg in messages:
        if isinstance(msg, ToolMessage):
            logger.info("📝 Tool result found - ending")
            return END
    
    last_message = messages[-1]
    tool_calls = get_tool_calls_from_message(last_message)
    
    if tool_calls:
        logger.info(f"🔧 Tool calls found - continuing to tools")
        return "tools"
    
    logger.info("✅ No tool calls - ending")
    return END


def execute_tool(tool_name: str, tool_args: dict) -> str:
    """Execute a tool by name with arguments."""
    tool_map = {
        "log_interaction": log_interaction,
        "edit_interaction": edit_interaction,
        "summarize_interaction": summarize_interaction,
        "extract_interaction_details": extract_interaction_details,
        "generate_followup_recommendations": generate_followup_recommendations,
        "search_hcp": search_hcp,
        "get_interaction_history": get_interaction_history,
    }
    
    if tool_name not in tool_map:
        return f"Tool {tool_name} not found"
    
    tool_func = tool_map[tool_name]
    
    try:
        if tool_name == "extract_interaction_details":
            text = tool_args.get("text") or tool_args.get("query") or tool_args.get("message", "")
            if not text:
                return "Error: Missing text"
            return tool_func.invoke(text)
            
        elif tool_name == "log_interaction":
            if "data_json" in tool_args:
                return tool_func.invoke(tool_args["data_json"])
            else:
                data = {}
                for key, value in tool_args.items():
                    if key not in ["data_json", "text", "query", "message"]:
                        data[key] = value
                return tool_func.invoke(json.dumps(data))
            
        elif tool_name == "edit_interaction":
            interaction_id = tool_args.get("interaction_id")
            update_data = tool_args.get("update_data", {})
            if not interaction_id:
                return "Error: Missing interaction_id"
            return tool_func.invoke(interaction_id, json.dumps(update_data))
            
        elif tool_name in ["summarize_interaction", "generate_followup_recommendations"]:
            # ✅ Fix: Get interaction_id from args
            interaction_id = tool_args.get("interaction_id")
            if not interaction_id:
                return "Error: Missing interaction_id. Please log an interaction first."
            logger.info(f"📝 Executing {tool_name} with interaction_id: {interaction_id}")
            return tool_func.invoke(interaction_id)
            
        elif tool_name == "search_hcp":
            query = tool_args.get("query") or tool_args.get("name") or tool_args.get("search", "")
            if not query:
                return "Error: Missing search query"
            return tool_func.invoke(query)
            
        elif tool_name == "get_interaction_history":
            hcp_id = tool_args.get("hcp_id")
            if not hcp_id:
                return "Error: Missing hcp_id"
            return tool_func.invoke(hcp_id)
            
        else:
            return tool_func.invoke(json.dumps(tool_args))
            
    except Exception as e:
        return f"Error executing tool: {str(e)}"


def tool_execution_node(state: AgentState) -> dict:
    """Execute tools and return results."""
    logger.info("🔧 Tool execution node called")
    
    messages = state.get("messages", [])
    
    if not messages:
        return {
            "messages": [AIMessage(content="No messages to process.")],
            "final_response": "No messages to process.",
            "selected_tool": None,
            "tool_calls": [],
            "errors": ["No messages"]
        }
    
    last_message = messages[-1]
    tool_calls = get_tool_calls_from_message(last_message)
    
    if not tool_calls and state.get("tool_calls"):
        tool_calls = state.get("tool_calls")
    
    if not tool_calls:
        return {
            "messages": [AIMessage(content="No tools to execute.")],
            "final_response": "No tools to execute.",
            "selected_tool": None,
            "tool_calls": [],
            "errors": ["No tool calls found"]
        }
    
    logger.info(f"🔧 Executing {len(tool_calls)} tool(s)")
    
    tool_results = []
    for tool_call in tool_calls:
        tool_name = tool_call.get("name", "unknown")
        tool_args = tool_call.get("args", {})
        tool_call_id = tool_call.get("id", "")
        
        logger.info(f"🔧 Executing tool: {tool_name}")
        logger.info(f"📝 Tool args: {json.dumps(tool_args, indent=2)}")
        
        try:
            result = execute_tool(tool_name, tool_args)
            logger.info(f"✅ Tool {tool_name} executed")
            
            tool_results.append(ToolMessage(content=result, tool_call_id=tool_call_id))
            
            state["selected_tool"] = tool_name
            state["tool_result"] = result
            
            if tool_name == "extract_interaction_details":
                try:
                    extracted = json.loads(result)
                    state["extracted_entities"] = extracted
                    if extracted.get("hcp_name"):
                        state["hcp_name"] = extracted.get("hcp_name")
                except:
                    pass
            
            if tool_name == "log_interaction":
                match = re.search(r"ID (\d+)", result)
                if match:
                    state["interaction_id"] = int(match.group(1))
                    logger.info(f"📝 Interaction ID saved: {state['interaction_id']}")
                    
        except Exception as e:
            error_msg = f"Error executing tool {tool_name}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            tool_results.append(ToolMessage(content=error_msg, tool_call_id=tool_call_id))
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(error_msg)
    
    return {
        "messages": tool_results,
        "final_response": "Tool execution completed.",
        "tool_calls": [],
        "errors": state.get("errors", [])
    }


def create_agent_graph():
    """Create and compile the LangGraph workflow."""
    logger.info("🔄 Creating agent graph...")
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_execution_node)
    
    workflow.set_entry_point("agent")
    
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    
    workflow.add_edge("tools", "agent")
    
    graph = workflow.compile()
    logger.info("✅ Agent graph compiled")
    return graph


try:
    agent_graph = create_agent_graph()
    logger.info("✅ Agent graph ready")
except Exception as e:
    logger.error(f"❌ Failed to create agent graph: {str(e)}")
    agent_graph = None