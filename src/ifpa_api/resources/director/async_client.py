"""Async director resource client with callable pattern."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ifpa_api.core.async_base import AsyncBaseResourceClient
from ifpa_api.core.deprecation import issue_deprecation_warning
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.models.director import CountryDirectorsResponse, Director

from .async_context import AsyncDirectorContext
from .async_query_builder import AsyncDirectorQueryBuilder

if TYPE_CHECKING:
    pass


class AsyncDirectorClient(AsyncBaseResourceClient):
    """Async callable client for director operations.

    This client provides both collection-level query builder and resource-level
    access via the callable pattern. Call with a director ID to get a context for
    director-specific operations.

    Attributes:
        _http: The async HTTP client instance
        _validate_requests: Whether to validate request parameters

    Example:
        ```python
        # Query builder pattern (RECOMMENDED)
        async with AsyncIfpaClient() as client:
            results = await client.director.search("Josh").country("US").get()

        # Resource-level operations
        async with AsyncIfpaClient() as client:
            director = await client.director(1533).details()
            tournaments = await client.director(1533).tournaments(TimePeriod.PAST)
        ```
    """

    def __call__(self, director_id: int | str) -> AsyncDirectorContext:
        """Get a context for a specific director.

        Args:
            director_id: The director's unique identifier

        Returns:
            AsyncDirectorContext instance for accessing director-specific operations

        Example:
            ```python
            # Get director context and access methods
            async with AsyncIfpaClient() as client:
                director = await client.director(1533).details()
                tournaments = await client.director(1533).tournaments(TimePeriod.PAST)
            ```
        """
        return AsyncDirectorContext(self._http, director_id, self._validate_requests)

    async def get(self, director_id: int | str) -> Director:
        """Get director by ID directly.

        This is a convenience method equivalent to calling director(id).details().

        Args:
            director_id: The director's unique identifier

        Returns:
            The director details

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # New preferred way
            async with AsyncIfpaClient() as client:
                director = await client.director.get(1533)

            # Old way (still works but deprecated)
            async with AsyncIfpaClient() as client:
                director = await client.director(1533).details()
            ```
        """
        context = self(director_id)
        return await context.details()

    async def get_or_none(self, director_id: int | str) -> Director | None:
        """Get director by ID, returning None if not found.

        This convenience method wraps get() and returns None instead of raising
        an exception when the director is not found (404 status code).

        Args:
            director_id: The director's unique identifier

        Returns:
            The director details, or None if not found

        Raises:
            IfpaApiError: If the API request fails with a non-404 error

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                director = await client.director.get_or_none(1533)
                if director:
                    print(f"Found: {director.name}")
                else:
                    print("Director not found")
            ```
        """
        try:
            return await self.get(director_id)
        except IfpaApiError as e:
            if e.status_code in (400, 404):
                return None
            raise

    async def exists(self, director_id: int | str) -> bool:
        """Check if a director exists by ID.

        This convenience method returns True if the director exists, False otherwise.
        It's more readable than checking if get_or_none() returns None when you
        only need to verify existence.

        Args:
            director_id: The director's unique identifier

        Returns:
            True if the director exists, False if not found

        Raises:
            IfpaApiError: If the API request fails with a non-404 error

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                if await client.director.exists(1533):
                    print("Director exists!")
                else:
                    print("Director not found")
            ```
        """
        director = await self.get_or_none(director_id)
        return director is not None

    def search(self, name: str = "") -> AsyncDirectorQueryBuilder:
        """Search for directors by name (preferred method).

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
                results = await client.director.search("Josh").get()

            # Chained filters
            async with AsyncIfpaClient() as client:
                results = await (client.director.search("Sharpe")
                    .country("US")
                    .state("IL")
                    .limit(25)
                    .get())

            # Filter-only search (no name query)
            async with AsyncIfpaClient() as client:
                results = await (client.director.search()
                    .country("CA")
                    .get())
            ```
        """
        builder = AsyncDirectorQueryBuilder(self._http)
        if name:
            return builder.query(name)
        return builder

    def query(self, name: str = "") -> AsyncDirectorQueryBuilder:
        """Create a fluent query builder for searching directors (deprecated).

        .. deprecated:: 0.4.0
            Use :meth:`search` instead. This method will be removed in version 1.0.0.

        Args:
            name: Optional director name to search for (can also be set via .query() on builder)

        Returns:
            AsyncDirectorQueryBuilder instance for building the search query
        """
        issue_deprecation_warning(
            old_name="query()",
            new_name="search()",
            version="1.0.0",
            additional_info="The search() method provides the same functionality.",
        )
        return self.search(name)

    async def country_directors(self) -> CountryDirectorsResponse:
        """Get list of IFPA country directors.

        Returns:
            List of country directors with their assigned countries

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                country_dirs = await client.director.country_directors()
                for director in country_dirs.country_directors:
                    print(f"{director.name} - {director.country_name}")
            ```
        """
        response = await self._http._request("GET", "/director/country")
        return CountryDirectorsResponse.model_validate(response)
