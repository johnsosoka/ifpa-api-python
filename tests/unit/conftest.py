"""Fixtures for unit tests."""

from collections.abc import Generator

import pytest
import requests_mock


@pytest.fixture  # type: ignore[misc]
def mock_requests() -> Generator[requests_mock.Mocker, None, None]:
    """Provide requests_mock fixture for mocking HTTP requests.

    Yields:
        requests_mock.Mocker instance for mocking requests library calls

    Example:
        ```python
        def test_something(mock_requests):
            mock_requests.get(
                "https://api.ifpapinball.com/player/123",
                json={"player_id": 123, "first_name": "John"}
            )
            # Make request through the mocked session
        ```
    """
    with requests_mock.Mocker() as m:
        yield m
