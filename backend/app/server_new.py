"""
PersonaSay Backend - LangChain Production Server
Official LangChain.com implementation with database persistence
Server-ready for deployment with independent persona agents
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies import get_or_none_langchain_manager, set_langchain_manager
from app.models import AppSettings
from app.routes import chat_router, debate_router, memory_router, summary_router, system_router

# Initialize application settings
app_settings = AppSettings()

# Initialize FastAPI app
app = FastAPI(
    title=app_settings.app_name,
    version=app_settings.version,
    description=app_settings.description,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include all route modules
app.include_router(system_router)
app.include_router(chat_router)
app.include_router(summary_router)
app.include_router(debate_router)
app.include_router(memory_router)


# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup when shutting down"""
    langchain_manager = get_or_none_langchain_manager()

    if langchain_manager:
        langchain_manager.cleanup()
        print("LangChain persona system cleaned up")


if __name__ == "__main__":
    import uvicorn

    print("Starting PersonaSay LangChain Production Server")
    print("=" * 60)
    print("Framework: LangChain (https://langchain.com/)")
    print("Architecture: Independent persona agents with persistent memory")
    print("Database: SQLAlchemy with persistent conversation storage")
    print("Features: Agent tools, memory persistence, concurrent processing")
    print("=" * 60)

    uvicorn.run("app.server:app", host="0.0.0.0", port=8000, reload=True)
