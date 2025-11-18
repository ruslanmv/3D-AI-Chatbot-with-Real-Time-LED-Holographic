"""
Pytest configuration and shared fixtures.

Author: Ruslan Magana
License: Apache 2.0
"""

import pytest


@pytest.fixture(scope="session")
def test_api_key() -> str:
    """Provide a test API key for all tests."""
    return "sk-test-key-1234567890abcdefghijklmnop"
