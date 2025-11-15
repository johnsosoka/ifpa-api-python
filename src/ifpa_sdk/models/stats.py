"""Statistics-related Pydantic models.

Models for global statistics, trends, and aggregate data.
"""

from typing import Any

from pydantic import Field

from ifpa_sdk.models.common import IfpaBaseModel


class GlobalStats(IfpaBaseModel):
    """Global IFPA statistics.

    Attributes:
        total_players: Total number of players
        total_tournaments: Total number of tournaments
        total_active_players: Number of currently active players
        total_countries: Number of countries with players
        total_wppr_points: Sum of all WPPR points
        average_wppr: Average WPPR across all players
        stats_date: Date these statistics were calculated
    """

    total_players: int | None = None
    total_tournaments: int | None = None
    total_active_players: int | None = None
    total_countries: int | None = None
    total_wppr_points: float | None = None
    average_wppr: float | None = None
    stats_date: str | None = None


class PlayerCountStats(IfpaBaseModel):
    """Player count statistics over time or by category.

    Attributes:
        period: Time period or category
        player_count: Number of players
        active_count: Number of active players
        new_players: Number of new players
        returning_players: Number of returning players
    """

    period: str
    player_count: int | None = None
    active_count: int | None = None
    new_players: int | None = None
    returning_players: int | None = None


class PlayerCountStatsResponse(IfpaBaseModel):
    """Response for player count statistics.

    Attributes:
        stats: List of player count statistics
        total_periods: Total number of periods
    """

    stats: list[PlayerCountStats] = Field(default_factory=list)
    total_periods: int | None = None


class TournamentCountStats(IfpaBaseModel):
    """Tournament count statistics over time or by category.

    Attributes:
        period: Time period or category
        tournament_count: Number of tournaments
        total_players: Total player participations
        average_size: Average tournament size
        largest_event: Largest event in period
    """

    period: str
    tournament_count: int | None = None
    total_players: int | None = None
    average_size: float | None = None
    largest_event: int | None = None


class TournamentCountStatsResponse(IfpaBaseModel):
    """Response for tournament count statistics.

    Attributes:
        stats: List of tournament count statistics
        total_periods: Total number of periods
    """

    stats: list[TournamentCountStats] = Field(default_factory=list)
    total_periods: int | None = None


class TopCountryStats(IfpaBaseModel):
    """Statistics for top countries.

    Attributes:
        rank: Country rank
        country_code: ISO country code
        country_name: Full country name
        player_count: Number of players
        tournament_count: Number of tournaments
        average_wppr: Average WPPR for country
        top_player: Top player information
    """

    rank: int
    country_code: str
    country_name: str
    player_count: int | None = None
    tournament_count: int | None = None
    average_wppr: float | None = None
    top_player: dict[str, Any] | None = None


class TopCountriesResponse(IfpaBaseModel):
    """Response for top countries statistics.

    Attributes:
        countries: List of country statistics
        total_countries: Total number of countries
    """

    countries: list[TopCountryStats] = Field(default_factory=list)
    total_countries: int | None = None


class TopTournamentStats(IfpaBaseModel):
    """Statistics for top tournaments.

    Attributes:
        rank: Tournament rank
        tournament_id: Tournament identifier
        tournament_name: Tournament name
        event_date: Tournament date
        player_count: Number of participants
        rating_value: Tournament rating value
        country_code: ISO country code
    """

    rank: int
    tournament_id: int
    tournament_name: str
    event_date: str | None = None
    player_count: int | None = None
    rating_value: float | None = None
    country_code: str | None = None


class TopTournamentsResponse(IfpaBaseModel):
    """Response for top tournaments statistics.

    Attributes:
        tournaments: List of tournament statistics
        criteria: Ranking criteria used
    """

    tournaments: list[TopTournamentStats] = Field(default_factory=list)
    criteria: str | None = None


class RecentTournamentStats(IfpaBaseModel):
    """Statistics for recent tournaments.

    Attributes:
        tournament_id: Tournament identifier
        tournament_name: Tournament name
        event_date: Tournament date
        player_count: Number of participants
        rating_value: Tournament rating value
        country_code: ISO country code
        days_ago: Days since tournament
    """

    tournament_id: int
    tournament_name: str
    event_date: str | None = None
    player_count: int | None = None
    rating_value: float | None = None
    country_code: str | None = None
    days_ago: int | None = None


class RecentTournamentsResponse(IfpaBaseModel):
    """Response for recent tournaments statistics.

    Attributes:
        tournaments: List of recent tournament statistics
        period_days: Number of days covered
    """

    tournaments: list[RecentTournamentStats] = Field(default_factory=list)
    period_days: int | None = None


class MachinePopularityStats(IfpaBaseModel):
    """Machine/game popularity statistics.

    Attributes:
        rank: Popularity rank
        machine_name: Name of the pinball machine
        manufacturer: Machine manufacturer
        year: Year of manufacture
        usage_count: Number of times used in tournaments
        tournament_count: Number of tournaments featuring this machine
        average_players: Average players on this machine
    """

    rank: int
    machine_name: str
    manufacturer: str | None = None
    year: int | None = None
    usage_count: int | None = None
    tournament_count: int | None = None
    average_players: float | None = None


class MachinePopularityResponse(IfpaBaseModel):
    """Response for machine popularity statistics.

    Attributes:
        machines: List of machine popularity statistics
        period: Time period covered
    """

    machines: list[MachinePopularityStats] = Field(default_factory=list)
    period: str | None = None


class TrendData(IfpaBaseModel):
    """Trend data point.

    Attributes:
        date: Date of data point
        value: Value at this date
        change: Change from previous period
        percentage_change: Percentage change from previous period
    """

    date: str
    value: float | None = None
    change: float | None = None
    percentage_change: float | None = None


class TrendsResponse(IfpaBaseModel):
    """Response for trend statistics.

    Attributes:
        metric: The metric being trended
        data_points: List of trend data points
        trend_direction: Overall trend direction (up, down, stable)
    """

    metric: str
    data_points: list[TrendData] = Field(default_factory=list)
    trend_direction: str | None = None


class HistoricalStats(IfpaBaseModel):
    """Historical statistics over time.

    Attributes:
        year: Year
        total_players: Total players in year
        total_tournaments: Total tournaments in year
        new_players: New players in year
        average_wppr: Average WPPR in year
        additional_metrics: Additional yearly metrics
    """

    year: int
    total_players: int | None = None
    total_tournaments: int | None = None
    new_players: int | None = None
    average_wppr: float | None = None
    additional_metrics: dict[str, Any] | None = None


class HistoricalStatsResponse(IfpaBaseModel):
    """Response for historical statistics.

    Attributes:
        stats: List of historical statistics by year
        earliest_year: Earliest year in data
        latest_year: Latest year in data
    """

    stats: list[HistoricalStats] = Field(default_factory=list)
    earliest_year: int | None = None
    latest_year: int | None = None


class ParticipationStats(IfpaBaseModel):
    """Player participation statistics.

    Attributes:
        category: Participation category
        player_count: Number of players
        percentage: Percentage of total players
        average_events: Average events per player
    """

    category: str
    player_count: int | None = None
    percentage: float | None = None
    average_events: float | None = None


class ParticipationStatsResponse(IfpaBaseModel):
    """Response for participation statistics.

    Attributes:
        stats: List of participation statistics
        total_active_players: Total active players
    """

    stats: list[ParticipationStats] = Field(default_factory=list)
    total_active_players: int | None = None
