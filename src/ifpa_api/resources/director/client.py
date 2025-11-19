"""Director resource client - main entry point.

Provides callable client for director operations with query builder support.
"""

from ifpa_api.core.base import BaseResourceClient
from ifpa_api.models.director import CountryDirectorsResponse

from .context import _DirectorContext
from .query_builder import DirectorQueryBuilder


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
