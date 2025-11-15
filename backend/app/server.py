"""
PersonaSay Backend - LangChain Production Server
Official LangChain.com implementation with database persistence
Server-ready for deployment with independent persona agents
"""

# Initialize logging - adjust level based on environment
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies import get_or_none_langchain_manager
from app.logging_config import setup_logging
from app.models import AppSettings
from app.routes import chat_router, debate_router, memory_router, summary_router, system_router

log_level = os.getenv("LOG_LEVEL", "INFO")
log_file = "logs/personasay.log" if os.getenv("LOG_TO_FILE", "true").lower() == "true" else None
logger = setup_logging(log_level=log_level, log_file=log_file)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup: Nothing to do here for now
    yield
    # Shutdown: Cleanup
    langchain_manager = get_or_none_langchain_manager()
    if langchain_manager:
        langchain_manager.cleanup()
        logger.info("LangChain persona system cleaned up")


# Initialize application settings
app_settings = AppSettings()

# Initialize FastAPI app with lifespan
# Disable docs in production for security
is_production = app_settings.environment == "production"

app = FastAPI(
    title=app_settings.app_name,
    version=app_settings.version,
    description=app_settings.description,
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    lifespan=lifespan,
)

# CORS middleware for frontend integration
# Get allowed origins from environment variable or app settings
allowed_origins_str = app_settings.cors_origins
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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


if __name__ == "__main__":
    import os

    import uvicorn

    # Get environment settings
    environment = os.getenv("ENVIRONMENT", "development")
    port = int(os.getenv("PORT", "8001"))
    host = os.getenv("HOST", "0.0.0.0")
    reload = environment == "development"

    logger.info("Starting PersonaSay LangChain Server")
    logger.info("=" * 60)
    logger.info(f"Environment: {environment}")
    logger.info(f"Host: {host}:{port}")
    logger.info("Framework: LangChain (https://langchain.com/)")
    logger.info("Architecture: Independent persona agents with persistent memory")
    logger.info("Database: SQLAlchemy with persistent conversation storage")
    logger.info("Features: Agent tools, memory persistence, concurrent processing")
    logger.info("=" * 60)

    uvicorn.run("app.server:app", host=host, port=port, reload=reload)
