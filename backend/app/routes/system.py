"""
System endpoints for PersonaSay API (health, stats, initialize, reset)
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import (
    get_langchain_manager,
    get_or_none_langchain_manager,
    set_langchain_manager,
)
from app.langchain_personas import LangChainPersonaManager
from app.logging_config import get_logger
from app.models import AppSettings, InitializeRequest

router = APIRouter(tags=["system"])
logger = get_logger(__name__)

# We'll need app_settings from main, but for now let's make it a module variable
app_settings = AppSettings()


@router.get("/")
async def root():
    """Root endpoint with system information"""
    langchain_manager = get_or_none_langchain_manager()
    return {
        "message": "PersonaSay LangChain API",
        "version": app_settings.version,
        "description": app_settings.description,
        "framework": "LangChain (langchain.com)",
        "features": [
            "Independent persona agents",
            "Persistent memory with database",
            "Tool-equipped agents",
            "Concurrent processing",
            "Intelligent debugging agent",
            "Automated error fixing",
            "Production-ready deployment",
        ],
        "status": "running",
        "initialized": langchain_manager is not None,
    }


@router.get("/health")
async def health_check():
    """
    Health check endpoint for load balancers and monitoring
    Returns 200 OK if service is healthy, 503 if unhealthy
    """
    from sqlalchemy import create_engine, text

    langchain_manager = get_or_none_langchain_manager()
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": app_settings.environment,
        "version": app_settings.version,
        "checks": {
            "application": "healthy",
            "langchain_initialized": langchain_manager is not None,
            "database": "unknown",
        },
    }

    # Check database connectivity
    try:
        # Get database URL from environment or use default
        import os

        database_url = os.getenv("DATABASE_URL", "sqlite:///./data/personasay.db")
        engine = create_engine(database_url, pool_pre_ping=True)

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["checks"]["database"] = "unhealthy"
        health_status["status"] = "degraded"

    # Return appropriate status code
    if health_status["status"] == "healthy":
        return health_status
    else:
        raise HTTPException(status_code=503, detail=health_status)


@router.post("/langchain/initialize")
async def initialize_langchain_personas(request: InitializeRequest):
    """Initialize LangChain persona agents with database persistence"""
    try:
        logger.info(f"Initializing LangChain PersonaSay with {len(request.personas)} agents...")

        # Get API key from backend settings
        if not app_settings.openai_api_key:
            raise HTTPException(
                status_code=500, detail="OpenAI API key not configured in backend .env file"
            )

        # Create new LangChain manager
        langchain_manager = LangChainPersonaManager(api_key=app_settings.openai_api_key)

        # Initialize all personas
        langchain_manager.initialize_personas(request.personas)

        # Set the global manager
        set_langchain_manager(langchain_manager)

        return {
            "message": f"Successfully initialized {len(request.personas)} LangChain persona agents",
            "personas": [p["name"] for p in request.personas],
            "framework": "LangChain",
            "features": [
                "persistent_memory",
                "agent_tools",
                "independent_thinking",
                "intelligent_debugging",
            ],
            "database": "enabled",
            "status": "ready",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to initialize LangChain system: {str(e)}"
        )


@router.post("/langchain/reset")
async def reset_langchain_system():
    """Reset the LangChain persona system"""
    langchain_manager = get_or_none_langchain_manager()

    try:
        if langchain_manager:
            langchain_manager.cleanup()
        set_langchain_manager(None)

        return {"message": "LangChain system (personas) reset successfully", "status": "reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System reset failed: {str(e)}")


@router.get("/langchain/stats")
async def get_system_stats(manager: LangChainPersonaManager = Depends(get_langchain_manager)):
    """Get system statistics and status"""
    try:
        stats = {
            "framework": "LangChain (langchain.com)",
            "active_personas": len(manager.personas),
            "persona_names": [persona.name for persona in manager.personas.values()],
            "database_url": manager.settings.database_url,
            "features": [
                "Persistent memory",
                "Independent agent thinking",
                "Tool-equipped personas",
                "Concurrent processing",
                "Database persistence",
                "Intelligent debugging agent",
            ],
            "status": "operational",
        }

        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")


# Development/Testing endpoints
if app_settings.environment == "development":

    @router.get("/dev/test-personas")
    async def create_test_personas():
        """Create test personas for development"""
        test_personas = [
            {
                "id": "alex_trading",
                "name": "Alex",
                "role": "Head of Trading",
                "company": "Tier 1 Sportsbook",
                "avatar": "alex.png",
                "empathy_map": {
                    "think_and_feel": "Focused on risk management and maximizing profitability",
                    "hear": "Market intelligence and competitor analysis",
                    "see": "Real-time odds movements and market patterns",
                    "say_and_do": "Makes strategic trading decisions and manages risk exposure",
                    "pain": "Market inefficiencies and poor data quality affecting decisions",
                    "gain": "Better odds accuracy, reduced risk, increased profitability",
                },
            },
            {
                "id": "ben_analyst",
                "name": "Ben",
                "role": "Performance Analyst",
                "company": "Regional Operator",
                "avatar": "ben.png",
                "empathy_map": {
                    "think_and_feel": "Data-driven and analytical approach to optimization",
                    "hear": "Performance metrics and KPI discussions",
                    "see": "Dashboard data and performance trends",
                    "say_and_do": "Analyzes performance data and recommends improvements",
                    "pain": "Incomplete data and difficulty proving ROI of initiatives",
                    "gain": "Clear performance insights and actionable recommendations",
                },
            },
        ]

        return {
            "test_personas": test_personas,
            "message": "Test personas available for development",
            "count": len(test_personas),
        }
