"""Test helper utilities for IFPA SDK tests.

This module provides common test data builders and response factories
used across unit and integration tests.
"""

from typing import Any


def mock_api_response(data: dict[str, Any], status_code: int = 200) -> dict[str, Any]:
    """Create a mock API response.

    This is a simple wrapper that can be extended to include response metadata
    or status information if needed in tests.

    Args:
        data: The response data dictionary
        status_code: HTTP status code (included for documentation purposes)

    Returns:
        The data dictionary as-is (for use with requests_mock)
    """
    return data


def get_sample_director() -> dict[str, Any]:
    """Get sample director data for tests.

    Returns a realistic director object matching IFPA API response format.

    Returns:
        Dictionary containing sample director data
    """
    return {
        "director_id": 1234,
        "first_name": "John",
        "last_name": "Doe",
        "city": "Seattle",
        "state": "WA",
        "country": "USA",
        "tournaments_directed": 10,
    }


def get_sample_player() -> dict[str, Any]:
    """Get sample player data for tests.

    Returns a realistic player object matching IFPA API response format.

    Returns:
        Dictionary containing sample player data
    """
    return {
        "player_id": 5678,
        "first_name": "Jane",
        "last_name": "Smith",
        "city": "Portland",
        "state": "OR",
        "country": "USA",
        "current_wppr_rank": 100,
        "current_wppr_value": 50.25,
    }
