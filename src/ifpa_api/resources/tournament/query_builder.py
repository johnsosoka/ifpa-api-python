"""Tournament query builder with fluent search interface.

Implements an immutable query builder pattern for searching tournaments.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self

from ifpa_api.core.base import LocationFiltersMixin, PaginationMixin
from ifpa_api.core.exceptions import IfpaClientValidationError
from ifpa_api.core.query_builder import QueryBuilder
from ifpa_api.models.tournaments import TournamentSearchResponse

if TYPE_CHECKING:
    from ifpa_api.core.http import _HttpClient


# ============================================================================
# Tournament Query Builder - Fluent Search Interface
# ============================================================================


class TournamentQueryBuilder(
    QueryBuilder[TournamentSearchResponse], LocationFiltersMixin, PaginationMixin
):
    """Fluent query builder for tournament search operations.

    This class implements an immutable query builder pattern for searching tournaments.
    Each method returns a new instance, allowing safe query composition and reuse.

    Inherits location filtering (country, state, city) from LocationFiltersMixin
    and pagination (limit, offset) from PaginationMixin.

    Attributes:
        _http: The HTTP client instance
        _params: Accumulated query parameters

    Example:
        ```python
        # Simple query
        results = client.tournament.query("PAPA").get()

        # Chained filters with immutability
        us_query = client.tournament.query().country("US")
        wa_tournaments = us_query.state("WA").limit(25).get()
        or_tournaments = us_query.state("OR").limit(25).get()  # base unchanged!

        # Complex query with date range
        results = (client.tournament.query("Championship")
            .country("US")
            .date_range("2024-01-01", "2024-12-31")
            .tournament_type("open")
            .limit(50)
            .get())
        ```
    """

    def __init__(self, http: _HttpClient) -> None:
        """Initialize the tournament query builder.

        Args:
            http: The HTTP client instance
        """
        super().__init__()
        self._http = http

    def query(self, name: str) -> Self:
        """Set the tournament name to search for.

        Args:
            name: Tournament name to search for (partial match)

        Returns:
            New TournamentQueryBuilder instance with the name parameter set

        Example:
            ```python
            results = client.tournament.query("PAPA").get()
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
            New TournamentQueryBuilder instance with date range filter applied

        Raises:
            ValueError: If start_date or end_date is None
            IfpaClientValidationError: If dates are not in YYYY-MM-DD format

        Example:
            ```python
            results = (client.tournament.query()
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
            New TournamentQueryBuilder instance with tournament type filter applied

        Example:
            ```python
            results = client.tournament.query().tournament_type("women").get()
            ```
        """
        clone = self._clone()
        clone._params["tournament_type"] = tournament_type
        return clone

    def get(self) -> TournamentSearchResponse:
        """Execute the query and return results.

        Validates that if either start_date or end_date is present, both must be present.

        Returns:
            TournamentSearchResponse containing matching tournaments

        Raises:
            IfpaClientValidationError: If only one of start_date or end_date is present
            IfpaApiError: If the API request fails

        Example:
            ```python
            results = client.tournament.query("Championship").country("US").get()
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

        response = self._http._request("GET", "/tournament/search", params=self._params)
        return TournamentSearchResponse.model_validate(response)
