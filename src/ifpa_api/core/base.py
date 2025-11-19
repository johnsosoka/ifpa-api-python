"""Base classes and mixins for IFPA API client architecture.

This module provides the foundational base classes and mixins that eliminate
code duplication across resource clients, context managers, and query builders.

The architecture is built on three key abstractions:

1. BaseResourceContext: Base for resource-specific context managers (e.g., _PlayerContext)
2. BaseResourceClient: Base for resource client classes (e.g., PlayerClient)
3. Mixins: Reusable behavior for query builders (LocationFiltersMixin, PaginationMixin)

These abstractions enable the callable pattern and fluent query builder interfaces
while maintaining type safety and minimizing code duplication.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from typing import Self

    from ifpa_api.core.http import _HttpClient

# Type variable for BaseResourceContext resource_id type
T = TypeVar("T")


class BaseResourceContext(Generic[T]):
    """Base class for resource-specific context managers.

    This base class provides common initialization for context managers
    that handle operations on a specific resource instance (e.g., a specific player,
    director, or tournament).

    Context managers are returned by calling resource clients with a resource ID,
    enabling the fluent callable pattern:
        ```python
        player = client.player(12345).details()
        director = client.director(1533).details()
        ```

    The generic type parameter T allows the resource_id to be typed as int, str,
    or int | str depending on the specific resource requirements.

    Attributes:
        _http: The HTTP client instance for making API requests
        _resource_id: The unique identifier for the resource instance
        _validate_requests: Whether to validate request parameters before sending

    Example:
        ```python
        class _PlayerContext(BaseResourceContext[int | str]):
            def details(self) -> Player:
                response = self._http._request("GET", f"/player/{self._resource_id}")
                return Player.model_validate(response)
        ```
    """

    def __init__(self, http: _HttpClient, resource_id: T, validate_requests: bool) -> None:
        """Initialize a resource context.

        Args:
            http: The HTTP client instance for making API requests
            resource_id: The resource's unique identifier (type determined by subclass)
            validate_requests: Whether to validate request parameters before sending
        """
        self._http = http
        self._resource_id = resource_id
        self._validate_requests = validate_requests


class BaseResourceClient:
    """Base class for resource client classes.

    This base class provides common initialization for resource clients
    that manage both collection-level operations and individual resource access.

    Resource clients serve as the entry point for API operations on a specific
    resource type (players, directors, tournaments, etc.) and typically provide:
    - Collection operations (search, list all, etc.)
    - Callable pattern for resource-specific contexts
    - Query builder factories

    Attributes:
        _http: The HTTP client instance for making API requests
        _validate_requests: Whether to validate request parameters before sending

    Example:
        ```python
        class PlayerClient(BaseResourceClient):
            def __call__(self, player_id: int | str) -> _PlayerContext:
                return _PlayerContext(self._http, player_id, self._validate_requests)

            def query(self, name: str = "") -> PlayerQueryBuilder:
                return PlayerQueryBuilder(self._http, name)
        ```
    """

    def __init__(self, http: _HttpClient, validate_requests: bool) -> None:
        """Initialize the resource client.

        Args:
            http: The HTTP client instance for making API requests
            validate_requests: Whether to validate request parameters before sending
        """
        self._http = http
        self._validate_requests = validate_requests


class LocationFiltersMixin:
    """Mixin providing common location filter methods for query builders.

    This mixin adds country, state, and city filtering capabilities to query builders.
    It follows the immutable query builder pattern where each method returns a new
    instance, enabling safe query composition and reuse.

    The mixin expects the query builder to:
    - Have a _params dict[str, Any] attribute
    - Implement a _clone() -> Self method

    Type annotations for _params and _clone are provided as class-level declarations
    to satisfy type checkers while allowing mixins to be composed.

    Example:
        ```python
        class PlayerQueryBuilder(QueryBuilder, LocationFiltersMixin):
            # Inherits country(), state(), city() methods

        # Usage
        query = client.player.query().country("US").state("WA").city("Seattle")
        results = query.get()
        ```
    """

    # Type annotations required for mixin methods
    _params: dict[str, Any]

    def country(self, country_code: str) -> Self:
        """Filter by country.

        Args:
            country_code: Country name or 2-digit ISO country code (e.g., "US", "CA")

        Returns:
            New query builder instance with the country filter applied

        Example:
            ```python
            # Filter by country code
            results = client.player.query().country("US").get()

            # Reusable base query
            us_query = client.player.query().country("US")
            wa_players = us_query.state("WA").get()
            or_players = us_query.state("OR").get()
            ```
        """
        clone = self._clone()  # type: ignore[attr-defined]
        clone._params["country"] = country_code
        return clone  # type: ignore[no-any-return]

    def state(self, stateprov: str) -> Self:
        """Filter by state or province.

        Args:
            stateprov: 2-character state or province code (e.g., "WA", "BC", "ON")

        Returns:
            New query builder instance with the state/province filter applied

        Example:
            ```python
            # US state
            results = client.player.query().state("WA").get()

            # Canadian province
            results = client.player.query().country("CA").state("BC").get()
            ```
        """
        clone = self._clone()  # type: ignore[attr-defined]
        clone._params["stateprov"] = stateprov
        return clone  # type: ignore[no-any-return]

    def city(self, city: str) -> Self:
        """Filter by city.

        Args:
            city: City name (partial strings may be accepted depending on API)

        Returns:
            New query builder instance with the city filter applied

        Example:
            ```python
            # Filter by city
            results = (client.director.query()
                .country("US")
                .state("WA")
                .city("Seattle")
                .get())
            ```
        """
        clone = self._clone()  # type: ignore[attr-defined]
        clone._params["city"] = city
        return clone  # type: ignore[no-any-return]


class PaginationMixin:
    """Mixin providing common pagination methods for query builders.

    This mixin adds limit and offset pagination capabilities to query builders.
    It follows the immutable query builder pattern where each method returns a new
    instance, enabling safe query composition and reuse.

    The mixin expects the query builder to:
    - Have a _params dict[str, Any] attribute
    - Implement a _clone() -> Self method

    The limit() method maps to the "count" parameter in the IFPA API.
    The offset() method maps to the "start_pos" parameter in the IFPA API.

    Example:
        ```python
        class PlayerQueryBuilder(QueryBuilder, PaginationMixin):
            # Inherits limit(), offset() methods

        # Usage - paginate through results
        page_size = 25
        page_1 = client.player.query("Smith").limit(page_size).get()
        page_2 = client.player.query("Smith").offset(25).limit(page_size).get()
        page_3 = client.player.query("Smith").offset(50).limit(page_size).get()
        ```
    """

    # Type annotations required for mixin methods
    _params: dict[str, Any]

    def limit(self, count: int) -> Self:
        """Set maximum number of results to return.

        This method maps to the IFPA API's "count" parameter.

        Important: API behavior varies by endpoint type:
        - **Search endpoints** (player, director, tournament): Return fixed 50-result
          pages. The count parameter is ignored. Use offset() to navigate pages.
        - **Rankings endpoints**: Count parameter is honored, variable result sizes supported.

        Args:
            count: Maximum number of results to return (must be positive)

        Returns:
            New query builder instance with the limit set

        Example:
            ```python
            # Rankings - count is honored
            rankings = client.rankings.wppr(count=10)  # Returns 10 results

            # Player search - count is ignored, returns 50
            players = client.player.query("Smith").limit(10).get()  # Returns 50 results

            # Use offset() for pagination on search endpoints
            page1 = client.player.query("Smith").offset(0).get()   # First 50
            page2 = client.player.query("Smith").offset(50).get()  # Next 50
            ```
        """
        clone = self._clone()  # type: ignore[attr-defined]
        clone._params["count"] = count
        return clone  # type: ignore[no-any-return]

    def offset(self, start_position: int) -> Self:
        """Set pagination offset (starting position).

        This method maps to the IFPA API's "start_pos" parameter. The SDK uses
        0-based indexing for consistency with Python conventions, but internally
        converts to the API's 1-based indexing.

        Args:
            start_position: Starting position for pagination (0-based index)

        Returns:
            New query builder instance with the offset set

        Example:
            ```python
            # Get second page of results (assuming 25 per page)
            results = client.player.query("Smith").offset(25).limit(25).get()

            # Skip first 100 results
            results = client.player.query().country("US").offset(100).get()
            ```
        """
        clone = self._clone()  # type: ignore[attr-defined]
        clone._params["start_pos"] = start_position + 1
        return clone  # type: ignore[no-any-return]
