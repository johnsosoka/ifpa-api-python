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
