"""Series-related Pydantic models.

Models for tournament series including standings, player cards, and statistics.
"""

from typing import Any

from pydantic import Field

from ifpa_api.models.common import IfpaBaseModel


class Series(IfpaBaseModel):
    """Tournament series information.

    Attributes:
        series_code: Unique series code/identifier (mapped from 'code')
        series_name: Series name (mapped from 'title')
        description: Series description
        website: Series website URL
        country_code: ISO country code
        start_date: Series start date
        end_date: Series end date
        active: Whether series is currently active
    """

    series_code: str = Field(alias="code")
    series_name: str = Field(alias="title")
    description: str | None = None
    website: str | None = None
    country_code: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    active: bool | None = None


class SeriesListResponse(IfpaBaseModel):
    """Response for series list query.

    Attributes:
        series: List of available series
        total_count: Total number of series
    """

    series: list[Series] = Field(default_factory=list)
    total_count: int | None = None


class SeriesStandingEntry(IfpaBaseModel):
    """Standing entry in a tournament series.

    Attributes:
        position: Current position in standings
        player_id: Unique player identifier
        player_name: Player's full name
        first_name: Player's first name
        last_name: Player's last name
        country_code: ISO country code
        points: Total points earned
        events_played: Number of events participated in
        best_finish: Best finishing position
        average_finish: Average finishing position
        events_counted: Number of events counting toward standings
    """

    position: int
    player_id: int
    player_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    country_code: str | None = None
    points: float | None = None
    events_played: int | None = None
    best_finish: int | None = None
    average_finish: float | None = None
    events_counted: int | None = None


class RegionOverview(IfpaBaseModel):
    """Overview of one region's standings in a series.

    Attributes:
        region_code: Region code (e.g., "AB", "OH")
        region_name: Full region name
        player_count: Total number of players in region (as string)
        unique_player_count: Number of unique players (as string)
        tournament_count: Number of tournaments in region (as string)
        current_leader: Dictionary with player_id and player_name of current leader
        prize_fund: Prize fund amount for this region
    """

    region_code: str
    region_name: str
    player_count: str
    unique_player_count: str | None = None
    tournament_count: str | None = None
    current_leader: dict[str, str]
    prize_fund: float


class SeriesStandingsResponse(IfpaBaseModel):
    """Response for series overall standings across all regions.

    This is returned by the /overall_standings endpoint and provides
    an overview of all regions participating in the series.

    Attributes:
        series_code: The series code
        year: Year of the standings
        championship_prize_fund: Total championship prize fund
        overall_results: List of region overviews with standings summary
    """

    series_code: str
    year: int
    championship_prize_fund: float
    overall_results: list[RegionOverview] = Field(default_factory=list)


class RegionStandingEntry(IfpaBaseModel):
    """One player's standing entry in a specific region.

    Attributes:
        series_rank: Player's rank in the region
        player_id: Player's unique identifier
        player_name: Player's full name
        city: City where player is located
        stateprov_code: State or province code
        country_code: ISO country code
        country_name: Full country name
        wppr_points: WPPR points earned in this region
        event_count: Number of events participated in
        win_count: Number of wins
    """

    series_rank: int
    player_id: int
    player_name: str
    city: str | None = None
    stateprov_code: str | None = None
    country_code: str
    country_name: str
    wppr_points: float
    event_count: int
    win_count: int


class SeriesRegionStandingsResponse(IfpaBaseModel):
    """Response for series region-specific standings.

    This is returned by the /standings endpoint when a region_code is provided
    and shows detailed player standings for that specific region.

    Attributes:
        series_code: The series code
        region_code: The region code
        region_name: Full region name
        prize_fund: Prize fund for this region (as string)
        year: Year of the standings
        standings: List of player standings in this region
    """

    series_code: str
    region_code: str
    region_name: str
    prize_fund: str
    year: int
    standings: list[RegionStandingEntry] = Field(default_factory=list)


class SeriesPlayerEvent(IfpaBaseModel):
    """Event result for a player in a series.

    Attributes:
        tournament_id: Unique tournament identifier
        tournament_name: Tournament name
        event_name: Specific event name within tournament
        event_end_date: End date of the event
        wppr_points: WPPR points earned
        region_event_rank: Player's rank in this region event
        event_date: Date of the event (legacy field)
        position: Player's finishing position (legacy field)
        points_earned: Points earned for this event (legacy field)
        player_count: Number of participants (legacy field)
        counting: Whether this event counts toward standings (legacy field)
    """

    tournament_id: int
    tournament_name: str
    event_name: str | None = None
    event_end_date: str | None = None
    wppr_points: float | None = None
    region_event_rank: int | None = None
    # Legacy fields for backwards compatibility
    event_date: str | None = None
    position: int | None = None
    points_earned: float | None = None
    player_count: int | None = None
    counting: bool | None = None


class SeriesPlayerCard(IfpaBaseModel):
    """Player's card for a specific series.

    Attributes:
        series_code: The series code
        region_code: Region code for this card
        year: Year for this card
        player_id: The player's ID
        player_name: The player's name
        player_card: List of event results (mapped from 'player_card' API field)
        current_position: Current position in standings (legacy field)
        total_points: Total points earned (legacy field)
        events: List of event results (legacy field)
        statistics: Additional player statistics for this series (legacy field)
    """

    series_code: str | None = None
    region_code: str | None = None
    year: int | None = None
    player_id: int
    player_name: str | None = None
    player_card: list[SeriesPlayerEvent] = Field(default_factory=list)
    # Legacy fields for backwards compatibility
    current_position: int | None = None
    total_points: float | None = None
    events: list[SeriesPlayerEvent] = Field(default_factory=list)
    statistics: dict[str, Any] | None = None


class SeriesRegion(IfpaBaseModel):
    """Region information for a series.

    Attributes:
        region_code: Region code
        region_name: Region name
        player_count: Number of players from this region
        event_count: Number of events in this region
    """

    region_code: str
    region_name: str
    player_count: int | None = None
    event_count: int | None = None


class SeriesRegionsResponse(IfpaBaseModel):
    """Response for series active regions.

    Attributes:
        series_code: The series code
        year: Year of the regions listing
        active_regions: List of active regions for this series/year
    """

    series_code: str | None = None
    year: int | None = None
    active_regions: list[SeriesRegion] = Field(default_factory=list)


class SeriesStats(IfpaBaseModel):
    """Statistics for a series.

    Attributes:
        series_code: The series code
        total_events: Total number of events
        total_players: Total unique players
        total_participations: Total player participations
        average_event_size: Average number of players per event
        statistics: Additional series statistics
    """

    series_code: str
    total_events: int | None = None
    total_players: int | None = None
    total_participations: int | None = None
    average_event_size: float | None = None
    statistics: dict[str, Any] | None = None


class RegionRepresentative(IfpaBaseModel):
    """Region representative information.

    Attributes:
        player_id: Representative's player ID
        name: Representative's name
        region_code: Region code they represent
        region_name: Full region name
        profile_photo: URL to representative's profile photo
    """

    player_id: int
    name: str
    region_code: str
    region_name: str
    profile_photo: str | None = None


class RegionRepsResponse(IfpaBaseModel):
    """Response for series region representatives.

    Attributes:
        series_code: The series code
        representative: List of region representatives
    """

    series_code: str | None = None
    representative: list[RegionRepresentative] = Field(default_factory=list)


class SeriesTournament(IfpaBaseModel):
    """Tournament in a series region.

    Attributes:
        tournament_id: Unique tournament identifier
        tournament_name: Tournament name
        event_date: Date of the event
        city: City where tournament is held
        stateprov: State or province code
    """

    tournament_id: int
    tournament_name: str
    event_date: str | None = None
    city: str | None = None
    stateprov: str | None = None


class SeriesTournamentsResponse(IfpaBaseModel):
    """Response for series tournaments in a region.

    Attributes:
        series_code: The series code
        region_code: The region code
        tournaments: List of tournaments in the region
    """

    series_code: str | None = None
    region_code: str | None = None
    tournaments: list[SeriesTournament] = Field(default_factory=list)
