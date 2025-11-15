"""
Integration tests for system routes
"""

from unittest.mock import Mock, patch

import pytest

from app.dependencies import set_langchain_manager


class TestSystemRoutes:
    """Test system endpoints"""

    def test_root_endpoint(self, client):
        """Test GET / returns system information"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "PersonaSay LangChain API"
        assert data["version"] == "2.0.0"
        assert "framework" in data
        assert "features" in data
        assert isinstance(data["features"], list)

    def test_health_check(self, client):
        """Test GET /health returns health status"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "environment" in data
        assert "version" in data
        assert "checks" in data
        assert data["checks"]["application"] == "healthy"
        assert "langchain_initialized" in data["checks"]
        assert "database" in data["checks"]

    def test_health_check_shows_initialization_status(self, client, mock_langchain_manager):
        """Test health check reflects initialization status"""
        # Not initialized
        set_langchain_manager(None)
        response = client.get("/health")
        assert response.json()["checks"]["langchain_initialized"] is False

        # Initialized
        set_langchain_manager(mock_langchain_manager)
        response = client.get("/health")
        assert response.json()["checks"]["langchain_initialized"] is True

    @patch("app.routes.system.app_settings")
    @patch("app.routes.system.LangChainPersonaManager")
    def test_initialize_langchain_personas(
        self, mock_manager_class, mock_settings, client, sample_personas
    ):
        """Test POST /langchain/initialize"""
        from unittest.mock import ANY

        # Mock app_settings to provide API key
        mock_settings.openai_api_key = "test-key"

        mock_instance = Mock()
        mock_manager_class.return_value = mock_instance

        payload = {"personas": sample_personas}

        response = client.post("/langchain/initialize", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "Successfully initialized" in data["message"]
        assert len(data["personas"]) == 2
        assert data["framework"] == "LangChain"
        assert data["status"] == "ready"

        # Verify manager was initialized with backend's API key
        mock_manager_class.assert_called_once_with(api_key="test-key")
        mock_instance.initialize_personas.assert_called_once()

    def test_reset_langchain_system(self, client, mock_langchain_manager):
        """Test POST /langchain/reset"""
        set_langchain_manager(mock_langchain_manager)

        response = client.post("/langchain/reset")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "reset"
        assert "successfully" in data["message"].lower()

        # Verify cleanup was called
        mock_langchain_manager.cleanup.assert_called_once()

    def test_reset_when_not_initialized(self, client):
        """Test reset works even when not initialized"""
        set_langchain_manager(None)

        response = client.post("/langchain/reset")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "reset"

    def test_get_system_stats(self, client, mock_langchain_manager):
        """Test GET /langchain/stats"""
        set_langchain_manager(mock_langchain_manager)

        response = client.get("/langchain/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["framework"] == "LangChain (langchain.com)"
        assert data["active_personas"] == 2
        assert len(data["persona_names"]) == 2
        assert "database_url" in data
        assert isinstance(data["features"], list)
        assert data["status"] == "operational"

    def test_get_stats_when_not_initialized(self, client):
        """Test stats endpoint when system not initialized"""
        set_langchain_manager(None)

        response = client.get("/langchain/stats")

        assert response.status_code == 503
        assert "not initialized" in response.json()["detail"].lower()


class TestDevEndpoints:
    """Test development endpoints"""

    @patch("app.routes.system.app_settings")
    def test_dev_test_personas_in_development(self, mock_settings, client):
        """Test /dev/test-personas in development mode"""
        mock_settings.environment = "development"

        # Need to reimport to pick up the new setting
        from app.routes import system as system_module

        response = client.get("/dev/test-personas")

        assert response.status_code == 200
        data = response.json()
        assert "test_personas" in data
        assert isinstance(data["test_personas"], list)
        assert data["count"] == len(data["test_personas"])
