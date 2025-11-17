"""Director resource client with callable pattern.

Provides access to tournament director information, their tournament history,
and search capabilities.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self

from ifpa_api.core.base import (
    BaseResourceClient,
    BaseResourceContext,
    LocationFiltersMixin,
    PaginationMixin,
)
from ifpa_api.models.common import TimePeriod
from ifpa_api.models.director import (
    CountryDirectorsResponse,
    Director,
    DirectorSearchResponse,
    DirectorTournamentsResponse,
)
from ifpa_api.query_builder import QueryBuilder

if TYPE_CHECKING:
    from ifpa_api.http import _HttpClient


# ============================================================================
# Director Context - Individual Director Operations
# ============================================================================


class _DirectorContext(BaseResourceContext[int | str]):
    """Context for interacting with a specific tournament director.

    This internal class provides resource-specific methods for a director
    identified by their director ID. Instances are returned by calling
    DirectorClient with a director ID.

    Attributes:
        _http: The HTTP client instance
        _resource_id: The director's unique identifier
        _validate_requests: Whether to validate request parameters
    """

    def details(self) -> Director:
        """Get detailed information about this director.

        Returns:
            Director information including statistics and profile

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            director = client.director(1000).details()
            print(f"Director: {director.name}")
            print(f"Tournaments: {director.stats.tournament_count}")
            ```
        """
        response = self._http._request("GET", f"/director/{self._resource_id}")
        return Director.model_validate(response)

    def tournaments(self, time_period: TimePeriod) -> DirectorTournamentsResponse:
        """Get tournaments directed by this director.

        Args:
            time_period: Whether to get past or future tournaments

        Returns:
            List of tournaments with details

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Get past tournaments
            past = client.director(1000).tournaments(TimePeriod.PAST)
            for tournament in past.tournaments:
                print(f"{tournament.tournament_name} - {tournament.event_date}")

            # Get upcoming tournaments
            future = client.director(1000).tournaments(TimePeriod.FUTURE)
            ```
        """
        # Convert enum to value
        period_value = time_period.value if isinstance(time_period, TimePeriod) else time_period

        response = self._http._request(
            "GET", f"/director/{self._resource_id}/tournaments/{period_value}"
        )
        return DirectorTournamentsResponse.model_validate(response)


# ============================================================================
# Director Query Builder - Fluent Search Interface
# ============================================================================


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


# ============================================================================
# Director Resource Client - Main Entry Point
# ============================================================================


class DirectorClient(BaseResourceClient):
    """Callable client for director operations.

    This client provides both collection-level methods (query, country_directors) and
    resource-level access via the callable pattern. Call with a director ID to get
    a context for director-specific operations.

    Attributes:
        _http: The HTTP client instance
        _validate_requests: Whether to validate request parameters

    Example:
        ```python
        # Query builder pattern (recommended)
        results = client.director.query("Josh").get()
        country_dirs = client.director.country_directors()

        # Resource-level operations
        director = client.director(1000).details()
        past_tournaments = client.director(1000).tournaments(TimePeriod.PAST)
        ```
    """

    def __call__(self, director_id: int | str) -> _DirectorContext:
        """Get a context for a specific director.

        Args:
            director_id: The director's unique identifier

        Returns:
            _DirectorContext instance for accessing director-specific operations

        Example:
            ```python
            # Get director context and access methods
            director = client.director(1000).details()
            tournaments = client.director(1000).tournaments(TimePeriod.PAST)
            ```
        """
        return _DirectorContext(self._http, director_id, self._validate_requests)

    def query(self, name: str = "") -> DirectorQueryBuilder:
        """Create a fluent query builder for searching directors.

        This is the recommended way to search for directors, providing a type-safe
        and composable interface. The returned builder can be reused and composed
        thanks to its immutable pattern.

        Args:
            name: Optional director name to search for (can also be set via .query() on builder)

        Returns:
            DirectorQueryBuilder instance for building the search query

        Example:
            ```python
            # Simple name search
            results = client.director.query("Josh").get()

            # Chained filters
            results = (client.director.query("Sharpe")
                .country("US")
                .state("IL")
                .city("Chicago")
                .limit(25)
                .get())

            # Query reuse (immutable pattern)
            us_base = client.director.query().country("US")
            il_directors = us_base.state("IL").get()
            or_directors = us_base.state("OR").get()  # base unchanged!

            # Empty query to start with filters
            results = (client.director.query()
                .country("US")
                .state("IL")
                .get())
            ```
        """
        builder = DirectorQueryBuilder(self._http)
        if name:
            return builder.query(name)
        return builder

    def country_directors(self) -> CountryDirectorsResponse:
        """Get list of IFPA country directors.

        Returns:
            List of country directors with their assigned countries

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            country_dirs = client.director.country_directors()
            for director in country_dirs.country_directors:
                print(f"{director.name} - {director.country_name}")
            ```
        """
        response = self._http._request("GET", "/director/country")
        return CountryDirectorsResponse.model_validate(response)
