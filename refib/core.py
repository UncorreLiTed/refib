"""
Core implementation of the refib decorator.
"""

import functools
import time

# Pre-computed Fibonacci numbers for positions 1-30
_FIBONACCI_CACHE = (
    1,
    1,
    2,
    3,
    5,
    8,
    13,
    21,
    34,
    55,
    89,
    144,
    233,
    377,
    610,
    987,
    1597,
    2584,
    4181,
    6765,
    10946,
    17711,
    28657,
    46368,
    75025,
    121393,
    196418,
    317811,
    514229,
    832040,
)


def _fibonacci(n):
    """Calculate the nth Fibonacci number (1-indexed)."""
    if n <= 0:
        raise ValueError("Fibonacci position must be positive")

    # Use pre-computed values for n <= 30
    if n <= 30:
        return _FIBONACCI_CACHE[n - 1]

    # Calculate for n > 30
    a, b = _FIBONACCI_CACHE[28], _FIBONACCI_CACHE[29]  # F(29), F(30)
    for _ in range(n - 30):
        a, b = b, a + b
    return b


def refib(exceptions=Exception, start=5, steps=10):
    """
    Retry decorator using Fibonacci sequence for delays.

    Args:
        exceptions: Exception(s) to catch. Default: Exception
        start: Starting Fibonacci number position. Default: 5 (F(5)=5 seconds)
        steps: Maximum retry attempts. Default: 10

    Example:
        @refib()  # Retries up to 10 times, delays: 5s, 8s, 13s, 21s...
        def api_call():
            return requests.get(url).json()

        @refib(start=1, steps=3)  # Quick retries: 1s, 1s, 2s
        def quick_call():
            return do_something()
    """
    # Validate parameters
    if steps <= 0:
        raise ValueError("steps must be greater than 0")
    if start <= 0:
        raise ValueError("start must be greater than 0")

    # Validate exception types
    if isinstance(exceptions, tuple):
        for exc in exceptions:
            if not (isinstance(exc, type) and issubclass(exc, BaseException)):
                raise TypeError(
                    "All exception types must be subclasses of BaseException"
                )
    else:
        if not (isinstance(exceptions, type) and issubclass(exceptions, BaseException)):
            raise TypeError("Exception type must be a subclass of BaseException")

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            position = start

            for attempt in range(steps):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == steps - 1:
                        raise

                    time.sleep(_fibonacci(position))
                    position += 1

        return wrapper

    return decorator
