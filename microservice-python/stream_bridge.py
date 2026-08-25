"""
Polyglot-Liquidity-Hub — Stream Bridge (Python 3.12)

Asynchronous coordinator that:
  - Pulls live REST updates via httpx
  - Normalises payloads
  - Forwards clean messages toward the Go router / downstream stores
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("liquidity.bridge")

# ---------------------------------------------------------------------------
# Domain model
# ---------------------------------------------------------------------------

@dataclass(slots=True, frozen=True)
class StreamEvent:
    symbol: str
    side: str
    quantity: float
    price: float
    source: str
    received_at: datetime


# ---------------------------------------------------------------------------
# Bridge
# ---------------------------------------------------------------------------

class StreamBridge:
    """
    Lightweight async bridge.
    Designed to sit between external REST feeds and the Go multiplexer.
    """

    def __init__(
        self,
        upstream_url: str,
        poll_interval: float = 0.5,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.upstream_url = upstream_url
        self.poll_interval = poll_interval
        self._client = client
        self._own_client = client is None
        self._queue: asyncio.Queue[StreamEvent] = asyncio.Queue(maxsize=2048)
        self._running = False

    async def __aenter__(self) -> "StreamBridge":
        if self._own_client:
            self._client = httpx.AsyncClient(timeout=5.0)
        return self

    async def __aexit__(self, *exc: Any) -> None:
        self._running = False
        if self._own_client and self._client:
            await self._client.aclose()

    async def _fetch_once(self) -> Optional[StreamEvent]:
        assert self._client is not None
        try:
            resp = await self._client.get(self.upstream_url)
            resp.raise_for_status()
            data: Dict[str, Any] = resp.json()

            return StreamEvent(
                symbol=str(data.get("symbol", "UNKNOWN")),
                side=str(data.get("side", "B")),
                quantity=float(data.get("quantity", 0.0)),
                price=float(data.get("price", 0.0)),
                source=str(data.get("source", "rest")),
                received_at=datetime.now(timezone.utc),
            )
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            logger.warning("fetch failed: %s", exc)
            return None

    async def _producer(self) -> None:
        while self._running:
            event = await self._fetch_once()
            if event is not None:
                try:
                    self._queue.put_nowait(event)
                except asyncio.QueueFull:
                    logger.warning("bridge queue full — dropping event")
            await asyncio.sleep(self.poll_interval)

    async def consume(self) -> StreamEvent:
        """Block until the next normalised event is available."""
        return await self._queue.get()

    async def run(self) -> None:
        self._running = True
        await self._producer()


# ---------------------------------------------------------------------------
# Demo entry-point
# ---------------------------------------------------------------------------

async def main() -> None:
    # Example public-style endpoint (replace with real feed)
    url = os.getenv("LIQUIDITY_FEED_URL", "https://httpbin.org/json")

    async with StreamBridge(url, poll_interval=1.0) as bridge:
        # Run producer in background
        task = asyncio.create_task(bridge.run())

        # Consume a few events for demonstration
        for _ in range(3):
            try:
                event = await asyncio.wait_for(bridge.consume(), timeout=5.0)
                logger.info("bridged event: %s", event)
            except asyncio.TimeoutError:
                logger.info("no event within timeout")

        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())
