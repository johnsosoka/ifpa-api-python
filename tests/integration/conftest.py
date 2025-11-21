"""Fixtures for integration tests."""

from collections.abc import AsyncGenerator, Generator
from datetime import datetime, timedelta
from typing import Any

import pytest

from ifpa_api import IfpaClient
from ifpa_api.async_client import AsyncIfpaClient
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
    series_active_code,
    series_player_id,
    series_region_code,
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


@pytest.fixture
async def async_ifpa_client(api_key: str) -> AsyncGenerator[AsyncIfpaClient, None]:
    """Create a real AsyncIfpaClient for async integration tests.

    This fixture requires IFPA_API_KEY to be set. If not available,
    tests using this fixture will be skipped.

    Args:
        api_key: The IFPA API key from the api_key fixture

    Yields:
        An initialized AsyncIfpaClient instance

    Example:
        ```python
        @pytest.mark.asyncio
        @pytest.mark.integration
        async def test_get_player(async_ifpa_client):
            async with async_ifpa_client as client:
                player = await client.player.get(123456)
                assert player is not None
        ```
    """
    client_instance = AsyncIfpaClient(api_key=api_key)
    try:
        yield client_instance
    finally:
        await client_instance.close()


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
    assert len(collection) > 0, "Collection is empty"


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


# === STATS-SPECIFIC HELPERS ===


def assert_stats_fields_types(obj: object, field_types: dict[str, type]) -> None:
    """Assert multiple stats fields have correct types.

    Helper function to reduce boilerplate when validating many fields at once.
    This is particularly useful for stats endpoints that return objects with
    10+ fields that need type validation.

    Args:
        obj: Object to validate
        field_types: Dictionary mapping field names to expected types

    Raises:
        AssertionError: If any field is missing, None, or wrong type

    Example:
        ```python
        assert_stats_fields_types(stats, {
            "overall_player_count": int,
            "active_player_count": int,
            "tournament_count": int,
            "wppr_value": float,
        })
        ```
    """
    for field_name, expected_type in field_types.items():
        assert_field_present(obj, field_name, expected_type)


def assert_stats_ranking_list(rankings: list[Any], min_count: int = 1) -> None:
    """Assert that a stats ranking list is valid.

    Validates:
    - List is not empty (unless min_count=0)
    - List has at least min_count items
    - All items have a stats_rank field
    - Ranks are in ascending order (1, 2, 3...)

    Args:
        rankings: List of ranking objects to validate
        min_count: Minimum expected number of items (default 1)

    Raises:
        AssertionError: If list is invalid or ranks are out of order

    Example:
        ```python
        result = client.stats.country_players()
        assert_stats_ranking_list(result.stats, min_count=10)
        ```
    """
    assert isinstance(rankings, list), f"Expected list, got {type(rankings)}"
    assert (
        len(rankings) >= min_count
    ), f"Expected at least {min_count} rankings, got {len(rankings)}"

    if len(rankings) > 0:
        # Validate first item has stats_rank field
        first_item = rankings[0]
        assert hasattr(first_item, "stats_rank"), "Ranking item missing 'stats_rank' field"

        # Validate ranks are sequential
        for i, item in enumerate(rankings, start=1):
            expected_rank = i
            actual_rank = int(item.stats_rank)
            assert actual_rank == expected_rank, (
                f"Rank out of order at position {i}: "
                f"expected {expected_rank}, got {actual_rank}"
            )


def assert_numeric_in_range(
    value: int | float, min_val: int | float, max_val: int | float, field_name: str = "value"
) -> None:
    """Assert that a numeric value is within an expected range.

    Args:
        value: Value to check
        min_val: Minimum acceptable value (inclusive)
        max_val: Maximum acceptable value (inclusive)
        field_name: Name of the field for error messages

    Raises:
        AssertionError: If value is outside range

    Example:
        ```python
        assert_numeric_in_range(stats.overall_player_count, 100000, 200000, "overall_player_count")
        ```
    """
    assert min_val <= value <= max_val, (
        f"{field_name} out of expected range: {value} " f"(expected {min_val}-{max_val})"
    )


# === STATS FIXTURES ===


@pytest.fixture
def stats_date_range_90_days() -> tuple[str, str]:
    """Date range for last 90 days (period-based stats queries).

    Returns:
        Tuple of (start_date, end_date) in YYYY-MM-DD format

    Use this for testing period-based endpoints like points_given_period
    and events_attended_period. 90 days provides good balance of recent
    data without being too restrictive.

    Example:
        ```python
        def test_points_period(client, stats_date_range_90_days):
            start, end = stats_date_range_90_days
            result = client.stats.points_given_period(start, end)
            assert result is not None
        ```
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    return (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))


@pytest.fixture
def stats_date_range_180_days() -> tuple[str, str]:
    """Date range for last 180 days (extended period stats queries).

    Returns:
        Tuple of (start_date, end_date) in YYYY-MM-DD format

    Use this for testing period queries that may have sparse data or when
    you need more results. 180 days captures seasonal patterns.

    Example:
        ```python
        def test_events_attended_longer_period(client, stats_date_range_180_days):
            start, end = stats_date_range_180_days
            result = client.stats.events_attended_period(start, end)
            assert len(result.rankings) > 0
        ```
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    return (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))


@pytest.fixture
def stats_date_range_last_year() -> tuple[str, str]:
    """Date range for last full year (annual stats queries).

    Returns:
        Tuple of (start_date, end_date) in YYYY-MM-DD format

    Use this for testing with a full year of data, useful for annual
    trends and comparing across seasons.

    Example:
        ```python
        def test_annual_activity(client, stats_date_range_last_year):
            start, end = stats_date_range_last_year
            result = client.stats.points_given_period(start, end)
            assert len(result.rankings) >= 100
        ```
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    return (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))


@pytest.fixture
def stats_thresholds() -> dict[str, int]:
    """Expected minimum thresholds for IFPA overall statistics.

    Returns:
        Dictionary of statistic names to minimum expected values

    These thresholds are based on IFPA's size as of 2025 (100,000+ players,
    2,000+ tournaments per year). If tests fail due to threshold violations,
    it may indicate either API changes or these thresholds need updating.

    Example:
        ```python
        def test_overall_stats_reasonable(client, stats_thresholds):
            stats = client.stats.overall()
            assert stats.overall_player_count >= stats_thresholds["overall_player_count"]
            assert stats.tournament_count >= stats_thresholds["tournament_count"]
        ```
    """
    return {
        "overall_player_count": 100000,  # 100k+ registered players
        "active_player_count": 20000,  # 20k+ active in last 2 years
        "tournament_count": 20000,  # 20k+ total tournaments
        "tournament_count_this_year": 500,  # 500+ tournaments this year
        "tournament_count_last_month": 50,  # 50+ tournaments last month
    }


@pytest.fixture
def stats_rank_types() -> list[str]:
    """List of rank types for parameterized testing.

    Returns:
        List ["OPEN", "WOMEN"] - the two primary IFPA ranking systems

    Use this for parameterized tests that need to run against both
    ranking systems.

    Note: "WOMEN" system has a known API bug in overall() endpoint
    where system_code is always "OPEN" regardless of parameter.

    Example:
        ```python
        @pytest.mark.parametrize("rank_type", ["OPEN", "WOMEN"])
        def test_country_players(client, rank_type):
            result = client.stats.country_players(rank_type=rank_type)
            assert result.rank_type == rank_type
        ```
    """
    return ["OPEN", "WOMEN"]
