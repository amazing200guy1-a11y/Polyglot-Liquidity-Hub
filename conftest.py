"""Shared pytest fixtures for Polyglot-Liquidity-Hub Python microservice tests."""
import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture()
def mock_httpx_client():
    """Return a mock async httpx client for stream coordinator tests."""
    client = AsyncMock()
    client.post = AsyncMock(return_value=AsyncMock(status_code=200, json=lambda: {"ok": True}))
    return client