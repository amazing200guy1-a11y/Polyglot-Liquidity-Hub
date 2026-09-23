#!/usr/bin/env python3
"""
Benchmark: Go router fan-out throughput simulation (Python driver).

Simulates the throughput model of the Go channel multiplexer
by measuring Python-side message dispatch rates.

Run with: python benchmark.py
"""
import time
from dataclasses import dataclass
from typing import List


@dataclass
class TrafficVector:
    symbol: str
    price: float
    side: str


def simulate_fanout(messages: int, endpoints: int) -> float:
    """Simulate fan-out dispatch and return throughput in msg/s."""
    vectors = [TrafficVector("EURUSD", 1.0850, "BUY") for _ in range(messages)]
    sinks: List[List[TrafficVector]] = [[] for _ in range(endpoints)]
    t0 = time.perf_counter()
    for v in vectors:
        for sink in sinks:
            sink.append(v)
    return messages / (time.perf_counter() - t0)


if __name__ == "__main__":
    for msgs, eps in [(10_000, 3), (100_000, 5), (500_000, 10)]:
        rate = simulate_fanout(msgs, eps)
        print(f"msgs={msgs:>7,} | endpoints={eps} | {rate:>12,.0f} dispatches/s")