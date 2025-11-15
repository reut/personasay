"""
Pydantic models for PersonaSay API requests and responses
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Allow extra fields from .env file
    )

    # App metadata
    app_name: str = "PersonaSay LangChain API"
    version: str = "2.0.0"
    description: str = "LangChain-based multi-agent persona system with persistent memory"

    # Environment configuration
    environment: str = "development"
    debug: bool = False
    secret_key: str = "dev-secret-key-change-in-production"
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000"

    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # API Keys
    openai_api_key: str = ""

    # Database
    database_url: str = "sqlite:///./data/personasay.db"
    redis_url: str = "redis://localhost:6379"

    # Logging
    log_level: str = "INFO"
    log_to_file: str = "true"


class ChatRequest(BaseModel):
    """Chat request with LangChain agents"""

    prompt: str = Field(..., description="User message to send to personas")
    personas: List[Dict[str, Any]] = Field(..., description="List of active personas")
    context: Dict[str, Any] = Field(..., description="Product context for the conversation")
    session_id: Optional[str] = Field(None, description="Conversation session ID")
    history: Optional[List[Dict[str, Any]]] = Field([], description="Previous conversation history")
    generate_mock: Optional[bool] = Field(
        False, description="Whether to generate SVG mock visualizations"
    )
    # Note: API key is read from backend .env, not from request


class SummaryRequest(BaseModel):
    """Summary generation request with KPI generation"""

    context: Dict[str, Any] = Field(..., description="Product context")
    history: List[Dict[str, Any]] = Field(..., description="Conversation history to summarize")
    session_id: Optional[str] = Field(None, description="Session ID for context")
    personas: Optional[List[Dict[str, Any]]] = Field(
        None, description="Selected personas for focused summary"
    )
    # Note: API key is read from backend .env, not from request


class InitializeRequest(BaseModel):
    """Initialize personas request"""

    personas: List[Dict[str, Any]] = Field(..., description="Persona data to initialize")
    # Note: API key is read from backend .env, not from request


class MemoryRequest(BaseModel):
    """Memory retrieval request"""

    persona_id: str = Field(..., description="Persona ID to get memory for")
    session_id: Optional[str] = Field(None, description="Specific session ID")


class DebateRequest(BaseModel):
    """Multi-agent debate request"""

    topic: str = Field(..., description="Debate topic")
    persona_ids: List[str] = Field(..., description="Personas to participate in debate")
    rounds: int = Field(3, description="Number of debate rounds")
    # Note: API key is read from backend .env, not from request
