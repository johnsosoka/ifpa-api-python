"""Shared test data fixtures for integration tests.

These fixtures provide known, stable IDs from the IFPA API that can be used
across multiple integration tests for consistency and maintainability.
"""

import pytest

# Known stable player IDs
TEST_PLAYER_ACTIVE_ID = 2643  # Mikael Englund (active player with history)
TEST_PLAYER_INACTIVE_ID = 50104  # Inactive player for edge case testing
TEST_PLAYER_IDS_MULTIPLE = [2643, 50104]  # For testing get_multiple()

# Known stable tournament ID
TEST_TOURNAMENT_ID = 7070  # PAPA 17 (2014) - well-known historical tournament

# Common test parameters
TEST_COUNTRY_CODE = "US"
TEST_COUNT_SMALL = 5
TEST_COUNT_MEDIUM = 10
TEST_COUNT_LARGE = 50

# Date ranges for testing
TEST_YEAR_START = 2020
TEST_YEAR_END = 2024


@pytest.fixture  # type: ignore[misc]
def player_active_id() -> int:
    """Known active player ID for testing.

    This fixture provides a stable ID for a player with extensive history
    and valid data, suitable for testing most player-related endpoints.

    Returns:
        Active player ID: 2643 (Mikael Englund)

    Example:
        ```python
        def test_get_active_player(client, player_active_id):
            player = client.player(player_active_id).get()
            assert player.player_id == player_active_id
        ```
    """
    return TEST_PLAYER_ACTIVE_ID


@pytest.fixture  # type: ignore[misc]
def player_inactive_id() -> int:
    """Known inactive player ID for testing.

    This fixture provides a stable ID for an inactive player, useful for
    testing edge cases and verifying handling of inactive accounts.

    Returns:
        Inactive player ID: 50104

    Example:
        ```python
        def test_handle_inactive_player(client, player_inactive_id):
            player = client.player(player_inactive_id).get()
            assert player is not None
        ```
    """
    return TEST_PLAYER_INACTIVE_ID


@pytest.fixture  # type: ignore[misc]
def player_ids_multiple() -> list[int]:
    """List of player IDs for testing get_multiple().

    This fixture provides multiple player IDs (both active and inactive)
    for testing batch operations and verifying correct handling of mixed
    player states.

    Returns:
        List of player IDs: [2643, 50104]

    Example:
        ```python
        def test_get_multiple_players(client, player_ids_multiple):
            result = client.players.get_multiple(player_ids_multiple)
            assert len(result.player) == len(player_ids_multiple)
        ```
    """
    return TEST_PLAYER_IDS_MULTIPLE


@pytest.fixture  # type: ignore[misc]
def tournament_id() -> int:
    """Known tournament ID for testing.

    This fixture provides a stable ID for a well-known historical tournament
    with reliable data and results.

    Returns:
        Tournament ID: 7070 (PAPA 17 - 2014)

    Example:
        ```python
        def test_tournament_results(client, tournament_id):
            results = client.tournament(tournament_id).results()
            assert results is not None
        ```
    """
    return TEST_TOURNAMENT_ID


@pytest.fixture  # type: ignore[misc]
def country_code() -> str:
    """Default country code for testing.

    This fixture provides a country code commonly used in test searches
    to filter results by location.

    Returns:
        Country code: "US"

    Example:
        ```python
        def test_search_us_players(client, country_code):
            result = client.players.search(country=country_code, count=5)
            assert result.search is not None
        ```
    """
    return TEST_COUNTRY_CODE


@pytest.fixture  # type: ignore[misc]
def count_small() -> int:
    """Small count value for testing.

    Useful for quick tests with minimal API response processing.

    Returns:
        Count value: 5

    Example:
        ```python
        def test_search_small(client, count_small):
            result = client.players.search(country="US", count=count_small)
            assert len(result.search) <= count_small
        ```
    """
    return TEST_COUNT_SMALL


@pytest.fixture  # type: ignore[misc]
def count_medium() -> int:
    """Medium count value for testing.

    Useful for testing pagination and larger result sets.

    Returns:
        Count value: 10

    Example:
        ```python
        def test_search_medium(client, count_medium):
            result = client.players.search(country="US", count=count_medium)
            assert len(result.search) <= count_medium
        ```
    """
    return TEST_COUNT_MEDIUM


@pytest.fixture  # type: ignore[misc]
def count_large() -> int:
    """Large count value for testing.

    Useful for testing substantial result sets and performance.

    Returns:
        Count value: 50

    Example:
        ```python
        def test_search_large(client, count_large):
            result = client.players.search(country="US", count=count_large)
            assert len(result.search) <= count_large
        ```
    """
    return TEST_COUNT_LARGE


@pytest.fixture  # type: ignore[misc]
def year_start() -> int:
    """Start year for date range testing.

    Returns:
        Year: 2020

    Example:
        ```python
        def test_year_range(client, year_start, year_end):
            # Test filtering by year range
            pass
        ```
    """
    return TEST_YEAR_START


@pytest.fixture  # type: ignore[misc]
def year_end() -> int:
    """End year for date range testing.

    Returns:
        Year: 2024

    Example:
        ```python
        def test_year_range(client, year_start, year_end):
            # Test filtering by year range
            pass
        ```
    """
    return TEST_YEAR_END
