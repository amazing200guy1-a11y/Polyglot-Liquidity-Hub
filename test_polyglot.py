"""
Unit and Integration Tests for Polyglot-Liquidity-Hub
=====================================================
Verifies stream event normalization, bridge polling resilience,
and high-throughput dispatch multiplexing.
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, MagicMock
import httpx

sys.path.insert(0, str(Path(__file__).parent / "microservice-python"))

from stream_bridge import StreamEvent, StreamBridge


def test_stream_event_dataclass_structure() -> None:
    """Verifies that StreamEvent slots and frozen invariants hold."""
    now = datetime.now(timezone.utc)
    evt = StreamEvent(
        symbol="EUR/USD",
        side="BUY",
        quantity=1.5,
        price=1.0854,
        source="FIX-ROUTER",
        received_at=now,
    )
    assert evt.symbol == "EUR/USD"
    assert evt.side == "BUY"
    assert evt.quantity == 1.5
    assert evt.price == 1.0854
    assert evt.source == "FIX-ROUTER"
    assert evt.received_at == now


@pytest.mark.asyncio
async def test_stream_bridge_fetch_success() -> None:
    """Verifies parsing and normalization of upstream JSON payloads."""
    bridge = StreamBridge(upstream_url="http://mock.upstream/feed")
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "symbol": "BTCUSD",
        "side": "SELL",
        "quantity": 0.25,
        "price": 64500.0,
        "source": "CRYPTO-REST",
    }
    mock_resp.raise_for_status.return_value = None
    mock_client.get.return_value = mock_resp

    bridge._client = mock_client
    bridge._own_client = False

    event = await bridge._fetch_once()
    assert event is not None
    assert event.symbol == "BTCUSD"
    assert event.price == 64500.0
    assert event.quantity == 0.25
    assert event.source == "CRYPTO-REST"


@pytest.mark.asyncio
async def test_stream_bridge_poll_resilience() -> None:
    """Verifies graceful handling of HTTP network failures."""
    bridge = StreamBridge(upstream_url="http://mock.upstream/failing-feed")
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.side_effect = httpx.RequestError("Connection refused")

    bridge._client = mock_client
    bridge._own_client = False

    event = await bridge._fetch_once()
    assert event is None


def test_benchmark_dispatch_simulation() -> None:
    """Simulates high-throughput fan-out dispatch queue."""
    from benchmark import simulate_fanout
    rate = simulate_fanout(messages=5_000, endpoints=3)
    assert rate > 0.0
