"""Resource clients for IFPA API endpoints.

This package contains resource-specific clients and handles for interacting
with different parts of the IFPA API.
"""

from ifpa_sdk.resources.directors import DirectorHandle, DirectorsClient
from ifpa_sdk.resources.players import PlayerHandle, PlayersClient
from ifpa_sdk.resources.rankings import RankingsClient
from ifpa_sdk.resources.series import SeriesClient, SeriesHandle
from ifpa_sdk.resources.stats import StatsClient
from ifpa_sdk.resources.tournaments import TournamentHandle, TournamentsClient

__all__ = [
    "DirectorHandle",
    "DirectorsClient",
    "PlayerHandle",
    "PlayersClient",
    "RankingsClient",
    "TournamentHandle",
    "TournamentsClient",
    "SeriesHandle",
    "SeriesClient",
    "StatsClient",
]
