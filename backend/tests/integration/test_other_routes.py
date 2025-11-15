"""
Integration tests for summary, debate, and memory routes
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.dependencies import set_langchain_manager


class TestSummaryRoute:
    """Test /summary endpoint"""

    @patch("app.routes.summary.ChatOpenAI")
    @pytest.mark.asyncio
    async def test_generate_summary(
        self,
        mock_openai,
        client,
        mock_langchain_manager,
        sample_context,
        sample_conversation_history,
    ):
        """Test POST /summary generates summary"""
        set_langchain_manager(mock_langchain_manager)

        # Mock OpenAI response
        mock_llm_instance = Mock()
        mock_response = Mock()
        mock_response.content = """## Key Insights
Test insights

## Concerns & Opportunities
Test concerns

## 6. Success Metrics & KPIs
KPI 1: Test KPI"""
        mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_llm_instance

        payload = {
            "context": sample_context,
            "history": sample_conversation_history,
        }

        response = client.post("/summary", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert data["framework"] == "langchain"
        assert data["status"] == "success"
        assert "Success Metrics & KPIs" in data["summary"]

    def test_summary_empty_history(self, client, mock_langchain_manager, sample_context):
        """Test summary with empty history"""
        set_langchain_manager(mock_langchain_manager)

        payload = {"context": sample_context, "history": []}

        response = client.post("/summary", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "No conversation history" in data["summary"]

    @patch("app.routes.summary.ChatOpenAI")
    def test_summary_not_initialized(
        self, mock_openai, client, sample_context, sample_conversation_history
    ):
        """Test summary works without LangChain initialization (uses backend API key directly)"""
        set_langchain_manager(None)

        # Mock OpenAI response
        mock_llm_instance = Mock()
        mock_response = Mock()
        mock_response.content = "## Key Insights\nTest\n## 6. Success Metrics & KPIs\nKPI 1: Test"
        mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_llm_instance

        payload = {
            "context": sample_context,
            "history": sample_conversation_history,
        }

        response = client.post("/summary", json=payload)

        # Summary endpoint now works without LangChain initialization
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert data["status"] == "success"


class TestDebateRoute:
    """Test /langchain/debate endpoint"""

    @pytest.mark.asyncio
    async def test_debate_multiple_rounds(self, client, mock_langchain_manager):
        """Test POST /langchain/debate with multiple rounds"""
        set_langchain_manager(mock_langchain_manager)

        payload = {
            "topic": "Should we implement this feature?",
            "persona_ids": ["alex_trading", "ben_analyst"],
            "rounds": 3,
        }

        response = client.post("/langchain/debate", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["debate_topic"] == payload["topic"]
        assert data["rounds"] == 3
        assert len(data["participants"]) == 2
        assert "debate_history" in data
        assert data["framework"] == "langchain"
        assert data["status"] == "completed"

    @pytest.mark.asyncio
    async def test_debate_single_round(self, client, mock_langchain_manager):
        """Test debate with single round"""
        set_langchain_manager(mock_langchain_manager)

        payload = {
            "topic": "Test topic",
            "persona_ids": ["alex_trading"],
            "rounds": 1,
        }

        response = client.post("/langchain/debate", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["rounds"] == 1

    def test_debate_not_initialized(self, client):
        """Test debate when system not initialized"""
        set_langchain_manager(None)

        payload = {"topic": "Test", "persona_ids": ["alex_trading"]}

        response = client.post("/langchain/debate", json=payload)

        assert response.status_code == 503


class TestMemoryRoutes:
    """Test memory and history endpoints"""

    def test_get_persona_memory(self, client, mock_langchain_manager):
        """Test GET /langchain/memory/{persona_id}"""
        set_langchain_manager(mock_langchain_manager)

        response = client.get("/langchain/memory/alex_trading")

        assert response.status_code == 200
        data = response.json()
        assert data["persona_id"] == "alex_trading"
        assert "memory" in data
        assert data["framework"] == "langchain"
        assert data["persistence"] == "database"

    def test_get_conversation_history(self, client, mock_langchain_manager):
        """Test GET /langchain/conversation/{session_id}"""
        set_langchain_manager(mock_langchain_manager)

        response = client.get("/langchain/conversation/test-session-123")

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-123"
        assert "history" in data
        assert data["framework"] == "langchain"
        assert "total_messages" in data

    def test_memory_not_initialized(self, client):
        """Test memory endpoint when not initialized"""
        set_langchain_manager(None)

        response = client.get("/langchain/memory/alex_trading")

        assert response.status_code == 503

    def test_conversation_not_initialized(self, client):
        """Test conversation endpoint when not initialized"""
        set_langchain_manager(None)

        response = client.get("/langchain/conversation/test-session")

        assert response.status_code == 503
