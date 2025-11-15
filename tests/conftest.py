"""Shared pytest fixtures for all tests."""

import os
from collections.abc import Generator
from typing import Any

import pytest


def pytest_configure(config: Any) -> None:
    """Register custom markers for pytest."""
    config.addinivalue_line("markers", "integration: integration tests requiring API access")


@pytest.fixture
def api_key() -> Generator[str, None, None]:
    """Get API key from environment or credentials file.

    Resolution order:
    1. IFPA_API_KEY environment variable
    2. credentials file in current directory
    3. Skip test if neither is available

    Yields:
        The API key string

    Raises:
        pytest.skip: If no API key can be found
    """
    key = os.getenv("IFPA_API_KEY")
    if not key:
        try:
            with open("credentials") as f:
                for line in f:
                    if line.startswith("IFPA_API_KEY="):
                        key = line.split("=", 1)[1].strip()
                        break
        except FileNotFoundError:
            pass
    if not key:
        pytest.skip("IFPA_API_KEY not found")
    assert key is not None
    yield key
