"""Fluent query builder for player search operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self

from ifpa_api.core.base import LocationFiltersMixin, PaginationMixin
from ifpa_api.core.query_builder import QueryBuilder
from ifpa_api.models.player import PlayerSearchResponse

if TYPE_CHECKING:
    from ifpa_api.core.http import _HttpClient


class PlayerQueryBuilder(
    QueryBuilder[PlayerSearchResponse],
    LocationFiltersMixin,
    PaginationMixin,
):
    """Fluent query builder for player search operations.

    This class implements an immutable query builder pattern for searching players.
    Each method returns a new instance, allowing safe query composition and reuse.

    Attributes:
        _http: The HTTP client instance
        _params: Accumulated query parameters

    Example:
        ```python
        # Simple query
        results = client.player.query("John").get()

        # Chained filters with immutability
        us_query = client.player.query().country("US")
        wa_players = us_query.state("WA").limit(25).get()
        or_players = us_query.state("OR").limit(25).get()  # base unchanged!

        # Complex query
        results = (client.player.query("Smith")
            .country("CA")
            .tournament("PAPA")
            .position(1)
            .limit(50)
            .get())
        ```
    """

    def __init__(self, http: _HttpClient) -> None:
        """Initialize the player query builder.

        Args:
            http: The HTTP client instance
        """
        super().__init__()
        self._http = http

    def query(self, name: str) -> Self:
        """Set the player name to search for.

        Args:
            name: Player name to search for (partial match, not case sensitive)

        Returns:
            New PlayerQueryBuilder instance with the name parameter set

        Example:
            ```python
            results = client.player.query("John").get()
            ```
        """
        clone = self._clone()
        clone._params["name"] = name
        return clone

    def tournament(self, tournament_name: str) -> Self:
        """Filter by tournament participation.

        Args:
            tournament_name: Tournament name (partial strings accepted)

        Returns:
            New PlayerQueryBuilder instance with the tournament filter applied

        Example:
            ```python
            results = client.player.query().tournament("PAPA").get()
            ```
        """
        clone = self._clone()
        clone._params["tournament"] = tournament_name
        return clone

    def position(self, finish_position: int) -> Self:
        """Filter by finishing position in tournament.

        Must be used with tournament() filter.

        Args:
            finish_position: Tournament finishing position to filter by

        Returns:
            New PlayerQueryBuilder instance with the position filter applied

        Example:
            ```python
            # Find all players who won PAPA
            results = client.player.query().tournament("PAPA").position(1).get()
            ```
        """
        clone = self._clone()
        clone._params["tourpos"] = finish_position
        return clone

    def get(self) -> PlayerSearchResponse:
        """Execute the query and return results.

        Returns:
            PlayerSearchResponse containing matching players

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            results = client.player.query("John").country("US").get()
            print(f"Found {len(results.search)} players")
            for player in results.search:
                print(f"{player.first_name} {player.last_name}")
            ```
        """
        response = self._http._request("GET", "/player/search", params=self._params)
        return PlayerSearchResponse.model_validate(response)
