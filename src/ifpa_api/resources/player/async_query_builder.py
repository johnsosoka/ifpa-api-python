"""Fluent async query builder for player search operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self

from ifpa_api.core.async_base import LocationFiltersMixin, PaginationMixin
from ifpa_api.core.async_query_builder import AsyncQueryBuilder
from ifpa_api.models.player import PlayerSearchResponse, PlayerSearchResult

if TYPE_CHECKING:
    from ifpa_api.core.async_http import _AsyncHttpClient


class AsyncPlayerQueryBuilder(
    AsyncQueryBuilder[PlayerSearchResponse],
    LocationFiltersMixin,
    PaginationMixin,
):
    """Fluent async query builder for player search operations.

    This class implements an immutable query builder pattern for searching players
    asynchronously. Each method returns a new instance, allowing safe query composition
    and reuse.

    Attributes:
        _http: The async HTTP client instance
        _params: Accumulated query parameters

    Example:
        ```python
        # Simple query
        async with AsyncIfpaClient() as client:
            results = await client.player.search("John").get()

        # Chained filters with immutability
        async with AsyncIfpaClient() as client:
            us_query = client.player.search().country("US")
            wa_players = await us_query.state("WA").limit(25).get()
            or_players = await us_query.state("OR").limit(25).get()  # base unchanged!

        # Complex query
        async with AsyncIfpaClient() as client:
            results = await (client.player.search("Smith")
                .country("CA")
                .tournament("PAPA")
                .position(1)
                .limit(50)
                .get())
        ```
    """

    def __init__(self, http: _AsyncHttpClient) -> None:
        """Initialize the async player query builder.

        Args:
            http: The async HTTP client instance
        """
        super().__init__()
        self._http = http

    def query(self, name: str) -> Self:
        """Set the player name to search for.

        Args:
            name: Player name to search for (partial match, not case sensitive)

        Returns:
            New AsyncPlayerQueryBuilder instance with the name parameter set

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                results = await client.player.search("John").get()
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
            New AsyncPlayerQueryBuilder instance with the tournament filter applied

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                results = await client.player.search().tournament("PAPA").get()
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
            New AsyncPlayerQueryBuilder instance with the position filter applied

        Example:
            ```python
            # Find all players who won PAPA
            async with AsyncIfpaClient() as client:
                results = await client.player.search().tournament("PAPA").position(1).get()
            ```
        """
        clone = self._clone()
        clone._params["tourpos"] = finish_position
        return clone

    async def get(self) -> PlayerSearchResponse:
        """Execute the query and return results.

        Returns:
            PlayerSearchResponse containing matching players

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                results = await client.player.search("John").country("US").get()
                print(f"Found {len(results.search)} players")
                for player in results.search:
                    print(f"{player.first_name} {player.last_name}")
            ```
        """
        response = await self._http._request("GET", "/player/search", params=self._params)
        return PlayerSearchResponse.model_validate(response)

    async def first(self) -> PlayerSearchResult:
        """Get the first result from the search.

        This is a convenience method that executes the query and returns
        only the first result.

        Returns:
            The first search result

        Raises:
            IfpaApiError: If the API request fails
            IndexError: If the search returns no results

        Example:
            ```python
            # Get first player matching search
            async with AsyncIfpaClient() as client:
                player = await client.player.search("Smith").first()

            # With filters
            async with AsyncIfpaClient() as client:
                player = await (client.player.search("John")
                    .country("US")
                    .first())
            ```
        """
        results = await self.get()
        if not results.search:
            raise IndexError("Search returned no results")
        return results.search[0]

    async def first_or_none(self) -> PlayerSearchResult | None:
        """Get the first result from the search, or None if no results.

        This is a convenience method that executes the query and returns
        the first result, or None if the search returns no results.

        Returns:
            The first search result, or None if no results found

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                player = await client.player.search("Smith").first_or_none()
                if player:
                    print(f"Found: {player.first_name}")
                else:
                    print("No results found")
            ```
        """
        try:
            return await self.first()
        except IndexError:
            return None
