"""Series resource client - main entry point.

Provides callable client for series operations.
"""

from ifpa_api.core.base import BaseResourceClient
from ifpa_api.models.series import SeriesListResponse

from .context import _SeriesContext


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
