"""Base query builder with immutable pattern for fluent API design.

This module provides the foundation for building fluent, type-safe query interfaces
across all IFPA API resources. The immutable pattern ensures thread-safety and
enables query reuse.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from copy import copy
from typing import TYPE_CHECKING, Any, Generic, TypeVar

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

    def __repr__(self) -> str:
        """Return a string representation of the query builder.

        Returns:
            String showing the class name and current parameters
        """
        return f"{self.__class__.__name__}(params={self._params})"
