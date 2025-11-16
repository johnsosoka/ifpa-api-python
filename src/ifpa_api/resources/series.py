"""Series resource client and handle.

Provides access to tournament series information, standings, player cards,
and statistics.
"""

from typing import TYPE_CHECKING

from ifpa_api.models.series import (
    RegionRepsResponse,
    SeriesListResponse,
    SeriesPlayerCard,
    SeriesRegionsResponse,
    SeriesRegionStandingsResponse,
    SeriesStandingsResponse,
    SeriesStats,
    SeriesTournamentsResponse,
)

if TYPE_CHECKING:
    from ifpa_api.http import _HttpClient


class _SeriesContext:
    """Internal context for series-specific operations.

    This class provides methods for accessing information about a specific
    series identified by its series code. It is returned by calling
    SeriesClient with a series code.

    Attributes:
        _http: The HTTP client instance
        _series_code: The series code identifier
        _validate_requests: Whether to validate request parameters
    """

    def __init__(self, http: "_HttpClient", series_code: str, validate_requests: bool) -> None:
        """Initialize a series context.

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
        """Get overall standings for this series across all regions.

        Returns an overview of standings for all regions in the series, including
        the current leader and prize fund for each region.

        Args:
            start_pos: Starting position for pagination (currently unused by API)
            count: Number of results to return (currently unused by API)

        Returns:
            Overall standings with region overviews

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            standings = client.series("NACS").standings()
            print(f"Series: {standings.series_code} ({standings.year})")
            print(f"Total Prize Fund: ${standings.championship_prize_fund}")
            for region in standings.overall_results:
                print(f"{region.region_name}: {region.player_count} players")
                print(f"  Leader: {region.current_leader['player_name']}")
            ```
        """
        params = {}
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count

        response = self._http._request(
            "GET", f"/series/{self._series_code}/overall_standings", params=params
        )
        return SeriesStandingsResponse.model_validate(response)

    def region_standings(
        self,
        region_code: str,
        start_pos: int | None = None,
        count: int | None = None,
    ) -> SeriesRegionStandingsResponse:
        """Get detailed player standings for a specific region in this series.

        Returns the full standings list with individual player rankings for
        a specific region.

        Args:
            region_code: Region code (e.g., "OH", "IL", "CA")
            start_pos: Starting position for pagination
            count: Number of results to return

        Returns:
            Detailed region standings with player rankings

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            standings = client.series("NACS").region_standings("OH")
            print(f"Region: {standings.region_name}")
            print(f"Prize Fund: ${standings.prize_fund}")
            for player in standings.standings[:10]:
                print(f"{player.series_rank}. {player.player_name}: {player.wppr_points} pts")
            ```
        """
        params: dict[str, str | int] = {"region_code": region_code}
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count

        response = self._http._request(
            "GET", f"/series/{self._series_code}/standings", params=params
        )
        return SeriesRegionStandingsResponse.model_validate(response)

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
            card = client.series("PAPA").player_card(12345, "OH")
            print(f"Position: {card.current_position}")
            print(f"Points: {card.total_points}")

            # Get card for specific year
            card_2023 = client.series("PAPA").player_card(12345, "OH", year=2023)
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

    def regions(self, region_code: str, year: int) -> SeriesRegionsResponse:
        """Get active regions in this series for a specific year.

        Note: The region_code parameter is required by the API but the endpoint
        returns all active regions for the specified year regardless of the
        region_code value provided.

        Args:
            region_code: Region code (e.g., "OH", "IL", "CA") - required by API
                but not used for filtering
            year: Year to fetch regions for

        Returns:
            List of all active regions for the specified year

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            regions = client.series("NACS").regions("OH", 2025)
            for region in regions.active_regions:
                print(f"{region.region_name} ({region.region_code})")
            ```
        """
        params = {"region_code": region_code, "year": year}
        response = self._http._request("GET", f"/series/{self._series_code}/regions", params=params)
        return SeriesRegionsResponse.model_validate(response)

    def stats(self, region_code: str) -> SeriesStats:
        """Get statistics for a specific region in this series.

        Args:
            region_code: Region code (e.g., "OH", "IL", "CA")

        Returns:
            Series statistics including totals and averages for the region

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            stats = client.series("NACS").stats("OH")
            print(f"Total Events: {stats.total_events}")
            print(f"Average Event Size: {stats.average_event_size}")
            ```
        """
        params = {"region_code": region_code}
        response = self._http._request("GET", f"/series/{self._series_code}/stats", params=params)
        return SeriesStats.model_validate(response)

    def tournaments(self, region_code: str) -> SeriesTournamentsResponse:
        """Get tournaments for a specific region in this series.

        Args:
            region_code: Region code (e.g., "OH", "IL", "CA")

        Returns:
            List of tournaments in the specified region

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            tournaments = client.series("NACS").tournaments("OH")
            for tournament in tournaments.tournaments:
                print(f"{tournament.tournament_name} on {tournament.event_date}")
            ```
        """
        params = {"region_code": region_code}
        response = self._http._request(
            "GET", f"/series/{self._series_code}/tournaments", params=params
        )
        return SeriesTournamentsResponse.model_validate(response)

    def region_reps(self) -> RegionRepsResponse:
        """Get region representatives for this series.

        Returns:
            List of region representatives

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            reps = client.series("PAPA").region_reps()
            for rep in reps.representative:
                print(f"{rep.region_name}: {rep.name} (Player #{rep.player_id})")
            ```
        """
        response = self._http._request("GET", f"/series/{self._series_code}/region_reps")
        return RegionRepsResponse.model_validate(response)


class SeriesClient:
    """Callable client for series operations.

    Provides both collection-level operations (listing series) and
    series-specific operations through the callable pattern.

    Call this client with a series code to get a context for series-specific
    operations like standings, player cards, and statistics.

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

    def __call__(self, series_code: str) -> _SeriesContext:
        """Get a context for a specific series.

        Args:
            series_code: The series code identifier (e.g., "NACS", "PAPA")

        Returns:
            _SeriesContext instance for accessing series-specific operations

        Example:
            ```python
            # Get series standings
            standings = client.series("NACS").standings()

            # Get player's series card
            card = client.series("PAPA").player_card(12345, "OH")

            # Get region standings
            region = client.series("NACS").region_standings("OH")
            ```
        """
        return _SeriesContext(self._http, series_code, self._validate_requests)

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
