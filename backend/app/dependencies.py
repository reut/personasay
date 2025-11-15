"""
Dependency injection and shared state for PersonaSay API
"""

from typing import Optional

from fastapi import HTTPException

from app.langchain_personas import LangChainPersonaManager

# Global LangChain persona manager
langchain_manager: Optional[LangChainPersonaManager] = None


def get_langchain_manager() -> LangChainPersonaManager:
    """Dependency to ensure LangChain manager is available"""
    global langchain_manager
    if langchain_manager is None:
        raise HTTPException(
            status_code=503,
            detail="LangChain system not initialized. Please initialize personas first at /langchain/initialize",
        )
    return langchain_manager


def set_langchain_manager(manager: Optional[LangChainPersonaManager]):
    """Set the global LangChain manager"""
    global langchain_manager
    langchain_manager = manager


def get_or_none_langchain_manager() -> Optional[LangChainPersonaManager]:
    """Get LangChain manager without raising error if not initialized"""
    global langchain_manager
    return langchain_manager
