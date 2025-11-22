"""Series resource client - main entry point.

Provides callable client for series operations.
"""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from ifpa_api.core.base import BaseResourceClient
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.models.series import SeriesListResponse, SeriesStandingsResponse

from .context import _SeriesContext

if TYPE_CHECKING:
    from ifpa_api.resources.series.query_builder import SeriesQueryBuilder


class SeriesClient(BaseResourceClient):
    """Callable client for series operations.

    Provides both collection-level operations (listing series) and
    series-specific operations through the callable pattern.

    Call this client with a series code to get a context for series-specific
    operations like standings, player cards, and statistics.

    Attributes:
        _http: The HTTP client instance
        _validate_requests: Whether to validate request parameters
    """

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

    def list_series(self, active_only: bool | None = None) -> SeriesListResponse:
        """List all available series (preferred name for consistency).

        Args:
            active_only: If True, only return active series. If False or None, return all.

        Returns:
            Response containing list of series

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Get all series
            all_series = client.series.list_series()
            for s in all_series.series:
                print(f"{s.series_code}: {s.series_name}")

            # Get only active series
            active = client.series.list_series(active_only=True)
            ```
        """
        params = {}
        if active_only is not None:
            params["active_only"] = str(active_only).lower()

        response = self._http._request("GET", "/series/list", params=params)
        return SeriesListResponse.model_validate(response)

    def list(self, active_only: bool | None = None) -> SeriesListResponse:
        """DEPRECATED: List all available series.

        .. deprecated:: 4.0.0
           Use :meth:`list_series` instead for naming consistency.
           This method will be removed in v5.0.0.

        Args:
            active_only: If True, only return active series

        Returns:
            Response containing list of series

        Example:
            ```python
            # Old way (deprecated)
            series = client.series.list()

            # New way (preferred)
            series = client.series.list_series()
            ```
        """
        warnings.warn(
            "The .list() method is deprecated. "
            "Use .list_series() instead for naming consistency. "
            "This method will be removed in v5.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.list_series(active_only)

    def get(self, series_code: str) -> SeriesStandingsResponse:
        """Get series standings by code.

        Args:
            series_code: The series code identifier (e.g., "NACS", "PAPA")

        Returns:
            SeriesStandingsResponse with overall series standings

        Raises:
            IfpaApiError: If series not found (404) or other API error

        Example:
            ```python
            standings = client.series.get("NACS")
            print(f"Total players: {len(standings.standings)}")
            ```
        """
        return self(series_code).standings()

    def get_or_none(self, series_code: str) -> SeriesStandingsResponse | None:
        """Get series standings by code, returning None if not found.

        Args:
            series_code: The series code identifier (e.g., "NACS", "PAPA")

        Returns:
            SeriesStandingsResponse if found, None if not found (404)

        Raises:
            IfpaApiError: For API errors other than 404

        Example:
            ```python
            standings = client.series.get_or_none("NACS")
            if standings:
                print(f"Found {len(standings.standings)} players")
            else:
                print("Series not found")
            ```
        """
        try:
            return self.get(series_code)
        except IfpaApiError as e:
            if e.status_code == 404:
                return None
            raise

    def exists(self, series_code: str) -> bool:
        """Check if series exists.

        Args:
            series_code: The series code identifier (e.g., "NACS", "PAPA")

        Returns:
            True if series exists, False otherwise

        Example:
            ```python
            if client.series.exists("NACS"):
                print("Series exists!")
            ```
        """
        return self.get_or_none(series_code) is not None

    def search(self, name: str = "") -> SeriesQueryBuilder:
        """Search for series by name with optional filters.

        Note: The Series API only provides a list endpoint, so name filtering
        is performed client-side. Use .active_only() for server-side filtering.

        Args:
            name: Name or partial name to search for (optional)

        Returns:
            Query builder for chaining filters

        Example:
            ```python
            # Search by name
            results = client.series.search("Circuit").get()

            # Active series only
            active = client.series.search().active_only().get()

            # Combined filters
            results = client.series.search("North American").active_only().get()

            # Use query builder methods
            nacs = client.series.search("NACS").first()

            # Query reuse
            base = client.series.search().active_only()
            circuit = base.name("Circuit").get()
            papa = base.name("PAPA").get()
            ```
        """
        from ifpa_api.resources.series.query_builder import SeriesQueryBuilder

        builder = SeriesQueryBuilder(self._http)
        if name:
            return builder.name(name)
        return builder
