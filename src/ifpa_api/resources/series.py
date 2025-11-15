"""Series resource client and handle.

Provides access to tournament series information, standings, player cards,
and statistics.
"""

from typing import TYPE_CHECKING

from ifpa_api.models.series import (
    RegionRepsResponse,
    SeriesListResponse,
    SeriesOverview,
    SeriesPlayerCard,
    SeriesRegionsResponse,
    SeriesRules,
    SeriesScheduleResponse,
    SeriesStandingsResponse,
    SeriesStats,
)

if TYPE_CHECKING:
    from ifpa_api.http import _HttpClient


class SeriesHandle:
    """Handle for interacting with a specific tournament series.

    This class provides methods for accessing information about a specific
    series identified by its series code.

    Attributes:
        _http: The HTTP client instance
        _series_code: The series code identifier
        _validate_requests: Whether to validate request parameters
    """

    def __init__(self, http: "_HttpClient", series_code: str, validate_requests: bool) -> None:
        """Initialize a series handle.

        Args:
            http: The HTTP client instance
            series_code: The series code identifier
            validate_requests: Whether to validate request parameters
        """
        self._http = http
        self._series_code = series_code
        self._validate_requests = validate_requests

    def standings(
        self,
        start_pos: int | None = None,
        count: int | None = None,
    ) -> SeriesStandingsResponse:
        """Get current standings for this series.

        Args:
            start_pos: Starting position for pagination
            count: Number of results to return

        Returns:
            List of player standings

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            standings = client.series("PAPA").standings(start_pos=0, count=50)
            for entry in standings.standings:
                print(f"{entry.position}. {entry.player_name}: {entry.points} pts")
            ```
        """
        params = {}
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count

        response = self._http._request(
            "GET", f"/series/{self._series_code}/standings", params=params
        )
        return SeriesStandingsResponse.model_validate(response)

    def player_card(
        self,
        player_id: int | str,
        region_code: str,
        year: int | None = None,
    ) -> SeriesPlayerCard:
        """Get a player's card for this series.

        Args:
            player_id: The player's unique identifier
            region_code: Region code (e.g., "OH", "IL")
            year: Year to fetch card for (defaults to current year if not specified)

        Returns:
            Player's series card with event results and statistics

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Get current year card for player in Ohio region
            card = client.series_handle("PAPA").player_card(12345, "OH")
            print(f"Position: {card.current_position}")
            print(f"Points: {card.total_points}")

            # Get card for specific year
            card_2023 = client.series_handle("PAPA").player_card(12345, "OH", year=2023)
            for event in card_2023.events:
                print(f"{event.tournament_name}: {event.points_earned} pts")
            ```
        """
        params: dict[str, str | int] = {"region_code": region_code}
        if year is not None:
            params["year"] = int(year)

        response = self._http._request(
            "GET", f"/series/{self._series_code}/player_card/{player_id}", params=params
        )
        return SeriesPlayerCard.model_validate(response)

    def overview(self) -> SeriesOverview:
        """Get overview information for this series.

        Returns:
            Series overview with description and statistics

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            overview = client.series("PAPA").overview()
            print(f"Series: {overview.series_name}")
            print(f"Total Events: {overview.total_events}")
            print(f"Total Players: {overview.total_players}")
            ```
        """
        response = self._http._request("GET", f"/series/{self._series_code}/overview")
        return SeriesOverview.model_validate(response)

    def regions(self) -> SeriesRegionsResponse:
        """Get regions participating in this series.

        Returns:
            List of regions with player and event counts

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            regions = client.series("PAPA").regions()
            for region in regions.regions:
                print(f"{region.region_name}: {region.player_count} players")
            ```
        """
        response = self._http._request("GET", f"/series/{self._series_code}/regions")
        return SeriesRegionsResponse.model_validate(response)

    def rules(self) -> SeriesRules:
        """Get rules for this series.

        Returns:
            Series rules and scoring system information

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            rules = client.series("PAPA").rules()
            print(f"Scoring System: {rules.scoring_system}")
            print(f"Events Counted: {rules.events_counted}")
            ```
        """
        response = self._http._request("GET", f"/series/{self._series_code}/rules")
        return SeriesRules.model_validate(response)

    def stats(self) -> SeriesStats:
        """Get statistics for this series.

        Returns:
            Series statistics including totals and averages

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            stats = client.series("PAPA").stats()
            print(f"Total Events: {stats.total_events}")
            print(f"Average Event Size: {stats.average_event_size}")
            ```
        """
        response = self._http._request("GET", f"/series/{self._series_code}/stats")
        return SeriesStats.model_validate(response)

    def schedule(self) -> SeriesScheduleResponse:
        """Get schedule for this series.

        Returns:
            List of scheduled events

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            schedule = client.series("PAPA").schedule()
            for event in schedule.events:
                print(f"{event.event_date}: {event.event_name} in {event.city}")
            ```
        """
        response = self._http._request("GET", f"/series/{self._series_code}/schedule")
        return SeriesScheduleResponse.model_validate(response)

    def region_reps(self) -> RegionRepsResponse:
        """Get region representatives for this series.

        Returns:
            List of region representatives

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            reps = client.series_handle("PAPA").region_reps()
            for rep in reps.representative:
                print(f"{rep.region_name}: {rep.name} (Player #{rep.player_id})")
            ```
        """
        response = self._http._request("GET", f"/series/{self._series_code}/region_reps")
        return RegionRepsResponse.model_validate(response)


class SeriesClient:
    """Client for series collection-level operations.

    This client provides methods for listing and accessing tournament series.

    Attributes:
        _http: The HTTP client instance
        _validate_requests: Whether to validate request parameters
    """

    def __init__(self, http: "_HttpClient", validate_requests: bool) -> None:
        """Initialize the series client.

        Args:
            http: The HTTP client instance
            validate_requests: Whether to validate request parameters
        """
        self._http = http
        self._validate_requests = validate_requests

    def list(self, active_only: bool | None = None) -> SeriesListResponse:
        """List all available series.

        Args:
            active_only: Filter to only active series

        Returns:
            List of series

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Get all series
            series = client.series.list()
            for s in series.series:
                print(f"{s.series_code}: {s.series_name}")

            # Get only active series
            active_series = client.series.list(active_only=True)
            ```
        """
        params = {}
        if active_only is not None:
            params["active_only"] = str(active_only).lower()

        response = self._http._request("GET", "/series/list", params=params)
        return SeriesListResponse.model_validate(response)
