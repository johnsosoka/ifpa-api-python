"""Player-related Pydantic models.

Models for players, their rankings, tournament results, and head-to-head comparisons.
"""

from typing import Any

from pydantic import Field

from ifpa_sdk.models.common import IfpaBaseModel


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


class PlayerSearchResult(IfpaBaseModel):
    """Search result for a player.

    Attributes:
        player_id: Unique player identifier
        first_name: Player's first name
        last_name: Player's last name
        city: City location
        stateprov: State or province
        country_code: ISO country code
        wppr_rank: Current WPPR rank
        wppr_value: Current WPPR value
    """

    player_id: int
    first_name: str
    last_name: str
    city: str | None = None
    stateprov: str | None = None
    country_code: str | None = None
    wppr_rank: int | None = None
    wppr_value: float | None = None


class PlayerSearchResponse(IfpaBaseModel):
    """Response for player search query.

    Attributes:
        players: List of matching players
        total_results: Total number of results found
    """

    players: list[PlayerSearchResult] = Field(default_factory=list)
    total_results: int | None = None


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


class RankingHistoryEntry(IfpaBaseModel):
    """Historical ranking entry for a player.

    Attributes:
        date: The date of this ranking snapshot
        rank: Player's rank at this date
        rating: Player's rating at this date
        active_events: Number of active events at this date
        rating_change: Change in rating from previous entry
        rank_change: Change in rank from previous entry
    """

    date: str
    rank: int | None = None
    rating: float | None = None
    active_events: int | None = None
    rating_change: float | None = None
    rank_change: int | None = None


class RankingHistory(IfpaBaseModel):
    """Player's ranking history over time.

    Attributes:
        player_id: The player's ID
        ranking_system: The ranking system (e.g., "Main", "Women")
        history: List of historical ranking entries
    """

    player_id: int
    ranking_system: str
    history: list[RankingHistoryEntry] = Field(default_factory=list)


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
