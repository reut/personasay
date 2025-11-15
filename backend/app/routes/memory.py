"""
Memory and conversation history endpoints for PersonaSay API
"""

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_langchain_manager
from app.langchain_personas import LangChainPersonaManager

router = APIRouter(tags=["memory"])


@router.get("/langchain/memory/{persona_id}")
async def get_persona_memory(
    persona_id: str, manager: LangChainPersonaManager = Depends(get_langchain_manager)
):
    """Get persistent memory for a specific persona"""
    try:
        memory_data = manager.get_persona_memory(persona_id)
        return {
            "persona_id": persona_id,
            "memory": memory_data,
            "framework": "langchain",
            "persistence": "database",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory retrieval failed: {str(e)}")


@router.get("/langchain/conversation/{session_id}")
async def get_conversation_history(
    session_id: str, manager: LangChainPersonaManager = Depends(get_langchain_manager)
):
    """Get full conversation history for a session"""
    try:
        history = manager.get_conversation_history(session_id)
        return {
            "session_id": session_id,
            "history": history,
            "framework": "langchain",
            "total_messages": len(history),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")
