"""Player resource client with callable pattern."""

from __future__ import annotations

from ifpa_api.core.base import BaseResourceClient
from ifpa_api.core.deprecation import issue_deprecation_warning
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.models.player import Player

from .context import _PlayerContext
from .query_builder import PlayerQueryBuilder


class PlayerClient(BaseResourceClient):
    """Callable client for player operations.

    This client provides both collection-level query builder and resource-level
    access via the callable pattern. Call with a player ID to get a context for
    player-specific operations.

    Attributes:
        _http: The HTTP client instance
        _validate_requests: Whether to validate request parameters

    Example:
        ```python
        # Query builder pattern (RECOMMENDED)
        results = client.player.query("John").country("US").get()

        # Resource-level operations
        player = client.player(12345).details()
        pvp = client.player(12345).pvp(67890)
        results = client.player(12345).results(RankingSystem.MAIN, ResultType.ACTIVE)
        ```
    """

    def __call__(self, player_id: int | str) -> _PlayerContext:
        """Get a context for a specific player.

        Args:
            player_id: The player's unique identifier

        Returns:
            _PlayerContext instance for accessing player-specific operations

        Example:
            ```python
            # Get player context and access methods
            player = client.player(12345).details()
            pvp = client.player(12345).pvp(67890)
            history = client.player(12345).history()
            ```
        """
        return _PlayerContext(self._http, player_id, self._validate_requests)

    def get(self, player_id: int | str) -> Player:
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
            player = client.player.get(12345)

            # Old way (still works but deprecated)
            player = client.player(12345).details()
            ```
        """
        return self(player_id).details()

    def get_or_none(self, player_id: int | str) -> Player | None:
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
            player = client.player.get_or_none(12345)
            if player:
                print(f"Found: {player.first_name} {player.last_name}")
            else:
                print("Player not found")
            ```
        """
        try:
            return self.get(player_id)
        except IfpaApiError as e:
            if e.status_code == 404:
                return None
            raise

    def exists(self, player_id: int | str) -> bool:
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
            if client.player.exists(12345):
                print("Player exists!")
            else:
                print("Player not found")
            ```
        """
        return self.get_or_none(player_id) is not None

    def search(self, name: str = "") -> PlayerQueryBuilder:
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
            results = client.player.search("John").get()

            # Chained filters
            results = (client.player.search("Smith")
                .country("US")
                .state("WA")
                .limit(25)
                .get())

            # Filter-only search (no name query)
            results = (client.player.search()
                .country("CA")
                .get())
            ```
        """
        builder = PlayerQueryBuilder(self._http)
        if name:
            return builder.query(name)
        return builder

    def query(self, name: str = "") -> PlayerQueryBuilder:
        """Create a fluent query builder for searching players (deprecated).

        .. deprecated:: 0.4.0
            Use :meth:`search` instead. This method will be removed in version 1.0.0.

        Args:
            name: Optional player name to search for (can also be set via .query() on builder)

        Returns:
            PlayerQueryBuilder instance for building the search query
        """
        issue_deprecation_warning(
            old_name="query()",
            new_name="search()",
            version="1.0.0",
            additional_info="The search() method provides the same functionality.",
        )
        return self.search(name)
