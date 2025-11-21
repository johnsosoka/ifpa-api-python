"""IFPA SDK - Python client for the International Flipper Pinball Association API.

This package provides a typed, modern Python interface to the IFPA API,
enabling easy access to player rankings, tournament data, statistics, and more.

Example:
    ```python
    from ifpa_api import IfpaClient, TimePeriod, RankingSystem, ResultType

    # Initialize client (uses IFPA_API_KEY environment variable)
    client = IfpaClient()

    # Get player information (preferred method)
    player = client.player.get(12345)
    print(f"{player.first_name} {player.last_name}")

    # Get rankings
    rankings = client.rankings.wppr(start_pos=0, count=100)
    for entry in rankings.rankings:
        print(f"{entry.rank}. {entry.player_name}: {entry.rating}")

    # Get tournament results
    results = client.player.get_results(
        12345,
        ranking_system=RankingSystem.MAIN,
        result_type=ResultType.ACTIVE
    )

    # Search for directors (preferred method)
    directors = client.director.search("Josh").get()

    # Get director's tournaments
    tournaments = client.director.get_tournaments(1000, TimePeriod.PAST)
    ```
"""

from ifpa_api.async_client import AsyncIfpaClient
from ifpa_api.client import IfpaClient
from ifpa_api.core.exceptions import (
    IfpaApiError,
    IfpaClientValidationError,
    IfpaError,
    MissingApiKeyError,
    PlayersNeverMetError,
    SeriesPlayerNotFoundError,
    TournamentNotLeagueError,
)
from ifpa_api.models.common import RankingSystem, ResultType, TimePeriod, TournamentType

__version__ = "0.4.0"

__all__ = [
    # Main clients
    "IfpaClient",
    "AsyncIfpaClient",
    # Enums
    "TimePeriod",
    "RankingSystem",
    "ResultType",
    "TournamentType",
    # Exceptions
    "IfpaError",
    "IfpaApiError",
    "MissingApiKeyError",
    "IfpaClientValidationError",
    "PlayersNeverMetError",
    "SeriesPlayerNotFoundError",
    "TournamentNotLeagueError",
]
