"""Async tournament resource client with callable pattern."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ifpa_api.core.async_base import AsyncBaseResourceClient
from ifpa_api.core.deprecation import issue_deprecation_warning
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.models.tournaments import Tournament, TournamentFormatsListResponse

from .async_context import AsyncTournamentContext
from .async_query_builder import AsyncTournamentQueryBuilder

if TYPE_CHECKING:
    pass


class AsyncTournamentClient(AsyncBaseResourceClient):
    """Async callable client for tournament operations.

    This client provides both collection-level methods and resource-level
    access via the callable pattern. Call with a tournament ID to get
    a context for tournament-specific operations.

    Attributes:
        _http: The async HTTP client instance
        _validate_requests: Whether to validate request parameters

    Example:
        ```python
        # Query builder pattern (RECOMMENDED)
        async with AsyncIfpaClient() as client:
            results = await client.tournament.search("PAPA").country("US").get()

        # Resource-level operations
        async with AsyncIfpaClient() as client:
            tournament = await client.tournament(12345).details()
            results = await client.tournament(12345).results()
        ```
    """

    def __call__(self, tournament_id: int | str) -> AsyncTournamentContext:
        """Get a context for a specific tournament.

        Args:
            tournament_id: The tournament's unique identifier

        Returns:
            AsyncTournamentContext instance for accessing tournament-specific operations

        Example:
            ```python
            # Get tournament context and access methods
            async with AsyncIfpaClient() as client:
                tournament = await client.tournament(12345).details()
                results = await client.tournament(12345).results()
            ```
        """
        return AsyncTournamentContext(self._http, tournament_id, self._validate_requests)

    async def get(self, tournament_id: int | str) -> Tournament:
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
            async with AsyncIfpaClient() as client:
                tournament = await client.tournament.get(12345)

            # Old way (still works but deprecated)
            async with AsyncIfpaClient() as client:
                tournament = await client.tournament(12345).details()
            ```
        """
        context = self(tournament_id)
        return await context.details()

    async def get_or_none(self, tournament_id: int | str) -> Tournament | None:
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
            async with AsyncIfpaClient() as client:
                tournament = await client.tournament.get_or_none(12345)
                if tournament:
                    print(f"Found: {tournament.tournament_name}")
                else:
                    print("Tournament not found")
            ```
        """
        try:
            return await self.get(tournament_id)
        except IfpaApiError as e:
            if e.status_code == 404:
                return None
            raise
        except Exception:
            # API returns empty dict {} for non-existent tournaments which causes validation error
            return None

    async def exists(self, tournament_id: int | str) -> bool:
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
            async with AsyncIfpaClient() as client:
                if await client.tournament.exists(12345):
                    print("Tournament exists!")
                else:
                    print("Tournament not found")
            ```
        """
        tournament = await self.get_or_none(tournament_id)
        return tournament is not None

    def search(self, name: str = "") -> AsyncTournamentQueryBuilder:
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
            async with AsyncIfpaClient() as client:
                results = await client.tournament.search("PAPA").get()

            # Chained filters
            async with AsyncIfpaClient() as client:
                results = await (client.tournament.search("Championship")
                    .country("US")
                    .state("WA")
                    .limit(25)
                    .get())

            # Filter-only search (no name query)
            async with AsyncIfpaClient() as client:
                results = await (client.tournament.search()
                    .date_range("2024-01-01", "2024-12-31")
                    .get())
            ```
        """
        builder = AsyncTournamentQueryBuilder(self._http)
        if name:
            return builder.query(name)
        return builder

    def query(self, name: str = "") -> AsyncTournamentQueryBuilder:
        """Create a fluent query builder for searching tournaments (deprecated).

        .. deprecated:: 0.4.0
            Use :meth:`search` instead. This method will be removed in version 1.0.0.

        Args:
            name: Optional tournament name to search for (can also be set via .query() on builder)

        Returns:
            AsyncTournamentQueryBuilder instance for building the search query
        """
        issue_deprecation_warning(
            old_name="query()",
            new_name="search()",
            version="1.0.0",
            additional_info="The search() method provides the same functionality.",
        )
        return self.search(name)

    async def list_formats(self) -> TournamentFormatsListResponse:
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
            async with AsyncIfpaClient() as client:
                formats = await client.tournament.list_formats()

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
        response = await self._http._request("GET", "/tournament/formats")
        return TournamentFormatsListResponse.model_validate(response)
