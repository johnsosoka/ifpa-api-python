"""Async series resource client - main entry point.

Provides callable async client for series operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ifpa_api.core.async_base import AsyncBaseResourceClient
from ifpa_api.models.series import SeriesListResponse

from .async_context import AsyncSeriesContext

if TYPE_CHECKING:
    pass


class AsyncSeriesClient(AsyncBaseResourceClient):
    """Async callable client for series operations.

    Provides both collection-level operations (listing series) and
    series-specific operations through the callable pattern.

    Call this client with a series code to get a context for series-specific
    operations like standings, player cards, and statistics.

    Attributes:
        _http: The async HTTP client instance
        _validate_requests: Whether to validate request parameters

    Example:
        ```python
        # Get series standings asynchronously
        async with AsyncIfpaClient() as client:
            standings = await client.series("NACS").standings()

        # Get player's series card
        async with AsyncIfpaClient() as client:
            card = await client.series("PAPA").player_card(12345, "OH")

        # Get region standings
        async with AsyncIfpaClient() as client:
            region = await client.series("NACS").region_standings("OH")
        ```
    """

    def __call__(self, series_code: str) -> AsyncSeriesContext:
        """Get a context for a specific series.

        Args:
            series_code: The series code identifier (e.g., "NACS", "PAPA")

        Returns:
            AsyncSeriesContext instance for accessing series-specific operations

        Example:
            ```python
            # Get series standings
            async with AsyncIfpaClient() as client:
                standings = await client.series("NACS").standings()

            # Get player's series card
            async with AsyncIfpaClient() as client:
                card = await client.series("PAPA").player_card(12345, "OH")

            # Get region standings
            async with AsyncIfpaClient() as client:
                region = await client.series("NACS").region_standings("OH")
            ```
        """
        return AsyncSeriesContext(self._http, series_code, self._validate_requests)

    async def list(self, active_only: bool | None = None) -> SeriesListResponse:
        """List all available series asynchronously.

        Args:
            active_only: Filter to only active series

        Returns:
            List of series

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Get all series
            async with AsyncIfpaClient() as client:
                series = await client.series.list()
                for s in series.series:
                    print(f"{s.series_code}: {s.series_name}")

            # Get only active series
            async with AsyncIfpaClient() as client:
                active_series = await client.series.list(active_only=True)
            ```
        """
        params = {}
        if active_only is not None:
            params["active_only"] = str(active_only).lower()

        response = await self._http._request("GET", "/series/list", params=params)
        return SeriesListResponse.model_validate(response)
