"""Tournament resource client with callable pattern.

Main entry point for tournament operations, providing both collection-level
and resource-level access patterns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ifpa_api.core.base import BaseResourceClient
from ifpa_api.models.tournaments import TournamentFormatsListResponse

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
