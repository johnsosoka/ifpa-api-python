"""Stats-related Pydantic models.

Models for IFPA statistical endpoints including country/state statistics,
tournament data, player activity metrics, and overall IFPA statistics.
"""

from decimal import Decimal
from typing import Any

from pydantic import Field, field_validator

from ifpa_api.models.common import IfpaBaseModel


class CountryPlayerStat(IfpaBaseModel):
    """Player count statistics for a single country.

    Attributes:
        country_name: Full name of the country
        country_code: ISO country code
        player_count: Number of registered players in this country
        stats_rank: Rank position by player count (1 = most players)
    """

    country_name: str
    country_code: str
    player_count: int
    stats_rank: int

    @field_validator("player_count", mode="before")
    @classmethod
    def coerce_player_count(cls, v: Any) -> int:
        """Convert string player count to integer.

        The IFPA API returns player_count as a string (e.g., "47101").
        This validator coerces it to an integer for type safety.

        Args:
            v: The player_count value from the API (may be str or int)

        Returns:
            The player count as an integer
        """
        if isinstance(v, str):
            return int(v)
        return int(v)


class CountryPlayersResponse(IfpaBaseModel):
    """Response from GET /stats/country_players endpoint.

    Attributes:
        type: Response type description
        rank_type: Ranking system used (OPEN or WOMEN)
        stats: List of country player statistics, sorted by player count
    """

    type: str
    rank_type: str
    stats: list[CountryPlayerStat] = Field(default_factory=list)


class StatePlayerStat(IfpaBaseModel):
    """Player count statistics for a single state/province.

    Note: This endpoint is specific to North American states/provinces.
    The "Unknown" state contains players without location data.

    Attributes:
        stateprov: State or province code (e.g., "WA", "CA", "Unknown")
        player_count: Number of registered players in this state/province
        stats_rank: Rank position by player count (1 = most players)
    """

    stateprov: str
    player_count: int
    stats_rank: int

    @field_validator("player_count", mode="before")
    @classmethod
    def coerce_player_count(cls, v: Any) -> int:
        """Convert string player count to integer.

        Args:
            v: The player_count value from the API (may be str or int)

        Returns:
            The player count as an integer
        """
        if isinstance(v, str):
            return int(v)
        return int(v)


class StatePlayersResponse(IfpaBaseModel):
    """Response from GET /stats/state_players endpoint.

    Attributes:
        type: Response type description
        rank_type: Ranking system used (OPEN or WOMEN)
        stats: List of state/province player statistics, sorted by player count
    """

    type: str
    rank_type: str
    stats: list[StatePlayerStat] = Field(default_factory=list)


class StateTournamentStat(IfpaBaseModel):
    """Tournament and points statistics for a single state/province.

    Provides detailed financial/points analysis by state including total
    WPPR points awarded and tournament values.

    Attributes:
        stateprov: State or province code (e.g., "WA", "CA")
        tournament_count: Number of tournaments held in this state
        total_points_all: Total WPPR points awarded across all tournaments
        total_points_tournament_value: Cumulative tournament rating values
        stats_rank: Rank position by tournament count (1 = most tournaments)
    """

    stateprov: str
    tournament_count: int
    total_points_all: Decimal
    total_points_tournament_value: Decimal
    stats_rank: int

    @field_validator("tournament_count", mode="before")
    @classmethod
    def coerce_tournament_count(cls, v: Any) -> int:
        """Convert string tournament count to integer.

        Args:
            v: The tournament_count value from the API (may be str or int)

        Returns:
            The tournament count as an integer
        """
        if isinstance(v, str):
            return int(v)
        return int(v)

    @field_validator("total_points_all", "total_points_tournament_value", mode="before")
    @classmethod
    def coerce_decimal_fields(cls, v: Any) -> Decimal:
        """Convert string point values to Decimal for precision.

        The API returns point values as strings (e.g., "232841.4800").
        Using Decimal preserves full precision for financial calculations.

        Args:
            v: The point value from the API (may be str, int, float, or Decimal)

        Returns:
            The point value as a Decimal
        """
        if isinstance(v, str):
            return Decimal(v)
        return Decimal(str(v))


class StateTournamentsResponse(IfpaBaseModel):
    """Response from GET /stats/state_tournaments endpoint.

    Attributes:
        type: Response type description
        rank_type: Ranking system used (OPEN or WOMEN)
        stats: List of state tournament statistics, sorted by tournament count
    """

    type: str
    rank_type: str
    stats: list[StateTournamentStat] = Field(default_factory=list)


class EventsByYearStat(IfpaBaseModel):
    """Tournament and player statistics for a single year.

    Shows yearly growth trends in international pinball competition.

    Attributes:
        year: Year of the statistics (e.g., "2024")
        country_count: Number of countries with tournaments
        tournament_count: Total number of tournaments held
        player_count: Total number of unique players who competed
        stats_rank: Rank position (1 = most recent year)
    """

    year: str
    country_count: int
    tournament_count: int
    player_count: int
    stats_rank: int

    @field_validator("country_count", "tournament_count", "player_count", mode="before")
    @classmethod
    def coerce_count_fields(cls, v: Any) -> int:
        """Convert string count fields to integers.

        Args:
            v: The count value from the API (may be str or int)

        Returns:
            The count as an integer
        """
        if isinstance(v, str):
            return int(v)
        return int(v)


class EventsByYearResponse(IfpaBaseModel):
    """Response from GET /stats/events_by_year endpoint.

    Attributes:
        type: Response type description
        rank_type: Ranking system used (OPEN or WOMEN)
        stats: List of yearly statistics, sorted by year descending
    """

    type: str
    rank_type: str
    stats: list[EventsByYearStat] = Field(default_factory=list)


class PlayersByYearStat(IfpaBaseModel):
    """Player activity and retention statistics for a single year.

    This unique endpoint tracks player retention across multiple years,
    showing how many players were active in consecutive years.

    Attributes:
        year: Year of the statistics (e.g., "2024")
        current_year_count: Players active in this year
        previous_year_count: Players also active in the previous year
        previous_2_year_count: Players also active 2 years prior
        stats_rank: Rank position (1 = most recent year)
    """

    year: str
    current_year_count: int
    previous_year_count: int
    previous_2_year_count: int
    stats_rank: int

    @field_validator(
        "current_year_count", "previous_year_count", "previous_2_year_count", mode="before"
    )
    @classmethod
    def coerce_count_fields(cls, v: Any) -> int:
        """Convert string count fields to integers.

        Args:
            v: The count value from the API (may be str or int)

        Returns:
            The count as an integer
        """
        if isinstance(v, str):
            return int(v)
        return int(v)


class PlayersByYearResponse(IfpaBaseModel):
    """Response from GET /stats/players_by_year endpoint.

    Attributes:
        type: Response type description
        rank_type: Ranking system used (OPEN or WOMEN)
        stats: List of yearly player retention statistics
    """

    type: str
    rank_type: str
    stats: list[PlayersByYearStat] = Field(default_factory=list)


class LargestTournamentStat(IfpaBaseModel):
    """Information about a single large tournament by player count.

    Attributes:
        country_name: Full name of the country where tournament was held
        country_code: ISO country code
        player_count: Number of participants
        tournament_id: Unique tournament identifier
        tournament_name: Tournament name
        event_name: Specific event name within the tournament
        tournament_date: Date of the tournament (YYYY-MM-DD format)
        stats_rank: Rank position by player count (1 = largest tournament)
    """

    country_name: str
    country_code: str
    player_count: int
    tournament_id: int
    tournament_name: str
    event_name: str
    tournament_date: str
    stats_rank: int

    @field_validator("player_count", mode="before")
    @classmethod
    def coerce_player_count(cls, v: Any) -> int:
        """Convert string player count to integer.

        Args:
            v: The player_count value from the API (may be str or int)

        Returns:
            The player count as an integer
        """
        if isinstance(v, str):
            return int(v)
        return int(v)


class LargestTournamentsResponse(IfpaBaseModel):
    """Response from GET /stats/largest_tournaments endpoint.

    Returns the top 25 tournaments by player count.

    Attributes:
        type: Response type description
        rank_type: Ranking system used (OPEN or WOMEN)
        stats: List of largest tournaments, sorted by player count
    """

    type: str
    rank_type: str
    stats: list[LargestTournamentStat] = Field(default_factory=list)


class LucrativeTournamentStat(IfpaBaseModel):
    """Information about a single high-value tournament.

    Attributes:
        country_name: Full name of the country where tournament was held
        country_code: ISO country code
        tournament_id: Unique tournament identifier
        tournament_name: Tournament name
        event_name: Specific event name within the tournament
        tournament_date: Date of the tournament (YYYY-MM-DD format)
        tournament_value: WPPR value/rating of the tournament
        stats_rank: Rank position by tournament value (1 = highest value)
    """

    country_name: str
    country_code: str
    tournament_id: int
    tournament_name: str
    event_name: str
    tournament_date: str
    tournament_value: float
    stats_rank: int


class LucrativeTournamentsResponse(IfpaBaseModel):
    """Response from GET /stats/lucrative_tournaments endpoint.

    Returns top 25 tournaments by WPPR value. Can be filtered by major
    tournament status using the 'major' parameter.

    Attributes:
        type: Response type description
        rank_type: Ranking system used (OPEN or WOMEN)
        stats: List of high-value tournaments, sorted by tournament value
    """

    type: str
    rank_type: str
    stats: list[LucrativeTournamentStat] = Field(default_factory=list)


class PointsGivenPeriodStat(IfpaBaseModel):
    """Points earned by a player during a specific time period.

    Used to identify top point earners in a date range.

    Attributes:
        player_id: Unique player identifier
        first_name: Player's first name
        last_name: Player's last name
        country_name: Full country name
        country_code: ISO country code
        wppr_points: Total WPPR points earned during the period
        stats_rank: Rank position by points earned (1 = most points)
    """

    player_id: int
    first_name: str
    last_name: str
    country_name: str
    country_code: str
    wppr_points: Decimal
    stats_rank: int

    @field_validator("player_id", mode="before")
    @classmethod
    def coerce_player_id(cls, v: Any) -> int:
        """Convert string player_id to integer.

        The API returns player_id as a string in period endpoints.

        Args:
            v: The player_id value from the API (may be str or int)

        Returns:
            The player ID as an integer
        """
        if isinstance(v, str):
            return int(v)
        return int(v)

    @field_validator("wppr_points", mode="before")
    @classmethod
    def coerce_wppr_points(cls, v: Any) -> Decimal:
        """Convert string WPPR points to Decimal for precision.

        The API returns wppr_points as a string (e.g., "4264.61").
        Using Decimal preserves full precision for point calculations.

        Args:
            v: The wppr_points value from the API (may be str, int, float, or Decimal)

        Returns:
            The WPPR points as a Decimal
        """
        if isinstance(v, str):
            return Decimal(v)
        return Decimal(str(v))


class PointsGivenPeriodResponse(IfpaBaseModel):
    """Response from GET /stats/points_given_period endpoint.

    Returns top point earners for a date range with support for limit,
    rank_type, and country_code filtering.

    Attributes:
        type: Response type description
        start_date: Start date of the period (YYYY-MM-DD format)
        end_date: End date of the period (YYYY-MM-DD format)
        return_count: Number of results returned
        rank_type: Ranking system used (OPEN or WOMEN)
        stats: List of player point statistics for the period
    """

    type: str
    start_date: str
    end_date: str
    return_count: int
    rank_type: str
    stats: list[PointsGivenPeriodStat] = Field(default_factory=list)


class EventsAttendedPeriodStat(IfpaBaseModel):
    """Tournament attendance by a player during a specific time period.

    Used to identify most active players by tournament count.

    Attributes:
        player_id: Unique player identifier
        first_name: Player's first name
        last_name: Player's last name
        country_name: Full country name
        country_code: ISO country code
        tournament_count: Number of tournaments attended during the period
        stats_rank: Rank position by tournament count (1 = most tournaments)
    """

    player_id: int
    first_name: str
    last_name: str
    country_name: str
    country_code: str
    tournament_count: int
    stats_rank: int

    @field_validator("player_id", mode="before")
    @classmethod
    def coerce_player_id(cls, v: Any) -> int:
        """Convert string player_id to integer.

        The API returns player_id as a string in period endpoints.

        Args:
            v: The player_id value from the API (may be str or int)

        Returns:
            The player ID as an integer
        """
        if isinstance(v, str):
            return int(v)
        return int(v)

    @field_validator("tournament_count", mode="before")
    @classmethod
    def coerce_tournament_count(cls, v: Any) -> int:
        """Convert string tournament count to integer.

        Args:
            v: The tournament_count value from the API (may be str or int)

        Returns:
            The tournament count as an integer
        """
        if isinstance(v, str):
            return int(v)
        return int(v)


class EventsAttendedPeriodResponse(IfpaBaseModel):
    """Response from GET /stats/events_attended_period endpoint.

    Returns most active players by tournament attendance for a date range
    with support for limit, rank_type, and country_code filtering.

    Note: Unlike points_given_period, this endpoint does not include a
    rank_type field in the response.

    Attributes:
        type: Response type description
        start_date: Start date of the period (YYYY-MM-DD format)
        end_date: End date of the period (YYYY-MM-DD format)
        return_count: Number of results returned
        stats: List of player tournament attendance statistics
    """

    type: str
    start_date: str
    end_date: str
    return_count: int
    stats: list[EventsAttendedPeriodStat] = Field(default_factory=list)


class AgeGenderStats(IfpaBaseModel):
    """Age distribution statistics for IFPA players.

    All values are percentages representing the proportion of players
    in each age bracket.

    Attributes:
        age_under_18: Percentage of players under 18 years old
        age_18_to_29: Percentage of players aged 18-29
        age_30_to_39: Percentage of players aged 30-39
        age_40_to_49: Percentage of players aged 40-49
        age_50_to_99: Percentage of players aged 50 and above
    """

    age_under_18: float
    age_18_to_29: float
    age_30_to_39: float
    age_40_to_49: float
    age_50_to_99: float


class OverallStats(IfpaBaseModel):
    """Overall IFPA statistics and aggregate metrics.

    Note: Unlike other stats endpoints, all numeric fields here are
    returned as proper numbers (int/float) rather than strings.

    Attributes:
        overall_player_count: Total registered players across all time
        active_player_count: Currently active players
        tournament_count: Total tournaments held
        tournament_count_last_month: Tournaments in the past month
        tournament_count_this_year: Tournaments held in the current year
        tournament_player_count: Total tournament participations (player-events)
        tournament_player_count_average: Average number of players per tournament
        age: Age distribution statistics for players
    """

    overall_player_count: int
    active_player_count: int
    tournament_count: int
    tournament_count_last_month: int
    tournament_count_this_year: int
    tournament_player_count: int
    tournament_player_count_average: float
    age: AgeGenderStats


class OverallStatsResponse(IfpaBaseModel):
    """Response from GET /stats/overall endpoint.

    Note: This endpoint has a unique structure where 'stats' is a single
    object rather than an array like other stats endpoints.

    API Bug: As of 2025-11-19, the system_code=WOMEN parameter appears to
    be ignored, and the endpoint always returns OPEN statistics regardless
    of the requested system_code.

    Attributes:
        type: Response type description
        system_code: Ranking system used (OPEN or WOMEN)
        stats: Overall statistics object (not an array)
    """

    type: str
    system_code: str
    stats: OverallStats
