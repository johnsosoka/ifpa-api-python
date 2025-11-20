"""Director resource client - main entry point.

Provides callable client for director operations with query builder support.
"""

from ifpa_api.core.base import BaseResourceClient
from ifpa_api.core.deprecation import issue_deprecation_warning
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.models.director import CountryDirectorsResponse, Director

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

    def get(self, director_id: int | str) -> Director:
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
            director = client.director.get(1000)

            # Old way (still works but deprecated)
            director = client.director(1000).details()
            ```
        """
        return self(director_id).details()

    def get_or_none(self, director_id: int | str) -> Director | None:
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
            director = client.director.get_or_none(1000)
            if director:
                print(f"Found: {director.name}")
            else:
                print("Director not found")
            ```
        """
        try:
            return self.get(director_id)
        except IfpaApiError as e:
            if e.status_code == 404:
                return None
            raise

    def exists(self, director_id: int | str) -> bool:
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
            if client.director.exists(1000):
                print("Director exists!")
            else:
                print("Director not found")
            ```
        """
        return self.get_or_none(director_id) is not None

    def search(self, name: str = "") -> DirectorQueryBuilder:
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
            results = client.director.search("Josh").get()

            # Chained filters
            results = (client.director.search("Sharpe")
                .country("US")
                .state("IL")
                .limit(25)
                .get())

            # Filter-only search (no name query)
            results = (client.director.search()
                .country("CA")
                .get())
            ```
        """
        builder = DirectorQueryBuilder(self._http)
        if name:
            return builder.query(name)
        return builder

    def query(self, name: str = "") -> DirectorQueryBuilder:
        """Create a fluent query builder for searching directors (deprecated).

        .. deprecated:: 0.4.0
            Use :meth:`search` instead. This method will be removed in version 1.0.0.

        Args:
            name: Optional director name to search for (can also be set via .query() on builder)

        Returns:
            DirectorQueryBuilder instance for building the search query
        """
        issue_deprecation_warning(
            old_name="query()",
            new_name="search()",
            version="1.0.0",
            additional_info="The search() method provides the same functionality.",
        )
        return self.search(name)

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
