"""Director-related Pydantic models.

Models for tournament directors, their statistics, and tournament history.
"""

from pydantic import Field

from ifpa_api.models.common import IfpaBaseModel


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

    Note: The API may return event_date, event_start_date, or both depending on context.
    This model handles both field names for maximum compatibility.

    Attributes:
        tournament_id: Unique tournament identifier
        tournament_name: Tournament name
        event_date: Date of the tournament (legacy field, maps to event_start_date)
        event_start_date: Tournament start date (ISO 8601 format)
        event_end_date: Tournament end date (ISO 8601 format)
        event_name: Event name (if different from tournament)
        ranking_system: Ranking system used (e.g., "MAIN", "PRO")
        qualifying_format: Format used for qualifying rounds
        finals_format: Format used for finals
        location_name: Venue name
        city: Tournament city
        stateprov: State or province (alias: stateprov_code)
        country_name: Country name
        country_code: ISO country code
        value: Tournament rating/value
        player_count: Number of participants
        women_only: Whether this is a women-only tournament
    """

    tournament_id: int
    tournament_name: str
    # Support both event_date (legacy) and event_start_date (spec)
    event_date: str | None = Field(default=None, alias="event_start_date")
    event_end_date: str | None = None
    event_name: str | None = None
    ranking_system: str | None = None
    qualifying_format: str | None = None
    finals_format: str | None = None
    location_name: str | None = None
    city: str | None = None
    # Support both stateprov and stateprov_code
    stateprov: str | None = Field(default=None, alias="stateprov_code")
    country_name: str | None = None
    country_code: str | None = None
    value: float | None = None
    player_count: int | None = None
    women_only: bool | None = None


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
        country_name: Full country name
        country_code: ISO country code
        profile_photo: URL to profile photo
        tournament_count: Number of tournaments directed
    """

    director_id: int
    name: str
    city: str | None = None
    stateprov: str | None = None
    country_name: str | None = None
    country_code: str | None = None
    profile_photo: str | None = None
    tournament_count: int | None = None


class DirectorSearchResponse(IfpaBaseModel):
    """Response for director search query.

    Note: The API spec shows search_term and count fields, but the actual API
    may also return total_results. This model supports both patterns.

    Attributes:
        search_term: The search term used (from API spec)
        count: Number of results returned (from API spec, alias: total_results)
        directors: List of matching directors
    """

    search_term: str | None = None
    count: int | None = Field(default=None, alias="total_results")
    directors: list[DirectorSearchResult] = Field(default_factory=list)


class PlayerProfile(IfpaBaseModel):
    """Player profile nested in country director response.

    This structure is returned by the /director/country endpoint
    where each country director has their player information nested
    inside a player_profile object.

    Attributes:
        player_id: The player ID of the country director
        name: Director's full name
        country_code: ISO country code
        country_name: Full country name
        profile_photo: URL to profile photo
    """

    player_id: int
    name: str
    country_code: str
    country_name: str
    profile_photo: str | None = None


class CountryDirector(IfpaBaseModel):
    """Country director information with nested player profile.

    The API returns country directors with a nested player_profile structure
    containing the actual director information.

    Attributes:
        player_profile: Nested player profile with director details
    """

    player_profile: PlayerProfile


class CountryDirectorsResponse(IfpaBaseModel):
    """Response for country directors list.

    The API returns 'country_directors' key with nested player_profile objects.

    Attributes:
        count: Total number of country directors
        country_directors: List of country directors with nested player profiles
    """

    count: int | None = None
    country_directors: list[CountryDirector] = Field(default_factory=list)
