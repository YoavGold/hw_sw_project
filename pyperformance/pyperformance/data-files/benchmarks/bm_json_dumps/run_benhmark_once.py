#!/usr/bin/env python3
"""
Simple benchmark: repeatedly run json.dumps on a nested object.

Use with perf/flamegraph to capture call stacks quickly.
"""

import json
import time


# Example data object (nested, non-trivial)
DATA = {
    "key1": 0,
    "key2": True,
    "key3": "value",
    "key4": {"inner": [1, 2, 3], "text": "foo"},
    "key5": [str(i) for i in range(50)],
}


def bench_json_dumps(iters: int = 1_000_000) -> None:
    for _ in range(iters):
        json.dumps(DATA)


if __name__ == "__main__":
    # Run for a fixed duration rather than fixed iterations
    seconds = 10.0
    end = time.perf_counter() + seconds
    loops = 0
    while time.perf_counter() < end:
        json.dumps(DATA)
        loops += 1
    print(f"Ran {loops:,} dumps in {seconds:.1f}s (~{loops/seconds:,.0f}/s)")
