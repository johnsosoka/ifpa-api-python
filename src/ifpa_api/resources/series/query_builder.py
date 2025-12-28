"""Fluent query builder for series search operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from typing import Self

from ifpa_api.core.query_builder import QueryBuilder
from ifpa_api.models.series import SeriesListResponse

if TYPE_CHECKING:
    from ifpa_api.core.http import _HttpClient


class SeriesQueryBuilder(QueryBuilder[SeriesListResponse]):
    """Fluent query builder for series search operations.

    The Series API only provides a list endpoint, so this builder performs
    client-side name filtering on the results. Server-side filtering is available
    for the active_only parameter.

    This class implements an immutable query builder pattern for searching series.
    Each method returns a new instance, allowing safe query composition and reuse.

    Attributes:
        _http: The HTTP client instance
        _params: Accumulated query parameters

    Example:
        ```python
        # Search by name (client-side filtering)
        series = client.series.search("North American").get()

        # Active series only (server-side filtering)
        active = client.series.search().active_only().get()

        # Combined filters
        results = client.series.search("Circuit").active_only().get()

        # Query reuse with immutable pattern
        base_query = client.series.search()
        active_series = base_query.active_only().get()
        all_series = base_query.get()  # base unchanged!
        ```
    """

    def __init__(self, http: _HttpClient) -> None:
        """Initialize the series query builder.

        Args:
            http: The HTTP client instance
        """
        super().__init__()
        self._http = http

    def name(self, name: str) -> Self:
        """Filter series by name (case-insensitive, client-side).

        This filter is applied client-side after fetching results from the API,
        matching against both series_name and series_code fields.

        Args:
            name: Name or partial name to search for

        Returns:
            New SeriesQueryBuilder instance with the name filter applied

        Raises:
            ValueError: If name() called multiple times in same chain

        Example:
            ```python
            # Find series with "Circuit" in name
            series = client.series.search("Circuit").get()

            # Also matches series codes
            nacs = client.series.search("NACS").get()
            ```
        """
        clone = self._clone()
        if "name" in clone._params:
            raise ValueError(
                f"name() called multiple times in query chain. "
                f"Previous value: '{clone._params['name']}', "
                f"Attempted value: '{name}'. "
                f"This is likely a mistake. Create a new query to change filters."
            )
        clone._params["name"] = name
        return clone

    def active_only(self, active: bool = True) -> Self:
        """Filter to only active or inactive series (server-side).

        This filter is applied server-side by the API.

        Args:
            active: If True, return only active series. If False, return only inactive.

        Returns:
            New SeriesQueryBuilder instance with the active filter applied

        Raises:
            ValueError: If active_only() called multiple times in same chain

        Example:
            ```python
            # Get only active series
            active = client.series.search().active_only().get()

            # Get only inactive series
            inactive = client.series.search().active_only(False).get()
            ```
        """
        clone = self._clone()
        if "active_only" in clone._params:
            raise ValueError(
                f"active_only() called multiple times in query chain. "
                f"Previous value: '{clone._params['active_only']}', "
                f"Attempted value: '{active}'. "
                f"This is likely a mistake. Create a new query to change filters."
            )
        clone._params["active_only"] = active
        return clone

    def get(self) -> SeriesListResponse:
        """Execute the query and return filtered results.

        Returns:
            Response containing filtered series list

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Execute simple search
            results = client.series.search("North").get()

            # Execute with filters
            results = client.series.search("Circuit").active_only().get()
            ```
        """
        # Build API request params (only active_only is sent to API)
        api_params = {}
        if "active_only" in self._params:
            api_params["active_only"] = str(self._params["active_only"]).lower()

        # Call API
        response = self._http._request("GET", "/series/list", params=api_params)
        result = SeriesListResponse.model_validate(response)

        # Client-side name filtering if specified
        if "name" in self._params:
            name_filter = self._params["name"].lower()
            result.series = [
                s
                for s in result.series
                if name_filter in s.series_name.lower() or name_filter in s.series_code.lower()
            ]

        return result

    def _extract_results(self, response: SeriesListResponse) -> list[Any]:
        """Extract result list from response for .iterate() and .get_all().

        Args:
            response: The series list response

        Returns:
            List of series from the response
        """
        return response.series
