"""Pydantic models for IFPA API resources.

This package contains all Pydantic models used for request validation and
response deserialization throughout the SDK.
"""

from ifpa_api.models.calendar import CalendarEvent, CalendarResponse
from ifpa_api.models.common import (
    IfpaBaseModel,
    RankingSystem,
    ResultType,
    TimePeriod,
    TournamentType,
)
from ifpa_api.models.director import (
    CountryDirector,
    CountryDirectorsResponse,
    Director,
    DirectorSearchResponse,
    DirectorSearchResult,
    DirectorStats,
    DirectorTournament,
    DirectorTournamentsResponse,
    PlayerProfile,
)
from ifpa_api.models.player import (
    MultiPlayerResponse,
    Player,
    PlayerCard,
    PlayerRanking,
    PlayerResultsResponse,
    PlayerSearchResponse,
    PlayerSearchResult,
    PvpAllCompetitors,
    PvpComparison,
    RankHistoryEntry,
    RankingHistory,
    RatingHistoryEntry,
    TournamentResult,
)
from ifpa_api.models.rankings import (
    CountryRankingsResponse,
    CustomRankingEntry,
    CustomRankingsResponse,
    RankingEntry,
    RankingsResponse,
)
from ifpa_api.models.series import (
    RegionOverview,
    RegionRepresentative,
    RegionRepsResponse,
    RegionStandingEntry,
    Series,
    SeriesListResponse,
    SeriesPlayerCard,
    SeriesPlayerEvent,
    SeriesRegion,
    SeriesRegionsResponse,
    SeriesRegionStandingsResponse,
    SeriesStandingEntry,
    SeriesStandingsResponse,
    SeriesStats,
    SeriesTournament,
    SeriesTournamentsResponse,
)
from ifpa_api.models.tournaments import (
    LeagueSession,
    Tournament,
    TournamentFormat,
    TournamentFormatsResponse,
    TournamentLeagueResponse,
    TournamentResultsResponse,
    TournamentSearchResponse,
    TournamentSearchResult,
    TournamentSubmission,
    TournamentSubmissionsResponse,
)
from ifpa_api.models.tournaments import (
    TournamentResult as TournamentResultDetail,
)

__all__ = [
    # Common
    "IfpaBaseModel",
    "TimePeriod",
    "RankingSystem",
    "ResultType",
    "TournamentType",
    # Director
    "Director",
    "DirectorStats",
    "DirectorTournament",
    "DirectorTournamentsResponse",
    "DirectorSearchResult",
    "DirectorSearchResponse",
    "CountryDirector",
    "CountryDirectorsResponse",
    "PlayerProfile",
    # Player
    "Player",
    "PlayerRanking",
    "PlayerSearchResult",
    "PlayerSearchResponse",
    "MultiPlayerResponse",
    "TournamentResult",
    "PlayerResultsResponse",
    "RankHistoryEntry",
    "RankingHistory",
    "RatingHistoryEntry",
    "PvpAllCompetitors",
    "PvpComparison",
    "PlayerCard",
    # Rankings
    "RankingEntry",
    "RankingsResponse",
    "CountryRankingsResponse",
    "CustomRankingEntry",
    "CustomRankingsResponse",
    # Tournaments
    "Tournament",
    "TournamentResultDetail",
    "TournamentResultsResponse",
    "TournamentFormat",
    "TournamentFormatsResponse",
    "LeagueSession",
    "TournamentLeagueResponse",
    "TournamentSubmission",
    "TournamentSubmissionsResponse",
    "TournamentSearchResult",
    "TournamentSearchResponse",
    # Series
    "Series",
    "SeriesListResponse",
    "SeriesStandingEntry",
    "SeriesStandingsResponse",
    "SeriesPlayerEvent",
    "SeriesPlayerCard",
    "SeriesRegion",
    "SeriesRegionsResponse",
    "SeriesStats",
    "SeriesTournament",
    "SeriesTournamentsResponse",
    "RegionOverview",
    "RegionRepresentative",
    "RegionRepsResponse",
    "RegionStandingEntry",
    "SeriesRegionStandingsResponse",
    # Calendar
    "CalendarEvent",
    "CalendarResponse",
]
