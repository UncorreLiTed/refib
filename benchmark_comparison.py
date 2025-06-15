#!/usr/bin/env python
"""
Quick benchmark comparing refib with tenacity and backoff.
Run: pip install tenacity backoff
"""

import time
import statistics


def benchmark_overhead():
    """Compare decorator overhead."""
    
    def noop():
        return 42
    
    # Baseline
    times = []
    for _ in range(10000):
        start = time.perf_counter_ns()
        noop()
        times.append(time.perf_counter_ns() - start)
    baseline = statistics.mean(times) / 1000  # microseconds
    
    print("Decorator overhead (10k calls):")
    print("Baseline: {:.3f}μs".format(baseline))
    
    # refib
    try:
        from refib import refib
        decorated = refib()(noop)
        times = []
        for _ in range(10000):
            start = time.perf_counter_ns()
            decorated()
            times.append(time.perf_counter_ns() - start)
        overhead = statistics.mean(times) / 1000 - baseline
        print("refib:    {:.3f}μs (+{:.3f}μs)".format(statistics.mean(times) / 1000, overhead))
        refib_overhead = overhead
    except ImportError:
        print("refib: NOT INSTALLED")
        refib_overhead = 1
    
    # backoff
    try:
        import backoff
        decorated = backoff.on_exception(backoff.expo, Exception, max_tries=10)(noop)
        times = []
        for _ in range(10000):
            start = time.perf_counter_ns()
            decorated()
            times.append(time.perf_counter_ns() - start)
        overhead = statistics.mean(times) / 1000 - baseline
        ratio = overhead / refib_overhead
        print("backoff:  {:.3f}μs (+{:.3f}μs, {:.1f}x)".format(statistics.mean(times) / 1000, overhead, ratio))
    except ImportError:
        print("backoff: NOT INSTALLED")
    
    # tenacity
    try:
        from tenacity import retry, stop_after_attempt
        decorated = retry(stop=stop_after_attempt(10))(noop)
        times = []
        for _ in range(10000):
            start = time.perf_counter_ns()
            decorated()
            times.append(time.perf_counter_ns() - start)
        overhead = statistics.mean(times) / 1000 - baseline
        ratio = overhead / refib_overhead
        print("tenacity: {:.3f}μs (+{:.3f}μs, {:.1f}x)".format(statistics.mean(times) / 1000, overhead, ratio))
    except ImportError:
        print("tenacity: NOT INSTALLED")


if __name__ == "__main__":
    benchmark_overhead()