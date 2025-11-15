"""Integration test helpers.

Helper functions for integration tests that make real API calls.
"""

import os

import pytest

from ifpa_sdk.client import IfpaClient


def skip_if_no_api_key() -> None:
    """Skip test if IFPA_API_KEY is not available.

    This decorator checks for the API key in environment variable or
    credentials file. If not found, the test is skipped.

    Example:
        ```python
        @pytest.mark.integration
        def test_something():
            skip_if_no_api_key()
            # Test code here
        ```
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
        pytest.skip("IFPA_API_KEY not available for integration tests")


def get_test_director_id(client: IfpaClient) -> int | None:
    """Find a director ID for testing.

    Uses search to find an active director with tournaments.

    Args:
        client: Initialized IfpaClient instance

    Returns:
        Director ID if found, None otherwise

    Example:
        ```python
        client = IfpaClient()
        director_id = get_test_director_id(client)
        if director_id:
            director = client.director(director_id).get()
        ```
    """
    try:
        # Search for directors, get first result
        results = client.directors.search()
        if results.directors and len(results.directors) > 0:
            return results.directors[0].director_id
    except Exception:
        pass
    return None


def get_test_player_id(client: IfpaClient) -> int | None:
    """Find a player ID for testing.

    Uses rankings to find a top-ranked player.

    Args:
        client: Initialized IfpaClient instance

    Returns:
        Player ID if found, None otherwise

    Example:
        ```python
        client = IfpaClient()
        player_id = get_test_player_id(client)
        if player_id:
            player = client.player(player_id).get()
        ```
    """
    try:
        # Get top WPPR rankings, use first player
        rankings = client.rankings.wppr(start_pos=0, count=1)
        if rankings.rankings and len(rankings.rankings) > 0:
            return rankings.rankings[0].player_id
    except Exception:
        pass
    return None


def get_test_tournament_id(client: IfpaClient) -> int | None:
    """Find a tournament ID for testing.

    Uses search to find a recent tournament.

    Args:
        client: Initialized IfpaClient instance

    Returns:
        Tournament ID if found, None otherwise

    Example:
        ```python
        client = IfpaClient()
        tournament_id = get_test_tournament_id(client)
        if tournament_id:
            tournament = client.tournament(tournament_id).get()
        ```
    """
    try:
        # Search for tournaments, get first result
        results = client.tournaments.search(count=1)
        if results.tournaments and len(results.tournaments) > 0:
            return results.tournaments[0].tournament_id
    except Exception:
        pass
    return None


def get_test_series_code(client: IfpaClient) -> str | None:
    """Find a series code for testing.

    Uses series list to find an active series.

    Args:
        client: Initialized IfpaClient instance

    Returns:
        Series code if found, None otherwise

    Example:
        ```python
        client = IfpaClient()
        series_code = get_test_series_code(client)
        if series_code:
            standings = client.series_handle(series_code).standings()
        ```
    """
    try:
        # List series, prefer active ones
        series_list = client.series.list(active_only=True)
        if series_list.series and len(series_list.series) > 0:
            return series_list.series[0].series_code
    except Exception:
        pass
    return None
