"""Fluent async query builder for director search operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self

from ifpa_api.core.async_base import LocationFiltersMixin, PaginationMixin
from ifpa_api.core.async_query_builder import AsyncQueryBuilder
from ifpa_api.models.director import DirectorSearchResponse, DirectorSearchResult

if TYPE_CHECKING:
    from ifpa_api.core.async_http import _AsyncHttpClient


class AsyncDirectorQueryBuilder(
    AsyncQueryBuilder[DirectorSearchResponse],
    LocationFiltersMixin,
    PaginationMixin,
):
    """Fluent async query builder for director search operations.

    This class implements an immutable query builder pattern for searching directors
    asynchronously. Each method returns a new instance, allowing safe query composition
    and reuse.

    Attributes:
        _http: The async HTTP client instance
        _params: Accumulated query parameters

    Example:
        ```python
        # Simple query
        async with AsyncIfpaClient() as client:
            results = await client.director.search("Josh").get()

        # Chained filters with immutability
        async with AsyncIfpaClient() as client:
            us_query = client.director.search().country("US")
            il_directors = await us_query.state("IL").limit(25).get()
            or_directors = await us_query.state("OR").limit(25).get()  # base unchanged!

        # Complex query
        async with AsyncIfpaClient() as client:
            results = await (client.director.search("Sharpe")
                .country("US")
                .state("IL")
                .city("Chicago")
                .limit(50)
                .get())
        ```
    """

    def __init__(self, http: _AsyncHttpClient) -> None:
        """Initialize the async director query builder.

        Args:
            http: The async HTTP client instance
        """
        super().__init__()
        self._http = http

    def query(self, name: str) -> Self:
        """Set the director name to search for.

        Args:
            name: Director name to search for (partial match, not case sensitive)

        Returns:
            New AsyncDirectorQueryBuilder instance with the name parameter set

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                results = await client.director.search("Josh").get()
            ```
        """
        clone = self._clone()
        clone._params["name"] = name
        return clone

    async def get(self) -> DirectorSearchResponse:
        """Execute the query and return results.

        Returns:
            DirectorSearchResponse containing matching directors

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                results = await client.director.search("Josh").country("US").get()
                print(f"Found {len(results.directors)} directors")
                for director in results.directors:
                    print(f"{director.name} - {director.city}")
            ```
        """
        response = await self._http._request("GET", "/director/search", params=self._params)
        return DirectorSearchResponse.model_validate(response)

    async def first(self) -> DirectorSearchResult:
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
            # Get first director matching search
            async with AsyncIfpaClient() as client:
                director = await client.director.search("Sharpe").first()

            # With filters
            async with AsyncIfpaClient() as client:
                director = await (client.director.search("Josh")
                    .country("US")
                    .first())
            ```
        """
        results = await self.get()
        if not results.directors:
            raise IndexError("Search returned no results")
        return results.directors[0]

    async def first_or_none(self) -> DirectorSearchResult | None:
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
                director = await client.director.search("Sharpe").first_or_none()
                if director:
                    print(f"Found: {director.name}")
                else:
                    print("No results found")
            ```
        """
        try:
            return await self.first()
        except IndexError:
            return None
