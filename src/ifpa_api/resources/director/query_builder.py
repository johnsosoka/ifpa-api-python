"""Director query builder for fluent search interface.

Provides immutable query builder pattern for searching directors.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self

from ifpa_api.core.base import LocationFiltersMixin, PaginationMixin
from ifpa_api.core.query_builder import QueryBuilder
from ifpa_api.models.director import DirectorSearchResponse

if TYPE_CHECKING:
    from ifpa_api.core.http import _HttpClient


class DirectorQueryBuilder(
    QueryBuilder[DirectorSearchResponse], LocationFiltersMixin, PaginationMixin
):
    """Fluent query builder for director search operations.

    This class implements an immutable query builder pattern for searching directors.
    Each method returns a new instance, allowing safe query composition and reuse.

    Inherits location filtering (country, state, city) from LocationFiltersMixin
    and pagination (limit, offset) from PaginationMixin.

    Attributes:
        _http: The HTTP client instance
        _params: Accumulated query parameters

    Example:
        ```python
        # Simple query
        results = client.director.query("Josh").get()

        # Chained filters with immutability
        us_query = client.director.query().country("US")
        il_directors = us_query.state("IL").city("Chicago").get()
        or_directors = us_query.state("OR").get()  # base unchanged!

        # Complex query
        results = (client.director.query("Sharpe")
            .country("US")
            .state("IL")
            .city("Chicago")
            .limit(50)
            .get())
        ```
    """

    def __init__(self, http: _HttpClient) -> None:
        """Initialize the director query builder.

        Args:
            http: The HTTP client instance
        """
        super().__init__()
        self._http = http

    def query(self, name: str) -> Self:
        """Set the director name to search for.

        Args:
            name: Director name to search for (partial match, not case sensitive)

        Returns:
            New DirectorQueryBuilder instance with the name parameter set

        Example:
            ```python
            results = client.director.query("Josh").get()
            ```
        """
        clone = self._clone()
        clone._params["name"] = name
        return clone

    def get(self) -> DirectorSearchResponse:
        """Execute the query and return results.

        Returns:
            DirectorSearchResponse containing matching directors

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            results = client.director.query("Josh").country("US").get()
            print(f"Found {len(results.directors)} directors")
            for director in results.directors:
                print(f"{director.name} - {director.city}")
            ```
        """
        response = self._http._request("GET", "/director/search", params=self._params)
        return DirectorSearchResponse.model_validate(response)
