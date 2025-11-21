"""Async base query builder with immutable pattern for fluent API design.

This module provides the foundation for building fluent, type-safe async query interfaces
across all IFPA API resources. The immutable pattern ensures thread-safety and
enables query reuse.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from copy import copy
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

if TYPE_CHECKING:
    from typing import Self

# Type variable for the response type that will be returned by execute()
T = TypeVar("T")


class AsyncQueryBuilder(ABC, Generic[T]):
    """Async base query builder with immutable pattern.

    This abstract class provides the foundation for async resource-specific query builders.
    It implements the immutable pattern where each method call returns a new instance,
    allowing queries to be safely composed and reused.

    The immutable pattern enables powerful query composition:
        ```python
        # Create a base query that can be reused
        async with AsyncIfpaClient() as client:
            base = client.player.search().country("US")

            # Each derivation creates a new instance
            wa_players = await base.state("WA").limit(25).get()
            or_players = await base.state("OR").limit(25).get()

            # The base query is unchanged and can be reused again
            ca_players = await base.state("CA").limit(25).get()
        ```

    Attributes:
        _params: Dictionary of accumulated query parameters
    """

    def __init__(self) -> None:
        """Initialize an empty query builder."""
        self._params: dict[str, Any] = {}

    def _clone(self) -> Self:
        """Create a shallow copy of this query builder.

        This method is the foundation of the immutable pattern. Each fluent method
        should call _clone(), modify the copy's parameters, and return the copy.

        Returns:
            A new instance with copied parameters of the same type as the caller

        Example:
            ```python
            def country(self, code: str) -> Self:
                clone = self._clone()
                clone._params["country"] = code
                return clone
            ```

        Note:
            This method uses shallow copy with explicit params dict copy. The _params
            dictionary should only contain immutable values (str, int, etc.). If you
            need to store mutable objects (lists, nested dicts), use deepcopy instead.
        """
        clone = copy(self)
        # Explicitly copy the params dict to ensure changes don't affect original
        # This is sufficient since params only contains scalar values (str, int, etc.)
        clone._params = self._params.copy()
        return clone

    @abstractmethod
    async def get(self) -> T:
        """Execute the query asynchronously and return results.

        This method must be implemented by subclasses to execute the actual
        API request with the accumulated parameters.

        Returns:
            The query results with type determined by the resource

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                results = await client.player.search("Smith").get()
            ```
        """

    async def iterate(self, limit: int = 100) -> AsyncIterator[Any]:
        """Async iterate through all results with automatic pagination.

        This method handles pagination automatically, fetching results in batches
        and yielding individual items. This is memory-efficient for large result sets.

        Args:
            limit: Number of results to fetch per request (default: 100)

        Yields:
            Individual items from the search results

        Raises:
            IfpaApiError: If any API request fails

        Example:
            ```python
            # Memory-efficient iteration over all US players
            async with AsyncIfpaClient() as client:
                async for player in client.player.search().country("US").iterate(limit=100):
                    print(f"{player.first_name} {player.last_name}")
            ```

        Note:
            This method assumes the response has a 'search' field containing results.
            Subclasses may need to override _extract_results() if the response
            structure differs.
        """
        offset = 0

        while True:
            # Clone and add pagination params
            query = self._clone()
            if hasattr(query, "limit"):
                query = query.limit(limit)
            if hasattr(query, "offset"):
                query = query.offset(offset)

            # Execute query asynchronously
            response = await query.get()

            # Extract results - this assumes 'search' field, override if different
            results = self._extract_results(response)

            if not results:
                break

            # Yield individual items
            for item in results:
                yield item

            # Check if we got fewer results than requested (last page)
            if len(results) < limit:
                break

            offset += limit

    def _extract_results(self, response: T) -> list[Any]:
        """Extract results list from response.

        This method should be overridden by subclasses if the response structure
        doesn't use the standard 'search' field.

        Args:
            response: The response object from get()

        Returns:
            List of result items
        """
        # Check for dict with 'search' key first (common case)
        if isinstance(response, dict):
            if "search" in response:
                return cast(list[Any], response["search"])
            if "results" in response:
                return cast(list[Any], response["results"])

        # Check for object with 'search' attribute
        if hasattr(response, "search"):
            return cast(list[Any], response.search)
        # Fallback for other patterns
        if hasattr(response, "results"):
            return cast(list[Any], response.results)
        # If response is already a list
        if isinstance(response, list):
            return response
        return []

    async def get_all(self, max_results: int | None = None) -> list[Any]:
        """Fetch all results asynchronously with automatic pagination.

        This is a convenience method that collects all results into a list.
        For large result sets, consider using iterate() instead for better
        memory efficiency.

        Args:
            max_results: Maximum number of results to fetch (optional safety limit)

        Returns:
            List of all result items

        Raises:
            IfpaApiError: If any API request fails
            ValueError: If max_results is exceeded

        Example:
            ```python
            # Fetch all players from Washington state
            async with AsyncIfpaClient() as client:
                all_players = await client.player.search().country("US").state("WA").get_all()
                print(f"Total players: {len(all_players)}")
            ```

        Warning:
            Without max_results limit, this could fetch thousands of results
            and consume significant memory. Use iterate() for large datasets.
        """
        results = []

        async for item in self.iterate():
            results.append(item)

            # Check max_results safety limit
            if max_results is not None and len(results) >= max_results:
                raise ValueError(
                    f"Result count exceeded max_results limit of {max_results}. "
                    f"Consider using iterate() for large datasets or increase the limit."
                )

        return results

    def __repr__(self) -> str:
        """Return a string representation of the query builder.

        Returns:
            String showing the class name and current parameters
        """
        return f"{self.__class__.__name__}(params={self._params})"
