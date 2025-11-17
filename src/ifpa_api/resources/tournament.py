"""Tournament resource client with callable pattern.

Provides access to tournament information, results, formats, and submissions.
"""

from __future__ import annotations

import re
import warnings
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from typing import Self

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


class _TournamentContext:
    """Context for interacting with a specific tournament.

    This internal class provides resource-specific methods for a tournament
    identified by its tournament ID. Instances are returned by calling
    TournamentClient with a tournament ID.

    Attributes:
        _http: The HTTP client instance
        _tournament_id: The tournament's unique identifier
        _validate_requests: Whether to validate request parameters
    """

    def __init__(
        self, http: _HttpClient, tournament_id: int | str, validate_requests: bool
    ) -> None:
        """Initialize a tournament context.

        Args:
            http: The HTTP client instance
            tournament_id: The tournament's unique identifier
            validate_requests: Whether to validate request parameters
        """
        self._http = http
        self._tournament_id = tournament_id
        self._validate_requests = validate_requests

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
        response = self._http._request("GET", f"/tournament/{self._tournament_id}")
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
        response = self._http._request("GET", f"/tournament/{self._tournament_id}/results")
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
        response = self._http._request("GET", f"/tournament/{self._tournament_id}/formats")
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
        response = self._http._request("GET", f"/tournament/{self._tournament_id}/league")
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
        response = self._http._request("GET", f"/tournament/{self._tournament_id}/submissions")
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
        response = self._http._request("GET", f"/tournament/{self._tournament_id}/related")
        return RelatedTournamentsResponse.model_validate(response)


class TournamentQueryBuilder(QueryBuilder[TournamentSearchResponse]):
    """Fluent query builder for tournament search operations.

    This class implements an immutable query builder pattern for searching tournaments.
    Each method returns a new instance, allowing safe query composition and reuse.

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

    def city(self, city: str) -> Self:
        """Filter by city.

        Args:
            city: City name

        Returns:
            New TournamentQueryBuilder instance with the city filter applied

        Example:
            ```python
            results = client.tournament.query().city("Portland").get()
            ```
        """
        clone = self._clone()
        clone._params["city"] = city
        return clone

    def state(self, stateprov: str) -> Self:
        """Filter by state/province.

        Args:
            stateprov: State or province code

        Returns:
            New TournamentQueryBuilder instance with the state filter applied

        Example:
            ```python
            results = client.tournament.query().state("OR").get()
            ```
        """
        clone = self._clone()
        clone._params["stateprov"] = stateprov
        return clone

    def country(self, country: str) -> Self:
        """Filter by country.

        Args:
            country: Country code (e.g., "US", "CA")

        Returns:
            New TournamentQueryBuilder instance with the country filter applied

        Example:
            ```python
            results = client.tournament.query().country("US").get()
            ```
        """
        clone = self._clone()
        clone._params["country"] = country
        return clone

    def date_range(self, start_date: str, end_date: str) -> Self:
        """Filter by date range.

        Both start_date and end_date are required. Dates should be in YYYY-MM-DD format.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            New TournamentQueryBuilder instance with date range filter applied

        Raises:
            IfpaClientValidationError: If dates are not in YYYY-MM-DD format

        Example:
            ```python
            results = (client.tournament.query()
                .country("US")
                .date_range("2024-01-01", "2024-12-31")
                .get())
            ```
        """
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

    def offset(self, start_position: int) -> Self:
        """Set pagination offset.

        Args:
            start_position: Starting position for pagination (0-based)

        Returns:
            New TournamentQueryBuilder instance with the offset set

        Example:
            ```python
            # Get second page of results
            results = client.tournament.query("Championship").offset(25).limit(25).get()
            ```
        """
        clone = self._clone()
        clone._params["start_pos"] = start_position
        return clone

    def limit(self, count: int) -> Self:
        """Set maximum number of results to return.

        Args:
            count: Maximum number of results

        Returns:
            New TournamentQueryBuilder instance with the limit set

        Example:
            ```python
            results = client.tournament.query("PAPA").limit(50).get()
            ```
        """
        clone = self._clone()
        clone._params["count"] = count
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


class TournamentClient:
    """Callable client for tournament operations.

    This client provides both collection-level methods (search, list_formats) and
    resource-level access via the callable pattern. Call with a tournament ID to get
    a context for tournament-specific operations.

    Attributes:
        _http: The HTTP client instance
        _validate_requests: Whether to validate request parameters

    Example:
        ```python
        # Collection-level operations
        results = client.tournament.search(name="PAPA")
        formats = client.tournament.list_formats()

        # Resource-level operations
        tournament = client.tournament(12345).details()
        results = client.tournament(12345).results()
        formats = client.tournament(12345).formats()
        ```
    """

    def __init__(self, http: _HttpClient, validate_requests: bool) -> None:
        """Initialize the tournament client.

        Args:
            http: The HTTP client instance
            validate_requests: Whether to validate request parameters
        """
        self._http = http
        self._validate_requests = validate_requests

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

    def search(
        self,
        name: str | None = None,
        city: str | None = None,
        stateprov: str | None = None,
        country: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        tournament_type: str | None = None,
        start_pos: int | str | None = None,
        count: int | str | None = None,
    ) -> TournamentSearchResponse:
        """Search for tournaments.

        .. deprecated:: 0.2.0
            Use :meth:`query` instead for a more fluent and type-safe interface.
            This method will be removed in version 1.0.0.

            Migration example:
                Old: ``client.tournament.search(name="PAPA", country="US")``

                New: ``client.tournament.query("PAPA").country("US").get()``

        Args:
            name: Tournament name to search for (partial match)
            city: Filter by city
            stateprov: Filter by state/province
            country: Filter by country code
            start_date: Filter by start date (YYYY-MM-DD). Must be provided with end_date.
            end_date: Filter by end date (YYYY-MM-DD). Must be provided with start_date.
            tournament_type: Filter by tournament type (open, women, etc.)
            start_pos: Starting position for pagination
            count: Number of results to return

        Returns:
            List of matching tournaments

        Raises:
            ValueError: If only one of start_date or end_date is provided
            IfpaApiError: If the API request fails

        Note:
            The API requires start_date and end_date to be provided together.
            Providing only one will result in a ValueError.

        Example:
            ```python
            # Search by name
            results = client.tournament.search(name="Pinball")

            # Search by location and date range (must provide BOTH dates)
            results = client.tournament.search(
                city="Portland",
                stateprov="OR",
                start_date="2024-01-01",
                end_date="2024-12-31"
            )

            # Paginated search
            results = client.tournament.search(
                country="US",
                start_pos=0,
                count=50
            )
            ```
        """
        warnings.warn(
            "TournamentClient.search() is deprecated and will be removed in v1.0.0. "
            "Use TournamentClient.query() instead:\n"
            "  # Old (deprecated):\n"
            "  client.tournament.search(name='PAPA', country='US')\n"
            "  # New (recommended):\n"
            "  client.tournament.query('PAPA').country('US').get()",
            DeprecationWarning,
            stacklevel=2,
        )

        # Validate that start_date and end_date are provided together
        if (start_date is not None) != (end_date is not None):
            raise ValueError(
                "start_date and end_date must be provided together. "
                "The IFPA API requires both dates or neither. "
                f"Received start_date={start_date}, end_date={end_date}"
            )

        params: dict[str, Any] = {}
        if name is not None:
            params["name"] = name
        if city is not None:
            params["city"] = city
        if stateprov is not None:
            params["stateprov"] = stateprov
        if country is not None:
            params["country"] = country
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        if tournament_type is not None:
            params["tournament_type"] = tournament_type
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count

        response = self._http._request("GET", "/tournament/search", params=params)
        return TournamentSearchResponse.model_validate(response)

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
