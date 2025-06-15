refib
=====

.. image:: https://img.shields.io/pypi/v/refib.svg
   :target: https://pypi.org/project/refib/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/refib.svg
   :target: https://pypi.org/project/refib/
   :alt: Python Support

.. image:: https://img.shields.io/github/actions/workflow/status/uncorrelited/refib/tests.yml?branch=main&label=tests
   :target: https://github.com/uncorrelited/refib/actions
   :alt: Tests

.. image:: https://img.shields.io/badge/coverage-100%25-brightgreen.svg
   :target: https://github.com/uncorrelited/refib
   :alt: Coverage

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: black

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

.. image:: https://img.shields.io/pypi/dm/refib.svg
   :target: https://pypi.org/project/refib/
   :alt: Downloads

.. image:: https://img.shields.io/badge/dependencies-0-brightgreen.svg
   :target: https://github.com/uncorrelited/refib
   :alt: Dependencies

.. image:: https://img.shields.io/badge/overhead-0.12μs-brightgreen.svg
   :target: https://github.com/uncorrelited/refib/blob/main/CHANGELOG.rst
   :alt: Performance

Dead simple Python retry decorator with Fibonacci backoff. Zero dependencies. Under 100 lines of code.

.. code-block:: python

    from refib import refib

    @refib()
    def flaky_api_call():
        return requests.get("https://example.com/api").json()

Why Fibonacci?
--------------

Fibonacci sequence (1, 1, 2, 3, 5, 8, 13, 21, ...) has useful properties for retry delays:

1. **Starts small** - First few retries are quick (1s, 1s, 2s)
2. **Grows moderately** - Delay increases by ~61.8% each time (golden ratio)  
3. **More predictable** - Unlike exponential backoff (2ⁿ), Fibonacci grows linearly in the exponent

Compare growth rates:

- Exponential (base 2): 1, 2, 4, 8, 16, 32, 64, 128, 256, 512...
- Fibonacci: 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377...

Fibonacci balances fast initial retries with reasonable backoff.

Install
-------

.. code-block:: bash

    pip install refib

Usage
-----

.. code-block:: python

    @refib()
    def api_call():
        # Default: start=5 (5s delay), steps=10
        # Delays: 5, 8, 13, 21, 34, 55, 89, 144, 233, 377 seconds
        pass

    @refib(start=1, steps=3)
    def quick_call():
        # Start at position 1, retry 3 times
        # Delays: 1, 1, 2 seconds
        pass

    @refib(start=10, steps=5)
    def slow_call():
        # Start at position 10 for patient retries
        # Delays: 55, 89, 144, 233, 377 seconds
        pass

    @refib(exceptions=ValueError)
    def parse_data(text):
        # Only retry on ValueError
        return json.loads(text)

API
---

.. code-block:: python

    @refib(exceptions=Exception, start=5, steps=10)

- ``exceptions``: Exception(s) to catch. Default: ``Exception``
- ``start``: Starting Fibonacci position (1-indexed). Default: ``5``
- ``steps``: Number of retry attempts. Default: ``10``

Implementation
--------------

Pre-computes first 30 Fibonacci numbers for O(1) lookup. Calculates beyond position 30 in O(n) time.

.. code-block:: python

    _FIBONACCI_CACHE = (1, 1, 2, 3, 5, 8, 13, 21, 34, 55, ...)

    def _fibonacci(n):
        if n <= 30:
            return _FIBONACCI_CACHE[n - 1]
        # Calculate for n > 30

Mathematical Note
-----------------

We use 1-indexed Fibonacci positions (F₁=1, F₂=1, F₃=2...) rather than 0-indexed. This matches the mathematical convention and makes the API clearer: ``start=1`` gives you 1 second delay.

When to Use
-----------

+---------------------------+--------------------------------+
| Use refib when you want   | Use alternatives when you need |
+===========================+================================+
| Simple retry logic        | Jitter/randomization           |
+---------------------------+--------------------------------+
| Zero dependencies         | Async/await support            |
+---------------------------+--------------------------------+
| Fast startup (0.1ms)      | Complex retry strategies       |
+---------------------------+--------------------------------+
| Predictable delays        | Per-attempt callbacks          |
+---------------------------+--------------------------------+
| Under 100 lines to audit  | Exponential backoff            |
+---------------------------+--------------------------------+

Limitations
-----------

- No jitter (could cause thundering herd)
- No async support
- No per-attempt callback
- Fixed sequence (no custom delay functions)

For complex needs, use tenacity_ or backoff_.

.. _tenacity: https://github.com/jd/tenacity
.. _backoff: https://github.com/litl/backoff

Performance
-----------

vs other libraries:

- **16-94x less overhead** than alternatives
- **2.2x less memory** usage  
- **Equal or faster import** time

Run benchmark_comparison.py to verify all claims.

FAQ
---

**Q: Why Fibonacci instead of exponential backoff?**

A: Fibonacci grows more gently (φ ≈ 1.618x per step vs 2x). This means more retry attempts within the same time window, which is useful for transient failures.

**Q: Why not just use tenacity/backoff?**

A: Those are great libraries with more features. Use refib when you want something dead simple with zero dependencies and minimal overhead.

**Q: Can I use this in production?**

A: Yes. It has 100% test coverage, handles edge cases, and is used in production systems. But evaluate if you need features like jitter or callbacks.

**Q: What about asyncio support?**

A: Not supported. For async, use tenacity or backoff. We kept it simple on purpose.

**Q: Why positions instead of seconds?**

A: More predictable and easier to reason about. You know exactly how many seconds each retry will wait.

**Q: What does "refib" mean?**

A: **re**\try + **fib**\onacci. Short, memorable, and descriptive.

Contributing
------------

Issues and PRs welcome. Please:

- Keep it simple (no feature creep)
- Maintain 100% test coverage
- Follow existing code style

License
-------

MIT

Star History
------------

.. image:: https://api.star-history.com/svg?repos=uncorrelited/refib&type=Date
   :target: https://star-history.com/#uncorrelited/refib&Date
   :alt: Star History Chart