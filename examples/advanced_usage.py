#!/usr/bin/env python
"""
Advanced usage examples for refib.

This file demonstrates more sophisticated patterns and configurations.
"""
from refib import refib
import random
import time
import logging

# Set up logging to see retry behavior
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# Example 1: Custom delay configuration
@refib(start=3, steps=5)  # Start at F(3)=2s, retry 5 times
def slow_external_service():
    """Simulates calling a slow external service with custom delays."""
    logger.info("Calling external service...")
    
    if random.random() < 0.7:
        raise ConnectionError("Service temporarily unavailable")
    
    return {"status": "success", "data": [1, 2, 3, 4, 5]}


# Example 2: Multiple exception types with different handling
class AuthenticationError(Exception):
    """Custom authentication error."""
    pass


class RateLimitError(Exception):
    """API rate limit exceeded."""
    pass


@refib(exceptions=(RateLimitError, ConnectionError), steps=8)
def api_request(endpoint, token):
    """
    Makes an API request that might fail for various reasons.
    Only retries on rate limits and connection errors.
    """
    logger.info("Requesting {}".format(endpoint))
    
    error_type = random.choice([
        None, None,  # 40% success
        RateLimitError,  # 20% rate limit
        ConnectionError,  # 20% connection error
        AuthenticationError  # 20% auth error (won't retry)
    ])
    
    if error_type:
        raise error_type("{} occurred".format(error_type.__name__))
    
    return {"endpoint": endpoint, "result": "data retrieved"}


# Example 3: Database transaction with retries
@refib(exceptions=(Exception,), start=1, steps=5)  # Start at F(1)=1s
def execute_transaction(operations):
    """
    Executes a database transaction that might fail due to locks.
    """
    logger.info("Executing {} operations".format(len(operations)))
    
    # Simulate lock contention
    if random.random() < 0.6:
        raise Exception("Transaction failed: table locked")
    
    # Simulate successful transaction
    results = []
    for op in operations:
        results.append("Executed: {}".format(op))
    
    return results


# Example 4: Combining with other decorators
def log_calls(func):
    """Simple logging decorator."""
    def wrapper(*args, **kwargs):
        logger.info("Calling {}".format(func.__name__))
        result = func(*args, **kwargs)
        logger.info("{} completed".format(func.__name__))
        return result
    return wrapper


@log_calls
@refib(start=1, steps=4)  # Start at F(1)=1s, retry 4 times
def process_batch(batch_id):
    """Process a batch with both logging and retry."""
    logger.info("Processing batch {}".format(batch_id))
    
    if random.random() < 0.5:
        raise RuntimeError("Batch {} processing failed".format(batch_id))
    
    return "Batch {} processed successfully".format(batch_id)


# Example 5: Context-aware retries
class DataProcessor:
    def __init__(self):
        self.retry_count = 0
    
    @refib(exceptions=ValueError, steps=6)
    def process_data(self, data):
        """Process data with retry, tracking attempt count."""
        self.retry_count += 1
        logger.info("Processing attempt #{}".format(self.retry_count))
        
        # Fail first few attempts
        if self.retry_count < 3:
            raise ValueError("Data validation failed")
        
        return "Processed: {}".format(data)


def main():
    """Demonstrate advanced usage patterns."""
    print("=" * 70)
    print("ADVANCED FIB-RETRY EXAMPLES")
    print("=" * 70)
    
    # Example 1: Custom delays
    print("\n1. CUSTOM DELAYS (starts at F(3)=2 seconds):")
    print("-" * 50)
    try:
        result = slow_external_service()
        print("✓ Service response: {}".format(result))
    except ConnectionError:
        print("✗ Service unavailable after all retries")
    
    # Example 2: Selective retry on exceptions
    print("\n2. SELECTIVE EXCEPTION RETRY:")
    print("-" * 50)
    print("Note: Only retries on RateLimitError and ConnectionError")
    
    for attempt in range(3):
        try:
            result = api_request("/users", "token123")
            print("✓ API response: {}".format(result))
            break
        except AuthenticationError:
            print("✗ Authentication failed (no retry)")
            break
        except (RateLimitError, ConnectionError) as e:
            print("✗ {} (will retry if attempts remain)".format(type(e).__name__))
    
    # Example 3: Database transaction
    print("\n3. DATABASE TRANSACTION:")
    print("-" * 50)
    operations = ["INSERT user", "UPDATE profile", "INSERT log"]
    try:
        results = execute_transaction(operations)
        print("✓ Transaction complete: {} operations".format(len(results)))
    except Exception as e:
        print("✗ Transaction failed: {}".format(e))
    
    # Example 4: Decorator stacking
    print("\n4. DECORATOR STACKING:")
    print("-" * 50)
    try:
        result = process_batch("BATCH-001")
        print("✓ {}".format(result))
    except RuntimeError:
        print("✗ Batch processing failed")
    
    # Example 5: Stateful retries
    print("\n5. STATEFUL RETRY:")
    print("-" * 50)
    processor = DataProcessor()
    try:
        result = processor.process_data("important_data.csv")
        print("✓ {} after {} attempts".format(result, processor.retry_count))
    except ValueError:
        print("✗ Processing failed after {} attempts".format(processor.retry_count))
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()