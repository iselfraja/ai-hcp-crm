from langchain_groq import ChatGroq
from .config import get_settings
import os
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

def get_llm(model: str = None, temperature: float = 0.3):
    """Get a Groq LLM instance."""
    api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
    
    if not api_key or api_key == "":
        raise ValueError("GROQ_API_KEY is not set. Please set it in .env file.")
    
    # Use llama-3.1-8b-instant as default (working model)
    if model is None:
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    
    # Force use of working model if gemma2 is specified
    if model == "gemma2-9b-it":
        logger.warning("gemma2-9b-it is decommissioned. Using llama-3.1-8b-instant instead.")
        model = "llama-3.1-8b-instant"
    
    logger.info(f"Initializing Groq LLM with model: {model}")
    
    return ChatGroq(
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_tokens=2048,
        timeout=60,
        max_retries=3,
    )