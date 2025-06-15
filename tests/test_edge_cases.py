"""
Edge case tests for refib decorator.
"""

import pytest
import time
from unittest.mock import Mock, patch
from refib import refib
from refib.core import _fibonacci


class TestEdgeCases:
    """Test edge cases and error scenarios."""

    def test_zero_max_steps(self):
        """Test with steps=0 (should not retry at all)."""
        mock_func = Mock(side_effect=ValueError("error"))

        # This should raise an error since max_steps must be positive
        with pytest.raises(ValueError):

            @refib(steps=0)
            def test_func():
                return mock_func()

    def test_negative_steps(self):
        """Test with negative steps."""
        with pytest.raises(ValueError):

            @refib(steps=-1)
            def test_func():
                pass

    def test_negative_start(self):
        """Test with negative start value."""
        with pytest.raises(ValueError):

            @refib(start=-1)
            def test_func():
                pass

    def test_zero_start(self):
        """Test with start=0 (invalid Fibonacci position)."""
        with pytest.raises(ValueError):

            @refib(start=0)
            def test_func():
                pass

    def test_single_exception_as_tuple(self):
        """Test passing single exception in a tuple."""
        mock_func = Mock(side_effect=[ValueError(), "success"])

        @refib(exceptions=(ValueError,), steps=2)
        def test_func():
            return mock_func()

        result = test_func()
        assert result == "success"
        assert mock_func.call_count == 2

    def test_empty_exception_tuple(self):
        """Test with empty exception tuple (should catch nothing)."""
        mock_func = Mock(side_effect=ValueError("error"))

        @refib(exceptions=(), steps=3)
        def test_func():
            return mock_func()

        # Should not retry since no exceptions are specified
        with pytest.raises(ValueError):
            test_func()
        assert mock_func.call_count == 1

    def test_non_exception_type(self):
        """Test with non-exception type in exceptions parameter."""
        with pytest.raises(TypeError):

            @refib(exceptions=str)  # str is not an exception
            def test_func():
                pass

    def test_non_exception_type_in_tuple(self):
        """Test with non-exception type in exceptions tuple."""
        with pytest.raises(TypeError, match="All exception types must be subclasses"):

            @refib(exceptions=(ValueError, str))  # str is not an exception
            def test_func():
                pass

    def test_very_large_fibonacci_numbers(self):
        """Test behavior with many retries (large Fibonacci numbers)."""
        mock_func = Mock(side_effect=[ValueError() for _ in range(19)] + ["success"])
        mock_sleep = Mock()

        @refib(steps=20, start=1)
        def test_func():
            return mock_func()

        import refib.core as core_module

        original_sleep = core_module.time.sleep
        core_module.time.sleep = mock_sleep

        try:
            result = test_func()
            assert result == "success"
            assert mock_func.call_count == 20

            # Check delays follow Fibonacci sequence starting from F(1)
            delays = [call[0][0] for call in mock_sleep.call_args_list]
            assert delays[0] == 1  # F(1)
            assert delays[1] == 1  # F(2)
            assert delays[2] == 2  # F(3)
            assert delays[3] == 3  # F(4)
            assert delays[4] == 5  # F(5)
            # Check some larger values
            assert delays[10] == 89  # F(11)
            assert delays[11] == 144  # F(12)
        finally:
            core_module.time.sleep = original_sleep

    def test_function_with_no_arguments(self):
        """Test decorating function with no arguments."""
        call_count = 0

        @refib(steps=3)
        def no_args():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError()
            return "success"

        result = no_args()
        assert result == "success"
        assert call_count == 3

    def test_function_with_only_kwargs(self):
        """Test function with only keyword arguments."""
        mock_func = Mock(side_effect=[ValueError(), "result"])

        @refib(steps=2)
        def kwargs_only(**kwargs):
            return mock_func(**kwargs)

        result = kwargs_only(a=1, b=2, c=3)
        assert result == "result"
        mock_func.assert_called_with(a=1, b=2, c=3)

    def test_async_not_supported(self):
        """Test that async functions are not supported (yet)."""

        # This documents current behavior - async support could be added later
        async def async_func():
            return "async result"

        # Should work but won't retry async exceptions properly
        decorated = refib()(async_func)
        assert decorated.__name__ == "async_func"

    def test_class_method(self):
        """Test decorating a class method."""

        class MyClass:
            def __init__(self):
                self.attempts = 0

            @refib(steps=3)
            def method(self):
                self.attempts += 1
                if self.attempts < 2:
                    raise ValueError()
                return "success"

        obj = MyClass()
        result = obj.method()
        assert result == "success"
        assert obj.attempts == 2

    def test_static_method(self):
        """Test decorating a static method."""

        class MyClass:
            call_count = 0

            @staticmethod
            @refib(steps=2)
            def static_method():
                MyClass.call_count += 1
                if MyClass.call_count < 2:
                    raise ValueError()
                return "static success"

        result = MyClass.static_method()
        assert result == "static success"
        assert MyClass.call_count == 2

    def test_exception_in_delay_calculation(self):
        """Test handling of exceptions during delay calculation."""
        # This is more of a defensive test - our implementation shouldn't fail
        mock_func = Mock(side_effect=[ValueError(), ValueError(), "success"])

        # Test with high Fibonacci positions
        @refib(steps=3, start=10)
        def test_func():
            return mock_func()

        # Should handle large values gracefully
        with patch("time.sleep") as mock_sleep:
            result = test_func()
            assert result == "success"
            # F(10)=55, F(11)=89
            delays = [call[0][0] for call in mock_sleep.call_args_list]
            assert delays[0] == 55  # F(10)
            assert delays[1] == 89  # F(11)

    def test_default_start_position(self):
        """Test with default start position."""
        mock_func = Mock(side_effect=[ValueError(), "success"])

        @refib(steps=2)
        def test_func():
            return mock_func()

        start = time.time()
        result = test_func()
        duration = time.time() - start

        assert result == "success"
        # Default start=5, so F(5) = 5 seconds delay
        assert 5.0 <= duration <= 5.5  # Allow some overhead

    def test_fibonacci_invalid_position(self):
        """Test _fibonacci function with invalid input."""
        with pytest.raises(ValueError, match="Fibonacci position must be positive"):
            _fibonacci(0)

        with pytest.raises(ValueError, match="Fibonacci position must be positive"):
            _fibonacci(-1)

    def test_fibonacci_large_values(self):
        """Test _fibonacci function for large positions."""
        # Test some known Fibonacci values
        assert _fibonacci(10) == 55
        assert _fibonacci(15) == 610
        assert _fibonacci(20) == 6765
        # Test beyond cache (n > 30)
        assert _fibonacci(31) == 1346269  # F(31) = F(30) + F(29)
        assert _fibonacci(32) == 2178309  # F(32) = F(31) + F(30)
