"""
Routes package for PersonaSay API
"""

from .chat import router as chat_router
from .debate import router as debate_router
from .memory import router as memory_router
from .summary import router as summary_router
from .system import router as system_router

__all__ = ["chat_router", "summary_router", "debate_router", "memory_router", "system_router"]
