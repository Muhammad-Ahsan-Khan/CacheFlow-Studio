# Algorithm Mapping

The assembly program and the web engine use the same cache model:

- Main memory: 20 values from 10 to 200
- Cache capacity: 5 values
- Default run: 30 random memory requests
- Policies: FIFO and LRU
- Metrics: hits, misses, accesses, and hit ratio

| Assembly module | Web engine equivalent | Purpose |
|---|---|---|
| `GenerateMemoryAccess` | `CacheFlowSimulator.run_random()` | Select a random memory index and read its value. |
| `ApplyFifoPolicy` | `CacheFlowSimulator.access()` in FIFO mode | Find a hit, fill empty lines, then replace using the FIFO cursor. |
| `ApplyLruPolicy` | `CacheFlowSimulator.access()` in LRU mode | Update timestamps on hits and replace the smallest timestamp on a full-cache miss. |
| `RenderCacheSnapshot` | `updateVisualizer()` | Show all five cache lines after every request. |
| `RenderFinalReport` | dashboard metrics and JSON report | Show hit, miss, total, and ratio values. |

## Integration note

A browser cannot execute MASM/Irvine32 code directly. Therefore, the project contains:

1. A refactored MASM console version for the COAL implementation.
2. A dependency-free Python engine that mirrors the same FIFO/LRU logic.
3. A local web server that streams every Python-engine event to the dashboard and prints the same event in the server terminal.

This structure keeps the assembly learning outcome intact while providing a practical UI/UX layer.
