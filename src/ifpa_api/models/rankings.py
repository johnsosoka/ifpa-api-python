"""Rankings-related Pydantic models.

Models for various IFPA ranking systems including WPPR, Women, Youth, Pro, etc.
"""

from pydantic import AliasChoices, Field, field_validator

from ifpa_api.models.common import IfpaBaseModel


class RankingEntry(IfpaBaseModel):
    """A single ranking entry in any ranking system.

    Attributes:
        rank: Current rank position (mapped from current_rank field)
        player_id: Unique player identifier
        player_name: Player's full name (mapped from name field)
        first_name: Player's first name
        last_name: Player's last name
        country_code: ISO country code
        country_name: Full country name
        city: City location
        stateprov: State or province
        rating: Rating value (mapped from rating_value field)
        active_events: Number of active events (mapped from event_count field)
        efficiency_value: Efficiency rating (mapped from efficiency_percent field)
        best_finish: Best tournament finish (as string, not int)
        best_finish_position: Best finishing position
        highest_rank: Player's highest rank achieved
        current_wppr: Current WPPR value
        wppr_points: Total WPPR points
        last_played: Date of last tournament
        rating_change: Change in rating from previous period
        rank_change: Change in rank from previous period
        age: Player's age
        profile_photo: URL to profile photo
        last_month_rank: Rank from last month
        rating_deviation: Rating deviation value
    """

    player_id: int
    rank: int | None = Field(default=None, alias="current_rank")
    player_name: str | None = Field(default=None, alias="name")
    first_name: str | None = None
    last_name: str | None = None
    country_code: str | None = None
    country_name: str | None = None
    city: str | None = None
    stateprov: str | None = None
    rating: float | None = Field(
        default=None, validation_alias=AliasChoices("rating_value", "rating")
    )
    active_events: int | None = Field(default=None, alias="event_count")
    efficiency_value: float | None = Field(default=None, alias="efficiency_percent")
    best_finish: str | None = None
    best_finish_position: int | None = None
    highest_rank: int | None = None
    current_wppr: float | None = None
    wppr_points: float | None = None
    last_played: str | None = None
    rating_change: float | None = None
    rank_change: int | None = None
    age: int | None = None
    profile_photo: str | None = Field(
        default=None, validation_alias=AliasChoices("profile_photo_url", "profile_photo")
    )
    last_month_rank: int | None = None
    rating_deviation: int | None = None

    @field_validator("age", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: str | int | None) -> int | None:
        """Convert empty string to None for age field.

        The IFPA API inconsistently returns age as:
        - int (when available)
        - null (when not available in some endpoints)
        - "" empty string (when not available in other endpoints)

        This validator normalizes empty strings to None.
        """
        if v == "" or v is None:
            return None
        return int(v)


class RankingsResponse(IfpaBaseModel):
    """Response for rankings queries.

    Attributes:
        rankings: List of ranking entries
        total_results: Total number of ranked players
        ranking_system: The ranking system name
        last_updated: When rankings were last updated
    """

    rankings: list[RankingEntry] = Field(default_factory=list)
    total_results: int | None = None
    ranking_system: str | None = None
    last_updated: str | None = None


class CountryRankingsResponse(IfpaBaseModel):
    """Response for player rankings filtered by country.

    Note: Despite the name, this endpoint returns individual player
    rankings within a specified country, NOT country-level statistics.

    Attributes:
        ranking_type: Type of ranking (e.g., "country")
        start_position: Starting position in results
        return_count: Number of results returned
        total_count: Total number of players in this country
        rank_country_name: Name of the filtered country
        rankings: List of player ranking entries
    """

    ranking_type: str | None = None
    start_position: int | None = None
    return_count: int | None = None
    total_count: int | None = None
    rank_country_name: str | None = None
    rankings: list[RankingEntry] = Field(default_factory=list)


class CustomRankingEntry(IfpaBaseModel):
    """Custom ranking entry for specialized ranking systems.

    Attributes:
        rank: Rank position
        player_id: Unique player identifier
        player_name: Player's full name
        value: Custom ranking value
        details: Additional ranking-specific details
    """

    rank: int
    player_id: int
    player_name: str
    value: float | None = None
    details: dict[str, float | int | str | None] | None = None


class CustomRankingsResponse(IfpaBaseModel):
    """Response for custom ranking queries.

    Attributes:
        rankings: List of custom ranking entries
        ranking_name: Name of the custom ranking (mapped from title field)
        description: Description of what this ranking measures
    """

    rankings: list[CustomRankingEntry] = Field(default_factory=list, alias="custom_view")
    ranking_name: str | None = Field(default=None, alias="title")
    description: str | None = None


class CountryListEntry(IfpaBaseModel):
    """A country with player count for rankings.

    Attributes:
        country_name: Full name of the country
        country_code: ISO country code
        player_count: Number of ranked players in this country
    """

    country_name: str
    country_code: str
    player_count: int


class RankingsCountryListResponse(IfpaBaseModel):
    """Response from GET /rankings/country_list endpoint.

    Attributes:
        count: Total number of countries returned
        country: List of countries with player counts
    """

    count: int | None = None
    country: list[CountryListEntry] = Field(default_factory=list)


class CustomRankingInfo(IfpaBaseModel):
    """Information about a custom ranking system.

    Attributes:
        view_id: Unique identifier for this custom ranking system
        title: Display title of the custom ranking
        description: Description of what this ranking measures (may be None)
    """

    view_id: int
    title: str
    description: str | None = None


class CustomRankingListResponse(IfpaBaseModel):
    """Response from GET /rankings/custom/list endpoint.

    Attributes:
        total_count: Total number of custom ranking systems
        custom_view: List of available custom ranking systems
    """

    total_count: int | None = None
    custom_view: list[CustomRankingInfo] = Field(default_factory=list)
