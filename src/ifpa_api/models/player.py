"""Player-related Pydantic models.

Models for players, their rankings, tournament results, and head-to-head comparisons.
"""

from typing import Any

from pydantic import Field, field_validator

from ifpa_api.models.common import IfpaBaseModel


class PlayerRanking(IfpaBaseModel):
    """Player ranking in a specific ranking system.

    Attributes:
        ranking_system: The ranking system name (e.g., "Main", "Women", "Youth")
        rank: Current rank position
        rating: Rating/points value
        country_rank: Rank within player's country
        region_rank: Rank within player's region (if applicable)
        active_events: Number of active events counting toward ranking
    """

    ranking_system: str | None = None
    rank: int | None = None
    rating: float | None = None
    country_rank: int | None = None
    region_rank: int | None = None
    active_events: int | None = None


class Player(IfpaBaseModel):
    """Player profile information.

    Attributes:
        player_id: Unique player identifier
        first_name: Player's first name
        last_name: Player's last name
        city: City location
        stateprov: State or province
        country_name: Full country name
        country_code: ISO country code
        profile_photo: URL to profile photo
        initials: Player initials
        age: Player age (if provided)
        excluded_flag: Whether player is excluded from rankings
        ifpa_registered: Whether player has registered with IFPA
        fide_player: Whether player is FIDE rated
        player_stats: Additional player statistics
        rankings: Player rankings across different systems
    """

    player_id: int
    first_name: str
    last_name: str
    city: str | None = None
    stateprov: str | None = None
    country_name: str | None = None
    country_code: str | None = None
    profile_photo: str | None = None
    initials: str | None = None
    age: int | None = None
    excluded_flag: bool | None = None
    ifpa_registered: bool | None = None
    fide_player: bool | None = None
    player_stats: dict[str, Any] | None = None
    rankings: list[PlayerRanking] = Field(default_factory=list)

    @field_validator("age", mode="before")
    @classmethod
    def validate_age(cls, v: Any) -> int | None:
        """Convert empty strings to None, validate age range.

        The IFPA API returns empty string for age when not provided.
        This validator handles that case and validates reasonable age values.

        Args:
            v: The age value from the API (may be int, str, or None)

        Returns:
            The validated age as int, or None if not provided

        Raises:
            ValueError: If age is invalid or out of range
        """
        if v == "" or v is None:
            return None
        try:
            age = int(v)
            if age < 0 or age > 120:
                raise ValueError(f"Age must be between 0 and 120, got {age}")
            return age
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid age value: {v}") from e


class PlayerSearchResult(IfpaBaseModel):
    """Search result for a player.

    Attributes:
        player_id: Unique player identifier
        first_name: Player's first name
        last_name: Player's last name
        city: City location
        state: State or province
        country_code: ISO country code
        country_name: Full country name
        wppr_rank: Current WPPR rank (as string)
    """

    player_id: int
    first_name: str
    last_name: str
    city: str | None = None
    state: str | None = None
    country_code: str | None = None
    country_name: str | None = None
    wppr_rank: str | None = None


class PlayerSearchResponse(IfpaBaseModel):
    """Response for player search query.

    Attributes:
        query: The search query string
        search: List of matching players
    """

    query: str | None = None
    search: list[PlayerSearchResult] = Field(default_factory=list)


class MultiPlayerResponse(IfpaBaseModel):
    """Response for fetching multiple players by ID.

    This represents the response from GET /player?players=123,456 endpoint.
    The API spec shows a single "player" object, but this endpoint accepts
    multiple IDs, so the actual structure may vary. This model is designed
    to be flexible.

    Attributes:
        player: Player or list of players returned
    """

    player: Player | list[Player]


class TournamentResult(IfpaBaseModel):
    """Tournament result for a player.

    Attributes:
        tournament_id: Unique tournament identifier
        tournament_name: Tournament name
        event_name: Event name
        event_date: Date of the tournament
        country_code: ISO country code
        country_name: Full country name
        city: Tournament city
        stateprov: State or province
        position: Player's finishing position
        position_points: Points earned for position
        count_flag: Whether result counts toward rankings
        wppr_points: WPPR points earned
        rating_value: Tournament rating value
        percentile_value: Player's percentile in tournament
        best_game_finish: Best individual game finish
        player_count: Number of participants
    """

    tournament_id: int
    tournament_name: str
    event_name: str | None = None
    event_date: str | None = None
    country_code: str | None = None
    country_name: str | None = None
    city: str | None = None
    stateprov: str | None = None
    position: int | None = None
    position_points: float | None = None
    count_flag: bool | None = None
    wppr_points: float | None = None
    rating_value: float | None = None
    percentile_value: float | None = None
    best_game_finish: int | None = None
    player_count: int | None = None


class PlayerResultsResponse(IfpaBaseModel):
    """Response for player tournament results.

    Attributes:
        player_id: The player's ID
        results: List of tournament results
        total_results: Total number of results
    """

    player_id: int | None = None
    results: list[TournamentResult] = Field(default_factory=list)
    total_results: int | None = None


class RankHistoryEntry(IfpaBaseModel):
    """Historical rank position entry for a player.

    Attributes:
        rank_date: The date of this ranking snapshot
        rank_position: Player's rank position at this date (string in API)
        wppr_points: WPPR points at this date (string in API)
        tournaments_played_count: Number of tournaments played (string in API)
    """

    rank_date: str
    rank_position: str
    wppr_points: str
    tournaments_played_count: str


class RatingHistoryEntry(IfpaBaseModel):
    """Historical rating entry for a player.

    Attributes:
        rating_date: The date of this rating snapshot
        rating: Player's rating at this date (string in API)
    """

    rating_date: str
    rating: str


class RankingHistory(IfpaBaseModel):
    """Player's ranking and rating history over time.

    The IFPA API returns two separate arrays for ranking history:
    - rank_history: Historical rank positions with WPPR points
    - rating_history: Historical rating values

    Attributes:
        player_id: The player's ID
        system: The ranking system (e.g., "MAIN", "WOMEN", "YOUTH")
        active_flag: Whether player is currently active ("Y"/"N")
        rank_history: List of historical rank position entries
        rating_history: List of historical rating entries
    """

    player_id: int
    system: str
    active_flag: str
    rank_history: list[RankHistoryEntry] = Field(default_factory=list)
    rating_history: list[RatingHistoryEntry] = Field(default_factory=list)


class PvpAllCompetitors(IfpaBaseModel):
    """Summary of all competitors a player has faced.

    This represents the response from GET /player/{id}/pvp endpoint,
    which returns a high-level summary of PVP data.

    Attributes:
        player_id: The player's ID
        total_competitors: Total number of competitors faced
        system: Ranking system (e.g., "MAIN")
        type: Type of PVP data (e.g., "all")
        title: Title or description (may be empty)
    """

    player_id: int
    total_competitors: int
    system: str
    type: str
    title: str


class PvpComparison(IfpaBaseModel):
    """Head-to-head comparison between two players.

    Attributes:
        player1_id: First player's ID
        player1_name: First player's name
        player2_id: Second player's ID
        player2_name: Second player's name
        player1_wins: Number of times player 1 finished ahead
        player2_wins: Number of times player 2 finished ahead
        ties: Number of ties
        total_meetings: Total number of tournaments both played
        tournaments: List of tournament comparisons
    """

    player1_id: int
    player1_name: str
    player2_id: int
    player2_name: str
    player1_wins: int | None = None
    player2_wins: int | None = None
    ties: int | None = None
    total_meetings: int | None = None
    tournaments: list[dict[str, Any]] = Field(default_factory=list)


class PlayerCard(IfpaBaseModel):
    """Player card showing achievements and badges.

    Attributes:
        player_id: The player's ID
        player_name: The player's name
        cards: List of earned cards/badges
        achievements: Player achievements
    """

    player_id: int
    player_name: str | None = None
    cards: list[dict[str, Any]] = Field(default_factory=list)
    achievements: dict[str, Any] | None = None
