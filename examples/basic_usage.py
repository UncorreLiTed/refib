#!/usr/bin/env python
"""
Basic usage examples for refib.

This file demonstrates simple, common use cases that beginners can understand.
"""
from refib import refib
import random
import time


# Example 1: Simplest possible usage
@refib()
def download_file():
    """Downloads a file that might fail due to network issues."""
    print("Attempting to download file...")
    
    # Simulate a 70% failure rate
    if random.random() < 0.7:
        raise ConnectionError("Network timeout!")
    
    print("Download successful!")
    return "file_content.pd"


# Example 2: Retry only on specific errors
@refib(exceptions=ValueError)
def convert_to_number(user_input):
    """Converts user input to a number, retrying on ValueError."""
    print("Trying to convert '{}' to a number...".format(user_input))
    
    # Simulate occasional parsing issues
    if random.random() < 0.5:
        raise ValueError("Cannot parse '{}' right now".format(user_input))
    
    return int(user_input)


# Example 3: Limit retry attempts
@refib(steps=3)
def save_to_database(data):
    """Saves data to database with limited retries."""
    print("Attempting to save: {}".format(data))
    
    # Simulate database being temporarily unavailable
    if random.random() < 0.6:
        raise Exception("Database is locked")
    
    print("Data saved successfully!")
    return True


# Example 4: Real-world API call example
@refib(exceptions=(ConnectionError, TimeoutError), steps=5)
def call_weather_api(city):
    """Calls a weather API that might be flaky."""
    print("Fetching weather for {}...".format(city))
    
    # Simulate API issues
    error_chance = random.random()
    if error_chance < 0.3:
        raise ConnectionError("Cannot reach weather service")
    elif error_chance < 0.5:
        raise TimeoutError("Request timed out")
    
    # Simulate successful response
    return {
        "city": city,
        "temperature": random.randint(60, 85),
        "conditions": "Partly cloudy"
    }


def main():
    """Run all examples with clear output."""
    print("=" * 60)
    print("FIB-RETRY EXAMPLES")
    print("=" * 60)
    
    # Example 1: Basic usage
    print("\n1. BASIC USAGE - Downloading a file with automatic retries:")
    print("-" * 40)
    try:
        filename = download_file()
        print("✓ Got file: {}".format(filename))
    except ConnectionError:
        print("✗ Failed after all retries")
    
    # Example 2: Specific exception
    print("\n2. SPECIFIC EXCEPTION - Converting user input:")
    print("-" * 40)
    try:
        number = convert_to_number("42")
        print("✓ Converted to: {}".format(number))
    except ValueError:
        print("✗ Could not convert input")
    
    # Example 3: Limited retries
    print("\n3. LIMITED RETRIES - Saving to database (max 3 attempts):")
    print("-" * 40)
    try:
        saved = save_to_database({"user": "john", "score": 100})
        print("✓ Save status: {}".format(saved))
    except Exception:
        print("✗ Could not save after 3 attempts")
    
    # Example 4: Real-world scenario
    print("\n4. REAL-WORLD API - Getting weather data:")
    print("-" * 40)
    try:
        weather = call_weather_api("San Francisco")
        print("✓ Weather: {}°F, {}".format(weather['temperature'], weather['conditions']))
    except (ConnectionError, TimeoutError) as e:
        print("✗ API error: {}".format(type(e).__name__))
    
    print("\n" + "=" * 60)
    print("Notice how the retries happen automatically!")
    print("The delays between retries follow the Fibonacci sequence.")
    print("=" * 60)


if __name__ == "__main__":
    main()