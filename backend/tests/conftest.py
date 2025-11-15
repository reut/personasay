"""
Shared pytest fixtures for PersonaSay backend tests
"""

from unittest.mock import MagicMock, Mock

import pytest
from fastapi.testclient import TestClient

from app.dependencies import set_langchain_manager
from app.langchain_personas import LangChainPersonaManager
from app.server import app


@pytest.fixture
def client(tmp_path):
    """FastAPI test client with database directory setup"""
    import os

    # Create data directory for tests
    data_dir = tmp_path / "data"
    data_dir.mkdir(exist_ok=True)

    # Set environment variables for tests
    os.environ["DATABASE_URL"] = f"sqlite:///{data_dir}/personasay.db"
    os.environ["OPENAI_API_KEY"] = "test-key-for-tests"

    with TestClient(app=app) as c:
        yield c

    # Cleanup
    for key in ["DATABASE_URL", "OPENAI_API_KEY"]:
        if key in os.environ:
            del os.environ[key]


@pytest.fixture
def sample_personas():
    """Sample persona data for testing"""
    return [
        {
            "id": "alex_trading",
            "name": "Alex",
            "role": "Head of Trading",
            "title": "Head of Trading",
            "company": "Tier 1 Sportsbook",
            "avatar": "alex.png",
            "empathy_map": {
                "think_and_feel": "Focused on risk management",
                "hear": "Market intelligence",
                "see": "Real-time odds movements",
                "say_and_do": "Makes strategic trading decisions",
                "pain": "Market inefficiencies",
                "gain": "Better odds accuracy",
            },
        },
        {
            "id": "ben_analyst",
            "name": "Ben",
            "role": "Performance Analyst",
            "title": "Performance Analyst",
            "company": "Regional Operator",
            "avatar": "ben.png",
            "empathy_map": {
                "think_and_feel": "Data-driven approach",
                "hear": "Performance metrics",
                "see": "Dashboard data",
                "say_and_do": "Analyzes performance data",
                "pain": "Incomplete data",
                "gain": "Clear performance insights",
            },
        },
    ]


@pytest.fixture
def sample_context():
    """Sample product context for testing"""
    return {
        "product_name": "Test Product",
        "feature": "Test Feature",
        "description": "A test feature for unit testing",
    }


@pytest.fixture
def sample_chat_request(sample_personas, sample_context):
    """Sample chat request data"""
    return {
        "prompt": "What do you think about this feature?",
        "personas": sample_personas,
        "context": sample_context,
        "api_key": "test-api-key-12345",
        "session_id": "test-session-123",
        "history": [],
        "generate_mock": False,
    }


@pytest.fixture
def sample_conversation_history():
    """Sample conversation history"""
    return [
        {"role": "user", "content": "Hello, what do you think about the new odds feature?"},
        {
            "role": "assistant",
            "content": "As a trading expert, I find this feature promising.",
            "sender": "Alex",
        },
        {"role": "user", "content": "What about performance implications?"},
        {
            "role": "assistant",
            "content": "From a performance standpoint, we need to monitor latency.",
            "sender": "Ben",
        },
    ]


@pytest.fixture
def mock_langchain_manager(sample_personas):
    """Mock LangChain persona manager"""
    mock_manager = Mock(spec=LangChainPersonaManager)

    # Create simple mock personas without circular references
    mock_personas = {}
    for p in sample_personas:
        persona_mock = Mock()
        persona_mock.name = p["name"]
        persona_mock.role = p["role"]
        persona_mock.company = p["company"]
        mock_personas[p["id"]] = persona_mock

    mock_manager.personas = mock_personas
    mock_manager.settings = Mock(database_url="sqlite:///test.db")

    # Mock get_all_responses
    async def mock_get_responses(*args, **kwargs):
        return [
            {
                "persona_id": "alex_trading",
                "name": "Alex",
                "response": "This is a test response from Alex",
                "role": "Head of Trading",
                "company": "Tier 1 Sportsbook",
                "thinking": "Strategic analysis...",
                "tools_used": [],
            },
            {
                "persona_id": "ben_analyst",
                "name": "Ben",
                "response": "This is a test response from Ben",
                "role": "Performance Analyst",
                "company": "Regional Operator",
                "thinking": "Performance analysis...",
                "tools_used": [],
            },
        ]

    mock_manager.get_all_responses = mock_get_responses
    mock_manager.get_persona_memory = Mock(return_value={"messages": []})
    mock_manager.get_conversation_history = Mock(return_value=[])
    mock_manager.cleanup = Mock()

    return mock_manager


@pytest.fixture(autouse=True)
def reset_dependencies():
    """Reset global dependencies after each test"""
    yield
    set_langchain_manager(None)


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    mock_response = Mock()
    mock_response.content = "This is a mocked AI response"
    return mock_response


@pytest.fixture
def sample_svg_data():
    """Sample data for SVG generation"""
    return {
        "bar_title": "Performance Metrics",
        "bar1_name": "Speed",
        "bar1_value": 95.0,
        "bar2_name": "Accuracy",
        "bar2_value": 88.0,
        "bar3_name": "Coverage",
        "bar3_value": 92.0,
        "line_title": "Trend Analysis",
        "line1_label": "Jan",
        "line1_value": 450,
        "line2_label": "Feb",
        "line2_value": 820,
        "line3_label": "Mar",
        "line3_value": 1250,
        "line4_label": "Apr",
        "line4_value": 1700,
        "donut_title": "Distribution",
        "donut1_name": "Feature A",
        "donut1_value": 50,
        "donut2_name": "Feature B",
        "donut2_value": 30,
        "donut3_name": "Feature C",
        "donut3_value": 20,
    }
