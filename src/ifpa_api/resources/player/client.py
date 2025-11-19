"""Player resource client with callable pattern."""

from __future__ import annotations

from ifpa_api.core.base import BaseResourceClient

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

    def query(self, name: str = "") -> PlayerQueryBuilder:
        """Create a fluent query builder for searching players.

        This is the recommended way to search for players, providing a type-safe
        and composable interface. The returned builder can be reused and composed
        thanks to its immutable pattern.

        Args:
            name: Optional player name to search for (can also be set via .query() on builder)

        Returns:
            PlayerQueryBuilder instance for building the search query

        Example:
            ```python
            # Simple name search
            results = client.player.query("John").get()

            # Chained filters
            results = (client.player.query("Smith")
                .country("US")
                .state("WA")
                .limit(25)
                .get())

            # Query reuse (immutable pattern)
            us_base = client.player.query().country("US")
            wa_players = us_base.state("WA").get()
            or_players = us_base.state("OR").get()  # base unchanged!

            # Empty query to start with filters
            results = (client.player.query()
                .tournament("PAPA")
                .position(1)
                .get())
            ```
        """
        builder = PlayerQueryBuilder(self._http)
        if name:
            return builder.query(name)
        return builder
