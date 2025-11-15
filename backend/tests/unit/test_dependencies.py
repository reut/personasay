"""
Unit tests for dependency injection module
"""

from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from app.dependencies import (
    get_langchain_manager,
    get_or_none_langchain_manager,
    set_langchain_manager,
)
from app.langchain_personas import LangChainPersonaManager


class TestDependencies:
    """Test dependency management functions"""

    def test_set_and_get_langchain_manager(self, mock_langchain_manager):
        """Test setting and getting the LangChain manager"""
        set_langchain_manager(mock_langchain_manager)
        manager = get_langchain_manager()

        assert manager is not None
        assert manager == mock_langchain_manager

    def test_get_langchain_manager_when_not_initialized(self):
        """Test that getting uninitialized manager raises error"""
        set_langchain_manager(None)

        with pytest.raises(HTTPException) as exc_info:
            get_langchain_manager()

        assert exc_info.value.status_code == 503
        assert "not initialized" in exc_info.value.detail.lower()

    def test_get_or_none_returns_none_when_not_initialized(self):
        """Test get_or_none returns None instead of raising error"""
        set_langchain_manager(None)
        manager = get_or_none_langchain_manager()

        assert manager is None

    def test_get_or_none_returns_manager_when_initialized(self, mock_langchain_manager):
        """Test get_or_none returns manager when it exists"""
        set_langchain_manager(mock_langchain_manager)
        manager = get_or_none_langchain_manager()

        assert manager is not None
        assert manager == mock_langchain_manager

    def test_set_manager_to_none(self, mock_langchain_manager):
        """Test that we can reset manager to None"""
        set_langchain_manager(mock_langchain_manager)
        assert get_or_none_langchain_manager() is not None

        set_langchain_manager(None)
        assert get_or_none_langchain_manager() is None

    def test_manager_persists_across_calls(self, mock_langchain_manager):
        """Test that manager persists across multiple calls"""
        set_langchain_manager(mock_langchain_manager)

        manager1 = get_langchain_manager()
        manager2 = get_langchain_manager()
        manager3 = get_or_none_langchain_manager()

        assert manager1 is manager2
        assert manager2 is manager3
        assert all(m == mock_langchain_manager for m in [manager1, manager2, manager3])
