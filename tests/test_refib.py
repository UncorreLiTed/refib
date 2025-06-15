"""
Tests for the refib decorator.
"""

import time
import pytest
from unittest.mock import Mock

from refib import refib


class TestFibRetry:
    """Test cases for refib decorator."""

    def test_successful_call_no_retry(self):
        """Test that successful calls don't retry."""
        mock_func = Mock(return_value="success")

        @refib()
        def test_func():
            return mock_func()

        result = test_func()
        assert result == "success"
        assert mock_func.call_count == 1

    def test_retry_on_exception(self):
        """Test that function retries on exception."""
        mock_func = Mock(side_effect=[ValueError(), ValueError(), "success"])

        @refib(steps=3)
        def test_func():
            return mock_func()

        result = test_func()
        assert result == "success"
        assert mock_func.call_count == 3

    def test_specific_exception_retry(self):
        """Test retry only on specific exceptions."""
        mock_func = Mock(side_effect=[ValueError(), "success"])

        @refib(exceptions=ValueError, steps=3)
        def test_func():
            return mock_func()

        result = test_func()
        assert result == "success"
        assert mock_func.call_count == 2

    def test_no_retry_on_different_exception(self):
        """Test no retry on non-specified exceptions."""
        mock_func = Mock(side_effect=TypeError("wrong type"))

        @refib(exceptions=ValueError, steps=3)
        def test_func():
            return mock_func()

        with pytest.raises(TypeError):
            test_func()
        assert mock_func.call_count == 1

    def test_multiple_exception_types(self):
        """Test retry on multiple exception types."""
        mock_func = Mock(side_effect=[ValueError(), TypeError(), "success"])

        @refib(exceptions=(ValueError, TypeError), steps=3)
        def test_func():
            return mock_func()

        result = test_func()
        assert result == "success"
        assert mock_func.call_count == 3

    def test_max_retries_exceeded(self):
        """Test that exception is raised after max retries."""
        mock_func = Mock(side_effect=ValueError("persistent error"))

        @refib(steps=3)
        def test_func():
            return mock_func()

        with pytest.raises(ValueError, match="persistent error"):
            test_func()
        assert mock_func.call_count == 3

    def test_fibonacci_delay_sequence(self):
        """Test that delays follow Fibonacci sequence."""
        mock_func = Mock(
            side_effect=[ValueError(), ValueError(), ValueError(), "success"]
        )
        mock_sleep = Mock()

        @refib(steps=4, start=1)
        def test_func():
            return mock_func()

        # Patch time.sleep to track delays
        import refib.core as core_module

        original_sleep = core_module.time.sleep
        core_module.time.sleep = mock_sleep

        try:
            result = test_func()
            assert result == "success"
            assert mock_func.call_count == 4

            # Starting at F(1), then F(2), F(3)
            expected_delays = [1, 1, 2]
            actual_delays = [c[0][0] for c in mock_sleep.call_args_list]
            assert actual_delays == expected_delays
        finally:
            core_module.time.sleep = original_sleep

    def test_min_delay_constraint(self):
        """Test that delays respect minimum constraint."""
        mock_func = Mock(side_effect=[ValueError(), "success"])
        mock_sleep = Mock()

        @refib(steps=2, start=3)
        def test_func():
            return mock_func()

        import refib.core as core_module

        original_sleep = core_module.time.sleep
        core_module.time.sleep = mock_sleep

        try:
            test_func()
            # Starting at F(3) = 2 seconds
            assert mock_sleep.call_args[0][0] == 2
        finally:
            core_module.time.sleep = original_sleep

    def test_max_delay_constraint(self):
        """Test that delays respect maximum constraint."""
        mock_func = Mock(side_effect=[ValueError() for _ in range(10)] + ["success"])
        mock_sleep = Mock()

        @refib(steps=11, start=1)
        def test_func():
            return mock_func()

        import refib.core as core_module

        original_sleep = core_module.time.sleep
        core_module.time.sleep = mock_sleep

        try:
            test_func()
            # Check the Fibonacci progression
            actual_delays = [c[0][0] for c in mock_sleep.call_args_list]
            # Starting at F(1), should progress through Fibonacci sequence
            expected_first_few = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
            for i, expected in enumerate(expected_first_few):
                assert actual_delays[i] == expected
        finally:
            core_module.time.sleep = original_sleep

    def test_decorator_with_function_args(self):
        """Test decorator works with function arguments."""
        mock_func = Mock(side_effect=[ValueError(), "result"])

        @refib(steps=2)
        def test_func(arg1, arg2, kwarg1=None):
            return mock_func(arg1, arg2, kwarg1)

        result = test_func("a", "b", kwarg1="c")
        assert result == "result"
        assert mock_func.call_count == 2
        mock_func.assert_called_with("a", "b", "c")

    def test_decorator_preserves_function_metadata(self):
        """Test that decorator preserves function metadata."""

        @refib()
        def test_func():
            """Test function docstring."""
            pass

        assert test_func.__name__ == "test_func"
        assert test_func.__doc__ == "Test function docstring."

    def test_default_parameters(self):
        """Test decorator with default parameters."""
        mock_func = Mock(side_effect=[Exception(), Exception(), "success"])

        @refib()  # Using all defaults
        def test_func():
            return mock_func()

        result = test_func()
        assert result == "success"
        assert mock_func.call_count == 3


class TestIntegration:
    """Integration tests with real delays."""

    def test_real_delay_timing(self):
        """Test actual timing of retries (with reduced delays)."""
        call_times = []

        @refib(steps=3, start=1)
        def test_func():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ValueError()
            return "success"

        start_time = time.time()
        result = test_func()
        total_time = time.time() - start_time

        assert result == "success"
        assert len(call_times) == 3
        # Should have delays of F(1)=1 and F(2)=1
        assert 2.0 <= total_time <= 2.5  # Allow some overhead
