"""Pydantic models for IFPA API resources.

This package contains all Pydantic models used for request validation and
response deserialization throughout the SDK.
"""

from ifpa_sdk.models.calendar import CalendarEvent, CalendarResponse
from ifpa_sdk.models.common import (
    IfpaBaseModel,
    RankingSystem,
    ResultType,
    TimePeriod,
    TournamentType,
)
from ifpa_sdk.models.director import (
    CountryDirector,
    CountryDirectorsResponse,
    Director,
    DirectorSearchResponse,
    DirectorSearchResult,
    DirectorStats,
    DirectorTournament,
    DirectorTournamentsResponse,
)
from ifpa_sdk.models.player import (
    Player,
    PlayerCard,
    PlayerRanking,
    PlayerResultsResponse,
    PlayerSearchResponse,
    PlayerSearchResult,
    PvpComparison,
    RankingHistory,
    RankingHistoryEntry,
    TournamentResult,
)
from ifpa_sdk.models.rankings import (
    CountryRankingEntry,
    CountryRankingsResponse,
    CustomRankingEntry,
    CustomRankingsResponse,
    RankingEntry,
    RankingsResponse,
)
from ifpa_sdk.models.series import (
    Series,
    SeriesListResponse,
    SeriesOverview,
    SeriesPlayerCard,
    SeriesPlayerEvent,
    SeriesRegion,
    SeriesRegionsResponse,
    SeriesRules,
    SeriesScheduleEvent,
    SeriesScheduleResponse,
    SeriesStandingEntry,
    SeriesStandingsResponse,
    SeriesStats,
)
from ifpa_sdk.models.tournaments import (
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
from ifpa_sdk.models.tournaments import (
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
    # Player
    "Player",
    "PlayerRanking",
    "PlayerSearchResult",
    "PlayerSearchResponse",
    "TournamentResult",
    "PlayerResultsResponse",
    "RankingHistoryEntry",
    "RankingHistory",
    "PvpComparison",
    "PlayerCard",
    # Rankings
    "RankingEntry",
    "RankingsResponse",
    "CountryRankingEntry",
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
    "SeriesOverview",
    "SeriesRegion",
    "SeriesRegionsResponse",
    "SeriesRules",
    "SeriesStats",
    "SeriesScheduleEvent",
    "SeriesScheduleResponse",
    # Calendar
    "CalendarEvent",
    "CalendarResponse",
]
