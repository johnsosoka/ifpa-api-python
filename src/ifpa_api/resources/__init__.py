"""Resource clients for IFPA API endpoints.

This package contains resource-specific clients and handles for interacting
with different parts of the IFPA API.
"""

from ifpa_api.resources.directors import DirectorHandle, DirectorsClient
from ifpa_api.resources.players import PlayerHandle, PlayersClient
from ifpa_api.resources.rankings import RankingsClient
from ifpa_api.resources.series import SeriesClient, SeriesHandle
from ifpa_api.resources.tournaments import TournamentHandle, TournamentsClient

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
]
