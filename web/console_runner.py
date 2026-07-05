"""Run CacheFlow Studio entirely in a terminal using the shared core engine."""

from __future__ import annotations

import argparse
import time

from cacheflow_core import CacheEvent, CacheFlowSimulator


def print_event(event: CacheEvent) -> None:
    cache_text = ", ".join("__" if item is None else str(item) for item in event.cache)
    replacement = f" | evicted={event.evicted}" if event.evicted is not None else ""
    print(
        f"[{event.step:02}] index={event.index:02} value={event.value:03} "
        f"| {event.outcome:<4} | slot={event.slot}{replacement} | cache=[{cache_text}]"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="CacheFlow Studio console simulator")
    parser.add_argument("--policy", choices=("fifo", "lru"), default="fifo")
    parser.add_argument("--accesses", type=int, default=30)
    parser.add_argument("--delay", type=float, default=0.35, help="seconds between requests")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    if not 1 <= args.accesses <= 1000:
        parser.error("--accesses must be between 1 and 1000")
    if not 0 <= args.delay <= 10:
        parser.error("--delay must be between 0 and 10 seconds")

    simulator = CacheFlowSimulator(args.policy)
    print("\nCACHEFLOW STUDIO")
    print(f"Policy: {simulator.policy} | Requests: {args.accesses} | Seed: {args.seed}\n")

    for event in simulator.run_random(args.accesses, args.seed):
        print_event(event)
        time.sleep(args.delay)

    report = simulator.summary()
    print("\nFINAL REPORT")
    print(f"Hits: {report['hits']}")
    print(f"Misses: {report['misses']}")
    print(f"Total accesses: {report['accesses']}")
    print(f"Hit ratio: {report['hit_ratio']:.2f}%")


if __name__ == "__main__":
    main()
