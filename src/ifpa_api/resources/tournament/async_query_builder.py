"""Fluent async query builder for tournament search operations."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self

from ifpa_api.core.async_base import LocationFiltersMixin, PaginationMixin
from ifpa_api.core.async_query_builder import AsyncQueryBuilder
from ifpa_api.core.exceptions import IfpaClientValidationError
from ifpa_api.models.tournaments import TournamentSearchResponse, TournamentSearchResult

if TYPE_CHECKING:
    from ifpa_api.core.async_http import _AsyncHttpClient


class AsyncTournamentQueryBuilder(
    AsyncQueryBuilder[TournamentSearchResponse],
    LocationFiltersMixin,
    PaginationMixin,
):
    """Fluent async query builder for tournament search operations.

    This class implements an immutable query builder pattern for searching tournaments
    asynchronously. Each method returns a new instance, allowing safe query composition
    and reuse.

    Attributes:
        _http: The async HTTP client instance
        _params: Accumulated query parameters

    Example:
        ```python
        # Simple query
        async with AsyncIfpaClient() as client:
            results = await client.tournament.search("PAPA").get()

        # Chained filters with immutability
        async with AsyncIfpaClient() as client:
            us_query = client.tournament.search().country("US")
            wa_tournaments = await us_query.state("WA").limit(25).get()
            or_tournaments = await us_query.state("OR").limit(25).get()  # base unchanged!

        # Complex query with date range
        async with AsyncIfpaClient() as client:
            results = await (client.tournament.search("Championship")
                .country("US")
                .date_range("2024-01-01", "2024-12-31")
                .tournament_type("open")
                .limit(50)
                .get())
        ```
    """

    def __init__(self, http: _AsyncHttpClient) -> None:
        """Initialize the async tournament query builder.

        Args:
            http: The async HTTP client instance
        """
        super().__init__()
        self._http = http

    def query(self, name: str) -> Self:
        """Set the tournament name to search for.

        Args:
            name: Tournament name to search for (partial match)

        Returns:
            New AsyncTournamentQueryBuilder instance with the name parameter set

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                results = await client.tournament.search("PAPA").get()
            ```
        """
        clone = self._clone()
        clone._params["name"] = name
        return clone

    def date_range(self, start_date: str | None, end_date: str | None) -> Self:
        """Filter by date range.

        Both start_date and end_date are required. Dates should be in YYYY-MM-DD format.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            New AsyncTournamentQueryBuilder instance with date range filter applied

        Raises:
            ValueError: If start_date or end_date is None
            IfpaClientValidationError: If dates are not in YYYY-MM-DD format

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                results = await (client.tournament.search()
                    .country("US")
                    .date_range("2024-01-01", "2024-12-31")
                    .get())
            ```
        """
        # Both dates must be provided together
        if start_date is None or end_date is None:
            raise ValueError("Both start_date and end_date must be provided")

        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(date_pattern, start_date):
            raise IfpaClientValidationError(
                f"start_date must be in YYYY-MM-DD format, got: {start_date}"
            )
        if not re.match(date_pattern, end_date):
            raise IfpaClientValidationError(
                f"end_date must be in YYYY-MM-DD format, got: {end_date}"
            )

        clone = self._clone()
        clone._params["start_date"] = start_date
        clone._params["end_date"] = end_date
        return clone

    def tournament_type(self, tournament_type: str) -> Self:
        """Filter by tournament type.

        Args:
            tournament_type: Tournament type (e.g., "open", "women", "youth")

        Returns:
            New AsyncTournamentQueryBuilder instance with tournament type filter applied

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                results = await client.tournament.search().tournament_type("women").get()
            ```
        """
        clone = self._clone()
        clone._params["tournament_type"] = tournament_type
        return clone

    async def get(self) -> TournamentSearchResponse:
        """Execute the query and return results.

        Validates that if either start_date or end_date is present, both must be present.

        Returns:
            TournamentSearchResponse containing matching tournaments

        Raises:
            IfpaClientValidationError: If only one of start_date or end_date is present
            IfpaApiError: If the API request fails

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                results = await client.tournament.search("Championship").country("US").get()
                print(f"Found {len(results.tournaments)} tournaments")
                for tournament in results.tournaments:
                    print(f"{tournament.tournament_name} on {tournament.event_date}")
            ```
        """
        # Validate date range: both must be present or both must be absent
        has_start = "start_date" in self._params
        has_end = "end_date" in self._params
        if has_start != has_end:
            raise IfpaClientValidationError(
                "start_date and end_date must be provided together. "
                "The IFPA API requires both dates or neither. "
                f"Current params: start_date={'present' if has_start else 'absent'}, "
                f"end_date={'present' if has_end else 'absent'}"
            )

        response = await self._http._request("GET", "/tournament/search", params=self._params)
        return TournamentSearchResponse.model_validate(response)

    async def first(self) -> TournamentSearchResult:
        """Get the first result from the search.

        This is a convenience method that executes the query and returns
        only the first result.

        Returns:
            The first search result

        Raises:
            IfpaApiError: If the API request fails
            IndexError: If the search returns no results

        Example:
            ```python
            # Get first tournament matching search
            async with AsyncIfpaClient() as client:
                tournament = await client.tournament.search("PAPA").first()

            # With filters
            async with AsyncIfpaClient() as client:
                tournament = await (client.tournament.search("Championship")
                    .country("US")
                    .first())
            ```
        """
        results = await self.get()
        if not results.tournaments:
            raise IndexError("Search returned no results")
        return results.tournaments[0]

    async def first_or_none(self) -> TournamentSearchResult | None:
        """Get the first result from the search, or None if no results.

        This is a convenience method that executes the query and returns
        the first result, or None if the search returns no results.

        Returns:
            The first search result, or None if no results found

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                tournament = await client.tournament.search("PAPA").first_or_none()
                if tournament:
                    print(f"Found: {tournament.tournament_name}")
                else:
                    print("No results found")
            ```
        """
        try:
            return await self.first()
        except IndexError:
            return None
