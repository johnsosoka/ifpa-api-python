"""IFPA SDK - Python client for the International Flipper Pinball Association API.

This package provides a typed, modern Python interface to the IFPA API,
enabling easy access to player rankings, tournament data, statistics, and more.

Example:
    ```python
    from ifpa_api import IfpaClient, TimePeriod, RankingSystem, ResultType

    # Initialize client (uses IFPA_API_KEY environment variable)
    client = IfpaClient()

    # Get player information
    player = client.player(12345).details()
    print(f"{player.first_name} {player.last_name}")

    # Get rankings
    rankings = client.rankings.wppr(start_pos=0, count=100)
    for entry in rankings.rankings:
        print(f"{entry.rank}. {entry.player_name}: {entry.rating}")

    # Get tournament results
    results = client.player(12345).results(
        ranking_system=RankingSystem.MAIN,
        result_type=ResultType.ACTIVE
    )

    # Search for directors
    directors = client.director.query("Josh").get()

    # Get director's tournaments
    tournaments = client.director(1000).tournaments(TimePeriod.PAST)
    ```
"""

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

__version__ = "0.3.0"

__all__ = [
    # Main client
    "IfpaClient",
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
