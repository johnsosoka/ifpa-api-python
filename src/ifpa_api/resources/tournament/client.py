"""Tournament resource client with callable pattern.

Main entry point for tournament operations, providing both collection-level
and resource-level access patterns.
"""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from ifpa_api.core.base import BaseResourceClient
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

    def search(self, name: str = "") -> TournamentQueryBuilder:
        """Search for tournaments by name (preferred method).

        This is the preferred method for searching tournaments. The .query() method is deprecated
        and will be removed in v5.0.0.

        Args:
            name: Name to search for (optional, can be empty to search all)

        Returns:
            TournamentQueryBuilder instance for chaining filters

        Example:
            ```python
            # Search by name
            results = client.tournament.search("PAPA").get()

            # Search all with filters
            results = client.tournament.search().country("US").limit(10).get()

            # Chained filters with date range
            results = (client.tournament.search("Championship")
                .country("US")
                .state("WA")
                .date_range("2024-01-01", "2024-12-31")
                .limit(25)
                .get())

            # Query reuse (immutable pattern)
            us_base = client.tournament.search().country("US")
            wa_tournaments = us_base.state("WA").get()
            or_tournaments = us_base.state("OR").get()  # base unchanged!
            ```
        """
        builder = TournamentQueryBuilder(self._http)
        if name:
            return builder.query(name)
        return builder

    def query(self, name: str = "") -> TournamentQueryBuilder:
        """DEPRECATED: Search for tournaments by name.

        .. deprecated:: 4.0.0
           Use :meth:`search` instead. This method will be removed in v5.0.0.

        Args:
            name: Name to search for

        Returns:
            TournamentQueryBuilder instance

        Example:
            ```python
            # Old way (deprecated)
            results = client.tournament.query("PAPA").get()

            # New way (preferred)
            results = client.tournament.search("PAPA").get()
            ```
        """
        warnings.warn(
            "The .query() method is deprecated and will be removed in v5.0.0. "
            "Please use .search() instead.",
            DeprecationWarning,
            stacklevel=2,
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

    def get(self, tournament_id: int | str) -> Tournament:
        """Get tournament by ID.

        Args:
            tournament_id: The tournament's unique identifier

        Returns:
            Tournament object with complete tournament information

        Raises:
            IfpaApiError: If tournament not found (404) or other API error

        Example:
            ```python
            tournament = client.tournament.get(54321)
            print(f"{tournament.tournament_name} on {tournament.event_date}")
            ```
        """
        return self(tournament_id).details()

    def get_or_none(self, tournament_id: int | str) -> Tournament | None:
        """Get tournament by ID, returning None if not found.

        Args:
            tournament_id: The tournament's unique identifier

        Returns:
            Tournament object if found, None if not found (404)

        Raises:
            IfpaApiError: For API errors other than 404

        Example:
            ```python
            tournament = client.tournament.get_or_none(54321)
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
        """Check if tournament exists.

        Args:
            tournament_id: The tournament's unique identifier

        Returns:
            True if tournament exists, False otherwise

        Example:
            ```python
            if client.tournament.exists(54321):
                print("Tournament exists!")
            ```
        """
        return self.get_or_none(tournament_id) is not None
