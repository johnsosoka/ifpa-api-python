"""Base query builder with immutable pattern for fluent API design.

This module provides the foundation for building fluent, type-safe query interfaces
across all IFPA API resources. The immutable pattern ensures thread-safety and
enables query reuse.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from copy import copy
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

if TYPE_CHECKING:
    from typing import Self

# Type variable for the response type that will be returned by execute()
T = TypeVar("T")


class QueryBuilder(ABC, Generic[T]):
    """Base query builder with immutable pattern.

    This abstract class provides the foundation for resource-specific query builders.
    It implements the immutable pattern where each method call returns a new instance,
    allowing queries to be safely composed and reused.

    The immutable pattern enables powerful query composition:
        ```python
        # Create a base query that can be reused
        base = client.player.query().country("US")

        # Each derivation creates a new instance
        wa_players = base.state("WA").limit(25).get()
        or_players = base.state("OR").limit(25).get()

        # The base query is unchanged and can be reused again
        ca_players = base.state("CA").limit(25).get()
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
    def get(self) -> T:
        """Execute the query and return results.

        This method must be implemented by subclasses to execute the actual
        API request with the accumulated parameters.

        Returns:
            The query results with type determined by the resource

        Raises:
            IfpaApiError: If the API request fails
        """

    def iterate(self, limit: int = 100) -> Iterator[Any]:
        """Iterate through all results with automatic pagination.

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
            for player in client.player.query().country("US").iterate(limit=100):
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

            # Execute query
            response = query.get()

            # Extract results - this assumes 'search' field, override if different
            results = self._extract_results(response)

            if not results:
                break

            # Yield individual items
            yield from results

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
        # Default implementation assumes response has 'search' field
        if hasattr(response, "search"):
            return cast(list[Any], response.search)
        # Fallback for other patterns
        if hasattr(response, "results"):
            return cast(list[Any], response.results)
        # If response is already a list
        if isinstance(response, list):
            return response
        return []

    def get_all(self, max_results: int | None = None) -> list[Any]:
        """Fetch all results with automatic pagination.

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
            all_players = client.player.query().country("US").state("WA").get_all()
            print(f"Total players: {len(all_players)}")
            ```

        Warning:
            Without max_results limit, this could fetch thousands of results
            and consume significant memory. Use iterate() for large datasets.
        """
        results = []

        for item in self.iterate():
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
