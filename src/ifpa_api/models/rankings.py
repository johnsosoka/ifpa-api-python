"""Rankings-related Pydantic models.

Models for various IFPA ranking systems including WPPR, Women, Youth, Pro, etc.
"""

from pydantic import AliasChoices, Field

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


class CountryRankingEntry(IfpaBaseModel):
    """Country ranking entry.

    Attributes:
        rank: Country's rank position
        country_code: ISO country code
        country_name: Full country name
        total_players: Number of ranked players from this country
        total_active_players: Number of active players
        total_tournaments: Total tournaments in country
        average_wppr: Average WPPR for country's players
        top_player_id: ID of country's top player
        top_player_name: Name of country's top player
        top_player_wppr: Top player's WPPR value
    """

    rank: int
    country_code: str
    country_name: str
    total_players: int | None = None
    total_active_players: int | None = None
    total_tournaments: int | None = None
    average_wppr: float | None = None
    top_player_id: int | None = None
    top_player_name: str | None = None
    top_player_wppr: float | None = None


class CountryRankingsResponse(IfpaBaseModel):
    """Response for country rankings.

    Attributes:
        country_rankings: List of country ranking entries
        total_countries: Total number of countries ranked
    """

    country_rankings: list[CountryRankingEntry] = Field(default_factory=list, alias="rankings")
    total_countries: int | None = None


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
