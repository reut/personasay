"""
Unit tests for Pydantic models
"""

import pytest
from pydantic import ValidationError

from app.models import (
    AppSettings,
    ChatRequest,
    DebateRequest,
    InitializeRequest,
    MemoryRequest,
    SummaryRequest,
)


class TestChatRequest:
    """Test ChatRequest model"""

    def test_valid_chat_request(self, sample_personas, sample_context):
        """Test creating a valid chat request"""
        request = ChatRequest(
            prompt="Test prompt",
            personas=sample_personas,
            context=sample_context,
        )
        assert request.prompt == "Test prompt"
        assert len(request.personas) == 2
        assert request.session_id is None
        assert request.generate_mock is False

    def test_chat_request_with_optional_fields(self, sample_personas, sample_context):
        """Test chat request with all optional fields"""
        request = ChatRequest(
            prompt="Test",
            personas=sample_personas,
            context=sample_context,
            session_id="session-123",
            history=[{"role": "user", "content": "Hi"}],
            generate_mock=True,
        )
        assert request.session_id == "session-123"
        assert len(request.history) == 1
        assert request.generate_mock is True

    def test_chat_request_missing_required_field(self, sample_personas, sample_context):
        """Test that missing required fields raise validation error"""
        with pytest.raises(ValidationError):
            ChatRequest(
                personas=sample_personas,
                context=sample_context,
                # Missing prompt
            )


class TestSummaryRequest:
    """Test SummaryRequest model"""

    def test_valid_summary_request(self, sample_context, sample_conversation_history):
        """Test creating a valid summary request"""
        request = SummaryRequest(context=sample_context, history=sample_conversation_history)
        assert len(request.history) == 4
        assert request.context["product_name"] == "Test Product"

    def test_summary_request_empty_history(self, sample_context):
        """Test summary request with empty history"""
        request = SummaryRequest(context=sample_context, history=[])
        assert request.history == []


class TestInitializeRequest:
    """Test InitializeRequest model"""

    def test_valid_initialize_request(self, sample_personas):
        """Test creating a valid initialize request"""
        request = InitializeRequest(personas=sample_personas)
        assert len(request.personas) == 2


class TestMemoryRequest:
    """Test MemoryRequest model"""

    def test_valid_memory_request(self):
        """Test creating a valid memory request"""
        request = MemoryRequest(persona_id="alex_trading", session_id="session-123")
        assert request.persona_id == "alex_trading"
        assert request.session_id == "session-123"

    def test_memory_request_without_session(self):
        """Test memory request without session ID"""
        request = MemoryRequest(persona_id="alex_trading")
        assert request.session_id is None


class TestDebateRequest:
    """Test DebateRequest model"""

    def test_valid_debate_request(self):
        """Test creating a valid debate request"""
        request = DebateRequest(
            topic="Should we implement this feature?",
            persona_ids=["alex_trading", "ben_analyst"],
            rounds=3,
        )
        assert request.topic == "Should we implement this feature?"
        assert len(request.persona_ids) == 2
        assert request.rounds == 3

    def test_debate_request_default_rounds(self):
        """Test debate request with default rounds"""
        request = DebateRequest(topic="Test topic", persona_ids=["alex_trading"])
        assert request.rounds == 3  # Default value


class TestAppSettings:
    """Test AppSettings model"""

    def test_default_settings(self):
        """Test default application settings"""
        settings = AppSettings()
        assert settings.app_name == "PersonaSay LangChain API"
        assert settings.version == "2.0.0"
        assert settings.environment == "development"  # Safe default
        assert settings.debug is False
        assert settings.secret_key == "dev-secret-key-change-in-production"
        assert (
            settings.cors_origins
            == "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000"
        )

    def test_production_settings(self, monkeypatch):
        """Test production environment settings"""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("SECRET_KEY", "secure-prod-key-123")
        monkeypatch.setenv("CORS_ORIGINS", "https://example.com")

        settings = AppSettings()
        assert settings.environment == "production"
        assert settings.secret_key == "secure-prod-key-123"
        assert settings.cors_origins == "https://example.com"
