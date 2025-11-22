"""Player resource client with callable pattern."""

from __future__ import annotations

import warnings

from ifpa_api.core.base import BaseResourceClient
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

    def search(self, name: str = "") -> PlayerQueryBuilder:
        """Search for players by name (preferred method).

        This is the preferred method for searching players. The .query() method is deprecated
        and will be removed in v5.0.0.

        Args:
            name: Name to search for (optional, can be empty to search all)

        Returns:
            PlayerQueryBuilder instance for chaining filters

        Example:
            ```python
            # Search by name
            results = client.player.search("John").get()

            # Search all with filters
            results = client.player.search().country("US").limit(10).get()

            # Chained filters
            results = (client.player.search("Smith")
                .country("US")
                .state("WA")
                .limit(25)
                .get())

            # Query reuse (immutable pattern)
            us_base = client.player.search().country("US")
            wa_players = us_base.state("WA").get()
            or_players = us_base.state("OR").get()  # base unchanged!
            ```
        """
        builder = PlayerQueryBuilder(self._http)
        if name:
            return builder.query(name)
        return builder

    def query(self, name: str = "") -> PlayerQueryBuilder:
        """DEPRECATED: Search for players by name.

        .. deprecated:: 4.0.0
           Use :meth:`search` instead. This method will be removed in v5.0.0.

        Args:
            name: Name to search for

        Returns:
            PlayerQueryBuilder instance

        Example:
            ```python
            # Old way (deprecated)
            results = client.player.query("John").get()

            # New way (preferred)
            results = client.player.search("John").get()
            ```
        """
        warnings.warn(
            "The .query() method is deprecated and will be removed in v5.0.0. "
            "Please use .search() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.search(name)

    def get(self, player_id: int | str) -> Player:
        """Get player by ID.

        Args:
            player_id: The player's unique identifier

        Returns:
            Player object with complete player information

        Raises:
            IfpaApiError: If player not found (404) or other API error

        Example:
            ```python
            player = client.player.get(12345)
            print(f"{player.first_name} {player.last_name}")
            ```
        """
        return self(player_id).details()

    def get_or_none(self, player_id: int | str) -> Player | None:
        """Get player by ID, returning None if not found.

        Args:
            player_id: The player's unique identifier

        Returns:
            Player object if found, None if not found (404)

        Raises:
            IfpaApiError: For API errors other than 404

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
        """Check if player exists.

        Args:
            player_id: The player's unique identifier

        Returns:
            True if player exists, False otherwise

        Example:
            ```python
            if client.player.exists(12345):
                print("Player exists!")
            ```
        """
        return self.get_or_none(player_id) is not None
