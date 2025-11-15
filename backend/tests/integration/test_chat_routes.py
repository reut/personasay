"""
Integration tests for chat routes
"""

from io import BytesIO
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.dependencies import set_langchain_manager


class TestChatRoute:
    """Test /chat endpoint"""

    @pytest.mark.asyncio
    @patch("app.routes.chat.LangChainPersonaManager")
    async def test_chat_auto_initialization(self, mock_manager_class, client, sample_chat_request):
        """Test chat endpoint auto-initializes if needed"""
        set_langchain_manager(None)

        mock_instance = Mock()
        mock_instance.personas = {}
        mock_instance.get_all_responses = AsyncMock(
            return_value=[
                {
                    "persona_id": "alex_trading",
                    "name": "Alex",
                    "response": "Test response",
                    "role": "Head of Trading",
                    "company": "Test Company",
                }
            ]
        )
        mock_manager_class.return_value = mock_instance

        response = client.post("/chat", json=sample_chat_request)

        assert response.status_code == 200
        data = response.json()
        assert "replies" in data
        assert "session_id" in data
        assert data["framework"] == "langchain"
        assert data["status"] == "success"

        # Verify manager was created
        mock_manager_class.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_chat_with_existing_manager(
        self, client, mock_langchain_manager, sample_chat_request
    ):
        """Test chat when manager already exists"""
        set_langchain_manager(mock_langchain_manager)

        response = client.post("/chat", json=sample_chat_request)

        assert response.status_code == 200
        data = response.json()
        assert len(data["replies"]) == 2
        assert data["total_personas"] == 2

    def test_chat_invalid_request(self, client):
        """Test chat with invalid request data"""
        invalid_request = {
            "prompt": "Test",
            # Missing required fields
        }

        response = client.post("/chat", json=invalid_request)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_chat_with_session_id(self, client, mock_langchain_manager, sample_chat_request):
        """Test chat maintains session ID"""
        set_langchain_manager(mock_langchain_manager)
        sample_chat_request["session_id"] = "test-session-456"

        response = client.post("/chat", json=sample_chat_request)

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-456"

    @patch("app.routes.chat.ChatOpenAI")
    @pytest.mark.asyncio
    async def test_chat_with_mock_generation(
        self, mock_openai, client, mock_langchain_manager, sample_chat_request
    ):
        """Test chat with SVG mock generation enabled"""
        set_langchain_manager(mock_langchain_manager)
        sample_chat_request["generate_mock"] = True

        # Mock OpenAI response for SVG generation
        mock_llm_instance = Mock()
        mock_response = Mock()
        mock_response.content = '{"bar_title": "Test", "bar1_name": "Metric", "bar1_value": 90}'
        mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_llm_instance

        response = client.post("/chat", json=sample_chat_request)

        assert response.status_code == 200
        data = response.json()
        assert "svg_mocks" in data["features_used"]


class TestChatAttachmentsRoute:
    """Test /chat-attachments endpoint"""

    @patch("app.routes.chat.LangChainPersonaManager")
    @pytest.mark.asyncio
    async def test_chat_attachments_without_files(
        self, mock_manager_class, client, sample_personas, sample_context
    ):
        """Test chat-attachments endpoint without files"""
        set_langchain_manager(None)

        mock_instance = Mock()
        mock_instance.get_all_responses = AsyncMock(
            return_value=[
                {"persona_id": "alex_trading", "name": "Alex", "response": "Test response"}
            ]
        )
        mock_manager_class.return_value = mock_instance

        import json

        response = client.post(
            "/chat-attachments",
            data={
                "prompt": "Test prompt",
                "personas": json.dumps(sample_personas),
                "context": json.dumps(sample_context),
                "generate_mock": "false",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "replies" in data
        assert data["framework"] == "langchain"

    @patch("app.routes.chat.ChatOpenAI")
    @pytest.mark.asyncio
    async def test_chat_attachments_with_image(
        self, mock_openai, client, sample_personas, sample_context
    ):
        """Test chat-attachments with image file"""
        import json

        # Mock vision model
        mock_llm_instance = Mock()
        mock_response = Mock()
        mock_response.content = "This is my analysis of the image"
        mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_llm_instance

        # Create a fake image file
        fake_image = BytesIO(b"fake image content")
        fake_image.name = "test.png"

        response = client.post(
            "/chat-attachments",
            data={
                "prompt": "What do you think?",
                "personas": json.dumps(sample_personas),
                "context": json.dumps(sample_context),
                "generate_mock": "false",
            },
            files={"files": ("test.png", fake_image, "image/png")},
        )

        assert response.status_code == 200
        data = response.json()
        assert "replies" in data
        assert "multimodal_vision" in data["features_used"]

    @pytest.mark.asyncio
    async def test_chat_attachments_invalid_json(self, client):
        """Test chat-attachments with invalid JSON in personas"""
        response = client.post(
            "/chat-attachments",
            data={
                "prompt": "Test",
                "personas": "invalid json{",
                "context": "{}",
            },
        )

        assert response.status_code == 500
        # Should get JSON parsing error
        detail = response.json()["detail"]
        assert (
            "json" in detail.lower() or "decode" in detail.lower() or "expecting" in detail.lower()
        )
