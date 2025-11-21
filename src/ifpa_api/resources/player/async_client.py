"""Async player resource client with callable pattern."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ifpa_api.core.async_base import AsyncBaseResourceClient
from ifpa_api.core.deprecation import issue_deprecation_warning
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.models.player import Player

from .async_context import AsyncPlayerContext
from .async_query_builder import AsyncPlayerQueryBuilder

if TYPE_CHECKING:
    pass


class AsyncPlayerClient(AsyncBaseResourceClient):
    """Async callable client for player operations.

    This client provides both collection-level query builder and resource-level
    access via the callable pattern. Call with a player ID to get a context for
    player-specific operations.

    Attributes:
        _http: The async HTTP client instance
        _validate_requests: Whether to validate request parameters

    Example:
        ```python
        # Query builder pattern (RECOMMENDED)
        async with AsyncIfpaClient() as client:
            results = await client.player.search("John").country("US").get()

        # Resource-level operations
        async with AsyncIfpaClient() as client:
            player = await client.player(12345).details()
            pvp = await client.player(12345).pvp(67890)
            results = await client.player(12345).results(RankingSystem.MAIN, ResultType.ACTIVE)
        ```
    """

    def __call__(self, player_id: int | str) -> AsyncPlayerContext:
        """Get a context for a specific player.

        Args:
            player_id: The player's unique identifier

        Returns:
            AsyncPlayerContext instance for accessing player-specific operations

        Example:
            ```python
            # Get player context and access methods
            async with AsyncIfpaClient() as client:
                player = await client.player(12345).details()
                pvp = await client.player(12345).pvp(67890)
                history = await client.player(12345).history()
            ```
        """
        return AsyncPlayerContext(self._http, player_id, self._validate_requests)

    async def get(self, player_id: int | str) -> Player:
        """Get player by ID directly.

        This is a convenience method equivalent to calling player(id).details().

        Args:
            player_id: The player's unique identifier

        Returns:
            The player details

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # New preferred way
            async with AsyncIfpaClient() as client:
                player = await client.player.get(12345)

            # Old way (still works but deprecated)
            async with AsyncIfpaClient() as client:
                player = await client.player(12345).details()
            ```
        """
        context = self(player_id)
        return await context.details()

    async def get_or_none(self, player_id: int | str) -> Player | None:
        """Get player by ID, returning None if not found.

        This convenience method wraps get() and returns None instead of raising
        an exception when the player is not found (404 status code).

        Args:
            player_id: The player's unique identifier

        Returns:
            The player details, or None if not found

        Raises:
            IfpaApiError: If the API request fails with a non-404 error

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                player = await client.player.get_or_none(12345)
                if player:
                    print(f"Found: {player.first_name} {player.last_name}")
                else:
                    print("Player not found")
            ```
        """
        try:
            return await self.get(player_id)
        except IfpaApiError as e:
            if e.status_code == 404:
                return None
            raise

    async def exists(self, player_id: int | str) -> bool:
        """Check if a player exists by ID.

        This convenience method returns True if the player exists, False otherwise.
        It's more readable than checking if get_or_none() returns None when you
        only need to verify existence.

        Args:
            player_id: The player's unique identifier

        Returns:
            True if the player exists, False if not found

        Raises:
            IfpaApiError: If the API request fails with a non-404 error

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                if await client.player.exists(12345):
                    print("Player exists!")
                else:
                    print("Player not found")
            ```
        """
        player = await self.get_or_none(player_id)
        return player is not None

    def search(self, name: str = "") -> AsyncPlayerQueryBuilder:
        """Search for players by name (preferred method).

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
                results = await client.player.search("John").get()

            # Chained filters
            async with AsyncIfpaClient() as client:
                results = await (client.player.search("Smith")
                    .country("US")
                    .state("WA")
                    .limit(25)
                    .get())

            # Filter-only search (no name query)
            async with AsyncIfpaClient() as client:
                results = await (client.player.search()
                    .country("CA")
                    .get())
            ```
        """
        builder = AsyncPlayerQueryBuilder(self._http)
        if name:
            return builder.query(name)
        return builder

    def query(self, name: str = "") -> AsyncPlayerQueryBuilder:
        """Create a fluent query builder for searching players (deprecated).

        .. deprecated:: 0.4.0
            Use :meth:`search` instead. This method will be removed in version 1.0.0.

        Args:
            name: Optional player name to search for (can also be set via .query() on builder)

        Returns:
            AsyncPlayerQueryBuilder instance for building the search query
        """
        issue_deprecation_warning(
            old_name="query()",
            new_name="search()",
            version="1.0.0",
            additional_info="The search() method provides the same functionality.",
        )
        return self.search(name)
