"""
Feedback routes for Langfuse user feedback integration
Allows users to rate persona responses with thumbs up/down
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Import Langfuse
try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    logger.warning("Langfuse not available for feedback endpoint")


class FeedbackRequest(BaseModel):
    """Request model for user feedback"""
    trace_id: str
    score: float  # 0 for thumbs down, 1 for thumbs up
    comment: Optional[str] = None
    persona_id: Optional[str] = None
    persona_name: Optional[str] = None


@router.post("/feedback")
async def log_feedback(request: FeedbackRequest):
    """
    Log user feedback for a persona response to Langfuse
    
    Args:
        request: FeedbackRequest with trace_id, score, and optional comment
        
    Returns:
        Success message with feedback details
    """
    if not LANGFUSE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Langfuse feedback is not available. Install langfuse package."
        )
    
    try:
        # Get Langfuse configuration from settings
        from app.langchain_personas import Settings
        settings = Settings()
        
        if not settings.langfuse_enabled:
            raise HTTPException(
                status_code=503,
                detail="Langfuse is disabled in configuration"
            )
        
        if not settings.langfuse_public_key or not settings.langfuse_secret_key:
            raise HTTPException(
                status_code=503,
                detail="Langfuse keys not configured"
            )
        
        # Initialize Langfuse client
        langfuse = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host
        )
        
        # Build comment with persona info if provided
        full_comment = request.comment or ""
        if request.persona_name:
            full_comment = f"Persona: {request.persona_name}. " + full_comment
        
        # Log score to Langfuse
        langfuse.score(
            trace_id=request.trace_id,
            name="user_feedback",
            value=request.score,
            comment=full_comment if full_comment else None
        )
        
        # Flush to ensure score is sent
        langfuse.flush()
        
        logger.info(
            f"Logged feedback for trace {request.trace_id}: "
            f"score={request.score}, persona={request.persona_name}"
        )
        
        return {
            "status": "success",
            "message": "Feedback logged successfully",
            "trace_id": request.trace_id,
            "score": request.score,
            "persona": request.persona_name
        }
        
    except Exception as e:
        logger.error(f"Error logging feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to log feedback: {str(e)}"
        )


@router.get("/feedback/health")
async def feedback_health():
    """Check if feedback system is available and configured"""
    from app.langchain_personas import Settings
    settings = Settings()
    
    return {
        "langfuse_available": LANGFUSE_AVAILABLE,
        "langfuse_enabled": settings.langfuse_enabled,
        "langfuse_configured": bool(
            settings.langfuse_public_key and settings.langfuse_secret_key
        ),
        "status": "ready" if (
            LANGFUSE_AVAILABLE and 
            settings.langfuse_enabled and 
            settings.langfuse_public_key and 
            settings.langfuse_secret_key
        ) else "not_ready"
    }
