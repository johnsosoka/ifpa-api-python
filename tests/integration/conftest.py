"""Fixtures for integration tests."""

from collections.abc import Generator

import pytest

from ifpa_api import IfpaClient

# Import test data fixtures to make them available to all integration tests
from tests.integration.test_data import (  # noqa: F401
    count_large,
    count_medium,
    count_small,
    country_code,
    player_active_id,
    player_active_id_2,
    player_highly_active_id,
    player_ids_active,
    player_ids_multiple,
    player_inactive_id,
    pvp_pair_never_met,
    pvp_pair_primary,
    search_idaho_johns,
    search_idaho_smiths,
    tournament_id,
    year_end,
    year_start,
)


@pytest.fixture
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
            player = client.player(123456).details()
            assert player is not None
        ```
    """
    client_instance = IfpaClient(api_key=api_key)
    try:
        yield client_instance
    finally:
        client_instance.close()
