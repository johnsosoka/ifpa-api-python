"""Director-related Pydantic models.

Models for tournament directors, their statistics, and tournament history.
"""

from pydantic import Field

from ifpa_sdk.models.common import IfpaBaseModel


class DirectorFormat(IfpaBaseModel):
    """Tournament format information for a director.

    Attributes:
        name: The format name (e.g., "Strike Knockout")
        count: Number of tournaments using this format
    """

    name: str | None = None
    count: int | None = None


class DirectorStats(IfpaBaseModel):
    """Statistics about a tournament director's activity.

    Attributes:
        tournament_count: Total number of tournaments directed
        unique_location_count: Number of unique venues
        women_tournament_count: Number of women's tournaments
        league_count: Number of league events
        highest_value: Highest tournament value/rating
        average_value: Average tournament value/rating
        total_player_count: Total player participations
        unique_player_count: Number of unique players
        first_time_player_count: Players competing for first time
        repeat_player_count: Repeat participants
        largest_event_count: Size of largest event
        single_format_count: Tournaments with single format
        multiple_format_count: Tournaments with multiple formats
        unknown_format_count: Tournaments with unspecified format
        formats: List of format usage details (if available)
    """

    tournament_count: int | None = None
    unique_location_count: int | None = None
    women_tournament_count: int | None = None
    league_count: int | None = None
    highest_value: float | None = None
    average_value: float | None = None
    total_player_count: int | None = None
    unique_player_count: int | None = None
    first_time_player_count: int | None = None
    repeat_player_count: int | None = None
    largest_event_count: int | None = None
    single_format_count: int | None = None
    multiple_format_count: int | None = None
    unknown_format_count: int | None = None
    formats: list[DirectorFormat] = Field(default_factory=list)


class Director(IfpaBaseModel):
    """Tournament director information.

    Attributes:
        director_id: Unique director identifier
        name: Director's full name
        profile_photo: URL to profile photo
        city: City location
        stateprov: State or province
        country_name: Full country name
        country_code: ISO country code
        country_id: IFPA country identifier
        twitch_username: Twitch username (if available)
        stats: Director statistics and metrics
    """

    director_id: int
    name: str
    profile_photo: str | None = None
    city: str | None = None
    stateprov: str | None = None
    country_name: str | None = None
    country_code: str | None = None
    country_id: int | None = None
    twitch_username: str | None = None
    stats: DirectorStats | None = None


class DirectorTournament(IfpaBaseModel):
    """Tournament information in a director's history.

    Attributes:
        tournament_id: Unique tournament identifier
        tournament_name: Tournament name
        event_date: Date of the tournament
        event_name: Event name (if different from tournament)
        location_name: Venue name
        city: Tournament city
        stateprov: State or province
        country_name: Country name
        country_code: ISO country code
        value: Tournament rating/value
        player_count: Number of participants
        women_only: Whether this is a women-only tournament
    """

    tournament_id: int
    tournament_name: str
    event_date: str | None = None
    event_name: str | None = None
    location_name: str | None = None
    city: str | None = None
    stateprov: str | None = None
    country_name: str | None = None
    country_code: str | None = None
    value: float | None = None
    player_count: int | None = None
    women_only: bool | None = Field(default=None, alias="women_only")


class DirectorTournamentsResponse(IfpaBaseModel):
    """Response for director tournaments list.

    Attributes:
        director_id: The director's ID
        director_name: The director's name
        tournaments: List of tournaments
        total_count: Total number of tournaments
    """

    director_id: int | None = None
    director_name: str | None = None
    tournaments: list[DirectorTournament] = Field(default_factory=list)
    total_count: int | None = None


class DirectorSearchResult(IfpaBaseModel):
    """Search result for a director.

    Attributes:
        director_id: Unique director identifier
        name: Director's full name
        city: City location
        stateprov: State or province
        country_code: ISO country code
        tournament_count: Number of tournaments directed
    """

    director_id: int
    name: str
    city: str | None = None
    stateprov: str | None = None
    country_code: str | None = None
    tournament_count: int | None = None


class DirectorSearchResponse(IfpaBaseModel):
    """Response for director search query.

    Attributes:
        directors: List of matching directors
        total_results: Total number of results found
    """

    directors: list[DirectorSearchResult] = Field(default_factory=list)
    total_results: int | None = None


class CountryDirector(IfpaBaseModel):
    """Country director information.

    Attributes:
        player_id: The player ID of the country director
        name: Director's full name
        country_code: ISO country code
        country_name: Full country name
    """

    player_id: int
    name: str
    country_code: str
    country_name: str


class CountryDirectorsResponse(IfpaBaseModel):
    """Response for country directors list.

    Attributes:
        country_directors: List of country directors
    """

    country_directors: list[CountryDirector] = Field(default_factory=list, alias="directors")
