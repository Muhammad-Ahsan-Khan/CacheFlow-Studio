from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "web"))

from cacheflow_core import CacheFlowSimulator  # noqa: E402


class CacheFlowCoreTests(unittest.TestCase):
    def test_fifo_replaces_oldest_inserted_value(self) -> None:
        simulator = CacheFlowSimulator("FIFO", cache_size=3, memory=(10, 20, 30, 40))
        events = list(simulator.run_sequence([0, 1, 2, 3]))

        self.assertEqual(events[-1].outcome, "MISS")
        self.assertEqual(events[-1].evicted, 10)
        self.assertEqual(events[-1].cache, (40, 20, 30))

    def test_lru_replaces_least_recently_used_value(self) -> None:
        simulator = CacheFlowSimulator("LRU", cache_size=3, memory=(10, 20, 30, 40))
        events = list(simulator.run_sequence([0, 1, 2, 0, 3]))

        self.assertEqual(events[-1].evicted, 20)
        self.assertEqual(events[-1].cache, (10, 40, 30))

    def test_hit_counters_and_ratio(self) -> None:
        simulator = CacheFlowSimulator("FIFO", cache_size=2, memory=(10, 20))
        list(simulator.run_sequence([0, 1, 0, 1]))

        self.assertEqual(simulator.hits, 2)
        self.assertEqual(simulator.misses, 2)
        self.assertEqual(simulator.accesses, 4)
        self.assertEqual(simulator.hit_ratio, 50.0)

    def test_random_run_is_reproducible_with_seed(self) -> None:
        first = CacheFlowSimulator("FIFO")
        second = CacheFlowSimulator("FIFO")
        first_indices = [event.index for event in first.run_random(12, seed=42)]
        second_indices = [event.index for event in second.run_random(12, seed=42)]

        self.assertEqual(first_indices, second_indices)


if __name__ == "__main__":
    unittest.main()
