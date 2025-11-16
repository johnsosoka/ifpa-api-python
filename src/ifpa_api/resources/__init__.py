"""Resource clients for IFPA API endpoints.

This package contains resource-specific clients and handles for interacting
with different parts of the IFPA API.
"""

from ifpa_api.resources.director import DirectorClient
from ifpa_api.resources.player import PlayerClient
from ifpa_api.resources.rankings import RankingsClient
from ifpa_api.resources.reference import ReferenceClient
from ifpa_api.resources.series import SeriesClient
from ifpa_api.resources.tournament import TournamentClient

__all__ = [
    "DirectorClient",
    "PlayerClient",
    "RankingsClient",
    "ReferenceClient",
    "TournamentClient",
    "SeriesClient",
]
