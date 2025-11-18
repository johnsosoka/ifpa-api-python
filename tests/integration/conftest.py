"""Fixtures for integration tests."""

from collections.abc import Generator

import pytest

from ifpa_api import IfpaClient
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.models.director import Director
from ifpa_api.models.player import Player
from ifpa_api.models.tournaments import Tournament

# Import test data fixtures to make them available to all integration tests
from tests.integration.test_data import (  # noqa: F401
    count_large,
    count_medium,
    count_small,
    country_code,
    director_active_id,
    director_highly_active_id,
    director_international_id,
    director_low_activity_id,
    director_zero_future_id,
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


def assert_field_present(obj: object, field_name: str, expected_type: type) -> None:
    """Assert that a field exists, is not None, and has the expected type.

    This helper is used for resilient integration testing where we validate
    field presence and type rather than exact values that may change.

    Args:
        obj: Object to check
        field_name: Name of the field to validate
        expected_type: Expected Python type

    Raises:
        AssertionError: If field is missing, None, or wrong type
    """
    assert hasattr(obj, field_name), f"Object missing field: {field_name}"
    value = getattr(obj, field_name)
    assert value is not None, f"Field {field_name} is None"
    assert isinstance(
        value, expected_type
    ), f"Field {field_name} has wrong type. Expected {expected_type}, got {type(value)}"


def assert_numeric_field_valid(value: float | int | None, min_threshold: float = 0.0) -> None:
    """Assert that a numeric field has a reasonable value if present.

    Args:
        value: Numeric value to check (can be None for optional fields)
        min_threshold: Minimum acceptable value (default 0.0)

    Raises:
        AssertionError: If value is present but invalid
    """
    if value is not None:
        assert isinstance(value, float | int), f"Expected numeric type, got {type(value)}"
        assert value >= min_threshold, f"Value {value} below threshold {min_threshold}"


def assert_collection_not_empty(collection: object) -> None:
    """Assert that a collection has at least one item.

    Args:
        collection: List, tuple, or other collection

    Raises:
        AssertionError: If collection is None or empty
    """
    assert collection is not None, "Collection is None"
    assert len(collection) > 0, "Collection is empty"  # type: ignore[arg-type]


def validate_test_player(client: IfpaClient, player_id: int) -> Player:
    """Validate that a test player exists in the API.

    This helper function checks if a player ID is still valid in the IFPA database.
    If the player doesn't exist (404 error), the test will be skipped with a helpful
    message rather than failing unexpectedly.

    Args:
        client: IFPA API client
        player_id: Player ID to validate

    Returns:
        Player object if player exists

    Raises:
        pytest.skip: If player doesn't exist or is inaccessible (404 error)

    Example:
        ```python
        def test_player_feature(client):
            player = validate_test_player(client, 25584)
            # Continue with test knowing player exists
            assert player.player_id == 25584
        ```
    """
    try:
        return client.player(player_id).details()
    except IfpaApiError as e:
        if e.status_code == 404:
            pytest.skip(
                f"Test player {player_id} not found in IFPA database. "
                "This test requires a valid player ID to run."
            )
        # Re-raise unexpected errors
        raise


def validate_test_director(client: IfpaClient, director_id: int) -> Director:
    """Validate that a test director exists in the API.

    This helper function checks if a director ID is still valid in the IFPA database.
    If the director doesn't exist (404 error), the test will be skipped with a helpful
    message rather than failing unexpectedly.

    Args:
        client: IFPA API client
        director_id: Director ID to validate

    Returns:
        Director object if director exists

    Raises:
        pytest.skip: If director doesn't exist or is inaccessible (404 error)

    Example:
        ```python
        def test_director_feature(client):
            director = validate_test_director(client, 1533)
            # Continue with test knowing director exists
            assert director.director_id == 1533
        ```
    """
    try:
        return client.director(director_id).details()
    except IfpaApiError as e:
        if e.status_code == 404:
            pytest.skip(
                f"Test director {director_id} not found in IFPA database. "
                "This test requires a valid director ID to run."
            )
        # Re-raise unexpected errors
        raise


def validate_test_tournament(client: IfpaClient, tournament_id_param: int) -> Tournament:
    """Validate that a test tournament exists in the API.

    This helper function checks if a tournament ID is still valid in the IFPA database.
    If the tournament doesn't exist (404 error), the test will be skipped with a helpful
    message rather than failing unexpectedly.

    Args:
        client: IFPA API client
        tournament_id_param: Tournament ID to validate

    Returns:
        Tournament object if tournament exists

    Raises:
        pytest.skip: If tournament doesn't exist or is inaccessible (404 error)

    Example:
        ```python
        def test_tournament_feature(client):
            tournament = validate_test_tournament(client, 12345)
            # Continue with test knowing tournament exists
            assert tournament.tournament_id == 12345
        ```
    """
    try:
        return client.tournament(tournament_id_param).details()
    except IfpaApiError as e:
        if e.status_code == 404:
            pytest.skip(
                f"Test tournament {tournament_id_param} not found in IFPA database. "
                "This test requires a valid tournament ID to run."
            )
        # Re-raise unexpected errors
        raise
