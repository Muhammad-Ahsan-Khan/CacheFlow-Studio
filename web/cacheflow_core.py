"""Core cache simulation logic used by both the console and web dashboard."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from random import Random
from typing import Iterable, Iterator, Literal, Optional

Policy = Literal["FIFO", "LRU"]
DEFAULT_MEMORY = tuple(range(10, 201, 10))


@dataclass(frozen=True)
class CacheEvent:
    step: int
    policy: Policy
    index: int
    value: int
    outcome: Literal["HIT", "MISS"]
    slot: int
    evicted: Optional[int]
    cache: tuple[Optional[int], ...]
    hits: int
    misses: int
    accesses: int
    hit_ratio: float

    def to_dict(self) -> dict:
        return asdict(self)


class CacheFlowSimulator:
    """A fixed-size cache with FIFO and LRU replacement policies."""

    def __init__(
        self,
        policy: str = "FIFO",
        cache_size: int = 5,
        memory: Iterable[int] = DEFAULT_MEMORY,
    ) -> None:
        normalized = policy.upper()
        if normalized not in {"FIFO", "LRU"}:
            raise ValueError("policy must be FIFO or LRU")
        if cache_size <= 0:
            raise ValueError("cache_size must be greater than zero")

        self.policy: Policy = normalized  # type: ignore[assignment]
        self.memory = tuple(memory)
        if not self.memory:
            raise ValueError("memory must contain at least one value")

        self.cache: list[Optional[int]] = [None] * cache_size
        self._fifo_cursor = 0
        self._lru_age = [0] * cache_size
        self._clock = 0
        self.hits = 0
        self.misses = 0
        self.accesses = 0

    @property
    def hit_ratio(self) -> float:
        return (self.hits / self.accesses * 100.0) if self.accesses else 0.0

    def access(self, index: int) -> CacheEvent:
        if not 0 <= index < len(self.memory):
            raise IndexError(f"memory index must be between 0 and {len(self.memory) - 1}")

        value = self.memory[index]
        self._clock += 1
        evicted: Optional[int] = None

        try:
            slot = self.cache.index(value)
            outcome: Literal["HIT", "MISS"] = "HIT"
            self.hits += 1
            if self.policy == "LRU":
                self._lru_age[slot] = self._clock
        except ValueError:
            outcome = "MISS"
            self.misses += 1

            try:
                slot = self.cache.index(None)
            except ValueError:
                if self.policy == "FIFO":
                    slot = self._fifo_cursor
                    self._fifo_cursor = (self._fifo_cursor + 1) % len(self.cache)
                else:
                    slot = min(range(len(self.cache)), key=self._lru_age.__getitem__)
                evicted = self.cache[slot]

            self.cache[slot] = value
            if self.policy == "LRU":
                self._lru_age[slot] = self._clock

        self.accesses += 1
        return CacheEvent(
            step=self.accesses,
            policy=self.policy,
            index=index,
            value=value,
            outcome=outcome,
            slot=slot,
            evicted=evicted,
            cache=tuple(self.cache),
            hits=self.hits,
            misses=self.misses,
            accesses=self.accesses,
            hit_ratio=round(self.hit_ratio, 2),
        )

    def run_random(self, count: int, seed: Optional[int] = None) -> Iterator[CacheEvent]:
        if count <= 0:
            raise ValueError("count must be greater than zero")
        randomizer = Random(seed)
        for _ in range(count):
            yield self.access(randomizer.randrange(len(self.memory)))

    def run_sequence(self, indices: Iterable[int]) -> Iterator[CacheEvent]:
        for index in indices:
            yield self.access(index)

    def summary(self) -> dict:
        return {
            "policy": self.policy,
            "hits": self.hits,
            "misses": self.misses,
            "accesses": self.accesses,
            "hit_ratio": round(self.hit_ratio, 2),
            "cache": self.cache.copy(),
        }
