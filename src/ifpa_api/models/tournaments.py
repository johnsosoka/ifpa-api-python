"""Tournament-related Pydantic models.

Models for tournament information, results, formats, and league data.
"""

from typing import Any

from pydantic import Field, field_validator

from ifpa_api.models.common import IfpaBaseModel


class Tournament(IfpaBaseModel):
    """Tournament information.

    Attributes:
        tournament_id: Unique tournament identifier
        tournament_name: Tournament name
        event_name: Parent event name (if part of larger event)
        director_name: Tournament director's name
        director_id: Tournament director's ID
        location_name: Venue name
        address1: Street address
        address2: Additional address info
        city: City location
        stateprov: State or province
        zipcode: Postal code
        country_name: Full country name
        country_code: ISO country code
        website: Tournament website URL
        lat: Latitude coordinate
        long: Longitude coordinate
        event_date: Date of the tournament
        event_start_date: Start date (for multi-day events)
        event_end_date: End date (for multi-day events)
        player_count: Number of participants
        machine_count: Number of machines/games used
        tournament_type: Type of tournament (open, women, etc.)
        rating_value: Tournament rating value
        wppr_value: WPPR value for the tournament
        private_flag: Whether tournament is private
        women_only: Whether tournament is women-only
        entry_fee: Entry fee amount (if applicable)
        prize_pool: Total prize pool (if applicable)
        details: Additional tournament details
    """

    tournament_id: int
    tournament_name: str
    event_name: str | None = None
    director_name: str | None = None
    director_id: int | None = None
    location_name: str | None = None
    address1: str | None = None
    address2: str | None = None
    city: str | None = None
    stateprov: str | None = None
    zipcode: str | None = None
    country_name: str | None = None
    country_code: str | None = None
    website: str | None = None
    lat: float | None = None
    long: float | None = None
    event_date: str | None = None
    event_start_date: str | None = None
    event_end_date: str | None = None
    player_count: int | None = None
    machine_count: int | None = None
    tournament_type: str | None = None
    rating_value: float | None = None
    wppr_value: float | None = None
    private_flag: bool | None = None
    women_only: bool | None = None
    entry_fee: float | None = None
    prize_pool: float | None = None
    details: str | None = None


class TournamentResult(IfpaBaseModel):
    """Individual result in a tournament.

    Attributes:
        position: Finishing position
        player_id: Unique player identifier
        player_name: Player's full name
        first_name: Player's first name
        last_name: Player's last name
        city: Player's city
        stateprov: Player's state/province
        country_code: ISO country code
        country_name: Full country name
        points: WPPR points earned
        wppr_rank: Player's current WPPR rank
        ratings_value: Rating points earned
        percentile: Player's percentile in tournament
        best_game_finish: Best individual game finish
        player_tournament_count: Total events played
    """

    position: int
    player_id: int
    player_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    city: str | None = None
    stateprov: str | None = None
    country_code: str | None = None
    country_name: str | None = None
    points: float | None = None
    wppr_rank: int | None = None
    ratings_value: float | None = None
    percentile: float | None = None
    best_game_finish: int | None = None
    player_tournament_count: int | None = None

    @field_validator("ratings_value", "points", "percentile", mode="before")
    @classmethod
    def handle_not_rated(cls, v: Any) -> float | None:
        """Convert "Not Rated" string to None for float fields.

        The IFPA API returns "Not Rated" as a string for unrated players,
        but the schema expects float values. This validator handles that
        conversion.

        Args:
            v: The value from the API (may be float, int, str, or None)

        Returns:
            The value as float, or None if "Not Rated" or empty
        """
        if v == "Not Rated" or v == "" or v is None:
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None


class TournamentResultsResponse(IfpaBaseModel):
    """Response for tournament results.

    Attributes:
        tournament_id: The tournament's ID
        tournament_name: The tournament's name
        event_date: Tournament date
        results: List of player results
        player_count: Total number of participants
    """

    tournament_id: int | None = None
    tournament_name: str | None = None
    event_date: str | None = None
    results: list[TournamentResult] = Field(default_factory=list)
    player_count: int | None = None


class TournamentFormat(IfpaBaseModel):
    """Format information for a tournament.

    Attributes:
        format_id: Format identifier
        format_name: Format name (e.g., "Swiss", "Match Play", "Strike Knockout")
        rounds: Number of rounds
        games_per_round: Games per round
        player_count: Number of players in this format
        machine_list: List of machines used
        details: Additional format details
    """

    format_id: int | None = None
    format_name: str
    rounds: int | None = None
    games_per_round: int | None = None
    player_count: int | None = None
    machine_list: list[str] = Field(default_factory=list)
    details: str | None = None


class TournamentFormatsResponse(IfpaBaseModel):
    """Response for tournament formats.

    Attributes:
        tournament_id: The tournament's ID
        formats: List of formats used in the tournament
    """

    tournament_id: int | None = None
    formats: list[TournamentFormat] = Field(default_factory=list)


class LeagueSession(IfpaBaseModel):
    """League session data.

    Attributes:
        session_date: Date of the session
        player_count: Number of players in session
        session_value: WPPR value for session
        session_data: Additional session details
    """

    session_date: str
    player_count: int | None = None
    session_value: float | None = None
    session_data: dict[str, Any] | None = None


class TournamentLeagueResponse(IfpaBaseModel):
    """Response for tournament league data.

    Attributes:
        tournament_id: The tournament's ID
        league_format: League format description
        sessions: List of league sessions
        total_sessions: Total number of sessions
    """

    tournament_id: int | None = None
    league_format: str | None = None
    sessions: list[LeagueSession] = Field(default_factory=list)
    total_sessions: int | None = None


class TournamentSubmission(IfpaBaseModel):
    """Tournament submission information.

    Attributes:
        submission_id: Unique submission identifier
        submission_date: Date of submission
        submitter_name: Name of person who submitted
        status: Submission status
        details: Submission details
    """

    submission_id: int
    submission_date: str | None = None
    submitter_name: str | None = None
    status: str | None = None
    details: str | None = None


class TournamentSubmissionsResponse(IfpaBaseModel):
    """Response for tournament submissions.

    Attributes:
        tournament_id: The tournament's ID
        submissions: List of submissions
    """

    tournament_id: int | None = None
    submissions: list[TournamentSubmission] = Field(default_factory=list)


class TournamentSearchResult(IfpaBaseModel):
    """Search result for a tournament.

    Attributes:
        tournament_id: Unique tournament identifier
        tournament_name: Tournament name
        event_name: Event name
        event_date: Date of the tournament
        city: City location
        stateprov: State or province
        country_code: ISO country code
        player_count: Number of participants
        rating_value: Tournament rating value
    """

    tournament_id: int
    tournament_name: str
    event_name: str | None = None
    event_date: str | None = None
    city: str | None = None
    stateprov: str | None = None
    country_code: str | None = None
    player_count: int | None = None
    rating_value: float | None = None


class TournamentSearchResponse(IfpaBaseModel):
    """Response for tournament search query.

    Note:
        The API returns tournament data under the 'search' key, not 'tournaments'.

    Attributes:
        tournaments: List of matching tournaments
        total_results: Total number of results found
    """

    tournaments: list[TournamentSearchResult] = Field(default_factory=list, alias="search")
    total_results: int | None = None


class RelatedTournamentWinner(IfpaBaseModel):
    """Winner information for a related tournament."""

    player_id: int
    name: str
    country_name: str
    country_code: str


class RelatedTournament(IfpaBaseModel):
    """A tournament related to the current tournament (same venue or series)."""

    tournament_id: int
    tournament_name: str
    tournament_type: str | None = None
    event_name: str
    event_start_date: str
    event_end_date: str
    ranking_system: str | None = None
    winner: RelatedTournamentWinner | None = None


class RelatedTournamentsResponse(IfpaBaseModel):
    """Response from GET /tournament/{id}/related endpoint."""

    tournament: list[RelatedTournament] = Field(default_factory=list)


class FormatDefinition(IfpaBaseModel):
    """Definition of a tournament format type."""

    format_id: int
    name: str
    description: str | None = None


class TournamentFormatsListResponse(IfpaBaseModel):
    """Response from GET /tournament/formats endpoint.

    Formats are split into two categories:
    - qualifying_formats: Formats used for qualifying rounds (11 types)
    - finals_formats: Formats used for finals rounds (14 types)
    """

    qualifying_formats: list[FormatDefinition] = Field(default_factory=list)
    finals_formats: list[FormatDefinition] = Field(default_factory=list)
