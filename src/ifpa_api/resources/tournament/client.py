"""Tournament resource client with callable pattern.

Main entry point for tournament operations, providing both collection-level
and resource-level access patterns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ifpa_api.core.base import BaseResourceClient
from ifpa_api.core.deprecation import issue_deprecation_warning
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.models.tournaments import Tournament, TournamentFormatsListResponse

from .context import _TournamentContext
from .query_builder import TournamentQueryBuilder

if TYPE_CHECKING:
    pass


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

    def get(self, tournament_id: int | str) -> Tournament:
        """Get tournament by ID directly.

        This is a convenience method equivalent to calling tournament(id).details().

        Args:
            tournament_id: The tournament's unique identifier

        Returns:
            The tournament details

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # New preferred way
            tournament = client.tournament.get(12345)

            # Old way (still works but deprecated)
            tournament = client.tournament(12345).details()
            ```
        """
        return self(tournament_id).details()

    def get_or_none(self, tournament_id: int | str) -> Tournament | None:
        """Get tournament by ID, returning None if not found.

        This convenience method wraps get() and returns None instead of raising
        an exception when the tournament is not found (404 status code).

        Args:
            tournament_id: The tournament's unique identifier

        Returns:
            The tournament details, or None if not found

        Raises:
            IfpaApiError: If the API request fails with a non-404 error

        Example:
            ```python
            tournament = client.tournament.get_or_none(12345)
            if tournament:
                print(f"Found: {tournament.tournament_name}")
            else:
                print("Tournament not found")
            ```
        """
        try:
            return self.get(tournament_id)
        except IfpaApiError as e:
            if e.status_code == 404:
                return None
            raise

    def exists(self, tournament_id: int | str) -> bool:
        """Check if a tournament exists by ID.

        This convenience method returns True if the tournament exists, False otherwise.
        It's more readable than checking if get_or_none() returns None when you
        only need to verify existence.

        Args:
            tournament_id: The tournament's unique identifier

        Returns:
            True if the tournament exists, False if not found

        Raises:
            IfpaApiError: If the API request fails with a non-404 error

        Example:
            ```python
            if client.tournament.exists(12345):
                print("Tournament exists!")
            else:
                print("Tournament not found")
            ```
        """
        return self.get_or_none(tournament_id) is not None

    def search(self, name: str = "") -> TournamentQueryBuilder:
        """Search for tournaments by name (preferred method).

        This method returns a query builder that allows you to compose search
        filters in a fluent, chainable way. This is the preferred method over
        the deprecated query() method.

        Args:
            name: Optional name query string to search for

        Returns:
            A query builder for composing search filters

        Example:
            ```python
            # Simple search
            results = client.tournament.search("PAPA").get()

            # Chained filters
            results = (client.tournament.search("Championship")
                .country("US")
                .state("WA")
                .limit(25)
                .get())

            # Filter-only search (no name query)
            results = (client.tournament.search()
                .date_range("2024-01-01", "2024-12-31")
                .get())
            ```
        """
        builder = TournamentQueryBuilder(self._http)
        if name:
            return builder.query(name)
        return builder

    def query(self, name: str = "") -> TournamentQueryBuilder:
        """Create a fluent query builder for searching tournaments (deprecated).

        .. deprecated:: 0.4.0
            Use :meth:`search` instead. This method will be removed in version 1.0.0.

        Args:
            name: Optional tournament name to search for (can also be set via .query() on builder)

        Returns:
            TournamentQueryBuilder instance for building the search query
        """
        issue_deprecation_warning(
            old_name="query()",
            new_name="search()",
            version="1.0.0",
            additional_info="The search() method provides the same functionality.",
        )
        return self.search(name)

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
