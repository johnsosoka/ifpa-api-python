"""Tournament resource client with callable pattern.

Provides access to tournament information, results, formats, and submissions.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self

from ifpa_api.core.base import (
    BaseResourceClient,
    BaseResourceContext,
    LocationFiltersMixin,
    PaginationMixin,
)
from ifpa_api.exceptions import IfpaClientValidationError
from ifpa_api.models.tournaments import (
    RelatedTournamentsResponse,
    Tournament,
    TournamentFormatsListResponse,
    TournamentFormatsResponse,
    TournamentLeagueResponse,
    TournamentResultsResponse,
    TournamentSearchResponse,
    TournamentSubmissionsResponse,
)
from ifpa_api.query_builder import QueryBuilder

if TYPE_CHECKING:
    from ifpa_api.http import _HttpClient


# ============================================================================
# Tournament Context - Individual Tournament Operations
# ============================================================================


class _TournamentContext(BaseResourceContext[int | str]):
    """Context for interacting with a specific tournament.

    This internal class provides resource-specific methods for a tournament
    identified by its tournament ID. Instances are returned by calling
    TournamentClient with a tournament ID.

    Attributes:
        _http: The HTTP client instance
        _resource_id: The tournament's unique identifier
        _validate_requests: Whether to validate request parameters
    """

    def details(self) -> Tournament:
        """Get detailed information about this tournament.

        Returns:
            Tournament information including venue, date, and details

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            tournament = client.tournament(12345).details()
            print(f"Tournament: {tournament.tournament_name}")
            print(f"Players: {tournament.player_count}")
            print(f"Date: {tournament.event_date}")
            ```
        """
        response = self._http._request("GET", f"/tournament/{self._resource_id}")
        return Tournament.model_validate(response)

    def results(self) -> TournamentResultsResponse:
        """Get results for this tournament.

        Returns:
            List of player results and standings

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            results = client.tournament(12345).results()
            for result in results.results:
                print(f"{result.position}. {result.player_name}: {result.wppr_points} WPPR")
            ```
        """
        response = self._http._request("GET", f"/tournament/{self._resource_id}/results")
        return TournamentResultsResponse.model_validate(response)

    def formats(self) -> TournamentFormatsResponse:
        """Get format information for this tournament.

        Returns:
            List of formats used in the tournament

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            formats = client.tournament(12345).formats()
            for fmt in formats.formats:
                print(f"Format: {fmt.format_name}")
                print(f"Rounds: {fmt.rounds}")
            ```
        """
        response = self._http._request("GET", f"/tournament/{self._resource_id}/formats")
        return TournamentFormatsResponse.model_validate(response)

    def league(self) -> TournamentLeagueResponse:
        """Get league information for this tournament (if applicable).

        Returns:
            League session data and format information

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            league = client.tournament(12345).league()
            print(f"Total sessions: {league.total_sessions}")
            for session in league.sessions:
                print(f"{session.session_date}: {session.player_count} players")
            ```
        """
        response = self._http._request("GET", f"/tournament/{self._resource_id}/league")
        return TournamentLeagueResponse.model_validate(response)

    def submissions(self) -> TournamentSubmissionsResponse:
        """Get submission information for this tournament.

        Returns:
            List of tournament submissions

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            submissions = client.tournament(12345).submissions()
            for submission in submissions.submissions:
                print(f"{submission.submission_date}: {submission.status}")
            ```
        """
        response = self._http._request("GET", f"/tournament/{self._resource_id}/submissions")
        return TournamentSubmissionsResponse.model_validate(response)

    def related(self) -> RelatedTournamentsResponse:
        """Get tournaments related to this tournament.

        Returns tournaments that are part of the same tournament series or held at
        the same venue. This is useful for finding recurring events and historical
        data for tournament series.

        Returns:
            RelatedTournamentsResponse with list of related tournaments.

        Raises:
            IfpaApiError: If the API request fails.

        Example:
            ```python
            # Get related tournaments
            tournament = client.tournament(12345).details()
            related = client.tournament(12345).related()

            print(f"Found {len(related.tournament)} related tournaments")
            for t in related.tournament:
                print(f"  {t.event_start_date}: {t.tournament_name}")
                if t.winner:
                    print(f"    Winner: {t.winner.name}")
            ```
        """
        response = self._http._request("GET", f"/tournament/{self._resource_id}/related")
        return RelatedTournamentsResponse.model_validate(response)


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


# ============================================================================
# Tournament Resource Client - Main Entry Point
# ============================================================================


class TournamentClient(BaseResourceClient):
    """Callable client for tournament operations.

    This client provides both collection-level methods (list_formats, league_results) and
    resource-level access via the callable pattern. Call with a tournament ID to get
    a context for tournament-specific operations.

    Attributes:
        _http: The HTTP client instance
        _validate_requests: Whether to validate request parameters

    Example:
        ```python
        # Collection-level operations
        results = client.tournament.query("PAPA").get()
        formats = client.tournament.list_formats()

        # Resource-level operations
        tournament = client.tournament(12345).details()
        results = client.tournament(12345).results()
        formats = client.tournament(12345).formats()
        ```
    """

    def __call__(self, tournament_id: int | str) -> _TournamentContext:
        """Get a context for a specific tournament.

        Args:
            tournament_id: The tournament's unique identifier

        Returns:
            _TournamentContext instance for accessing tournament-specific operations

        Example:
            ```python
            # Get tournament context and access methods
            tournament = client.tournament(12345).details()
            results = client.tournament(12345).results()
            league = client.tournament(12345).league()
            ```
        """
        return _TournamentContext(self._http, tournament_id, self._validate_requests)

    def query(self, name: str = "") -> TournamentQueryBuilder:
        """Create a fluent query builder for searching tournaments.

        This is the recommended way to search for tournaments, providing a type-safe
        and composable interface. The returned builder can be reused and composed
        thanks to its immutable pattern.

        Args:
            name: Optional tournament name to search for (can also be set via .query() on builder)

        Returns:
            TournamentQueryBuilder instance for building the search query

        Example:
            ```python
            # Simple name search
            results = client.tournament.query("PAPA").get()

            # Chained filters
            results = (client.tournament.query("Championship")
                .country("US")
                .state("WA")
                .limit(25)
                .get())

            # Query reuse (immutable pattern)
            us_base = client.tournament.query().country("US")
            wa_tournaments = us_base.state("WA").get()
            or_tournaments = us_base.state("OR").get()  # base unchanged!

            # Empty query to start with filters
            results = (client.tournament.query()
                .date_range("2024-01-01", "2024-12-31")
                .tournament_type("women")
                .get())
            ```
        """
        builder = TournamentQueryBuilder(self._http)
        if name:
            return builder.query(name)
        return builder

    def list_formats(self) -> TournamentFormatsListResponse:
        """Get list of all available tournament format types.

        Returns a comprehensive list of format types used for tournament qualifying
        and finals rounds. This reference data is useful for understanding format
        options when creating or searching for tournaments.

        Returns:
            TournamentFormatsListResponse with qualifying and finals format lists.

        Raises:
            IfpaApiError: If the API request fails.

        Example:
            ```python
            # Get all tournament formats
            formats = client.tournament.list_formats()

            print(f"Qualifying formats ({len(formats.qualifying_formats)}):")
            for fmt in formats.qualifying_formats:
                print(f"  {fmt.format_id}: {fmt.name}")

            print(f"\\nFinals formats ({len(formats.finals_formats)}):")
            for fmt in formats.finals_formats:
                print(f"  {fmt.format_id}: {fmt.name}")

            # Find a specific format
            swiss = next(
                f for f in formats.qualifying_formats
                if "swiss" in f.name.lower()
            )
            print(f"\\nSwiss format ID: {swiss.format_id}")
            ```
        """
        response = self._http._request("GET", "/tournament/formats")
        return TournamentFormatsListResponse.model_validate(response)
