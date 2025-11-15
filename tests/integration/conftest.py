"""Fixtures for integration tests."""

from collections.abc import Generator

import pytest

from ifpa_sdk import IfpaClient


@pytest.fixture  # type: ignore[misc]
def client(api_key: str) -> Generator[IfpaClient, None, None]:
    """Create a real IfpaClient for integration tests.

    This fixture requires IFPA_API_KEY to be set. If not available,
    tests using this fixture will be skipped.

    Args:
        api_key: The IFPA API key from the api_key fixture

    Yields:
        An initialized IfpaClient instance

    Example:
        ```python
        @pytest.mark.integration
        def test_get_player(client):
            player = client.player(123456).get()
            assert player is not None
        ```
    """
    client_instance = IfpaClient(api_key=api_key)
    try:
        yield client_instance
    finally:
        client_instance.close()
