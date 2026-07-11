from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from typing import Optional, List
from ..core.groq_client import get_llm
from .interaction import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])

class VoiceSummaryRequest(BaseModel):
    transcript: str

class VoiceSummaryResponse(BaseModel):
    summary: str
    sentiment: Optional[str] = None
    key_points: Optional[List[str]] = []

@router.post("/summarize", response_model=VoiceSummaryResponse)
async def summarize_voice_note(
    request: VoiceSummaryRequest,
    current_user = Depends(get_current_user)
):
    """Summarize a voice note transcript."""
    logger.info(f"📝 Summarizing voice note: {request.transcript[:50]}...")
    
    if not request.transcript or len(request.transcript.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Voice note transcript is too short or empty."
        )
    
    try:
        llm = get_llm(model="llama-3.1-8b-instant")
        
        prompt = f"""
        Provide a concise, professional summary of this HCP interaction:
        
        {request.transcript}
        
        Keep it under 100 words and professional.
        """
        response = llm.invoke(prompt)
        summary = response.content
        logger.info(f"✅ Summary generated: {summary[:50]}...")
        
        sentiment_prompt = f"""
        Analyze the sentiment and return only one word: Positive, Neutral, or Negative.
        
        {request.transcript}
        """
        sentiment_response = llm.invoke(sentiment_prompt)
        sentiment = sentiment_response.content.strip()
        if sentiment not in ["Positive", "Neutral", "Negative"]:
            sentiment = "Neutral"
        
        return VoiceSummaryResponse(
            summary=summary,
            sentiment=sentiment,
            key_points=["Meeting notes summarized successfully"]
        )
        
    except Exception as e:
        logger.error(f"❌ Voice summarization failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to summarize: {str(e)}"
        )