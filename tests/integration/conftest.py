"""Fixtures for integration tests."""

import pytest

from ifpa_sdk import IfpaClient


@pytest.fixture
def client(api_key: str) -> IfpaClient:
    """Create a real IfpaClient for integration tests.

    This fixture requires IFPA_API_KEY to be set. If not available,
    tests using this fixture will be skipped.

    Args:
        api_key: The IFPA API key from the api_key fixture

    Returns:
        An initialized IfpaClient instance

    Example:
        ```python
        @pytest.mark.integration
        def test_get_player(client):
            player = client.player(123456).get()
            assert player is not None
        ```
    """
    return IfpaClient(api_key=api_key)
