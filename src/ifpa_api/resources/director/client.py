"""Director resource client - main entry point.

Provides callable client for director operations with query builder support.
"""

import warnings

from ifpa_api.core.base import BaseResourceClient
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

    def search(self, name: str = "") -> DirectorQueryBuilder:
        """Search for directors by name (preferred method).

        This is the preferred method for searching directors. The .query() method is deprecated
        and will be removed in v5.0.0.

        Args:
            name: Name to search for (optional, can be empty to search all)

        Returns:
            DirectorQueryBuilder instance for chaining filters

        Example:
            ```python
            # Search by name
            results = client.director.search("Josh").get()

            # Search all with filters
            results = client.director.search().country("US").limit(10).get()

            # Chained filters
            results = (client.director.search("Sharpe")
                .country("US")
                .state("IL")
                .city("Chicago")
                .limit(25)
                .get())

            # Query reuse (immutable pattern)
            us_base = client.director.search().country("US")
            il_directors = us_base.state("IL").get()
            or_directors = us_base.state("OR").get()  # base unchanged!
            ```
        """
        builder = DirectorQueryBuilder(self._http)
        if name:
            return builder.query(name)
        return builder

    def query(self, name: str = "") -> DirectorQueryBuilder:
        """DEPRECATED: Search for directors by name.

        .. deprecated:: 4.0.0
           Use :meth:`search` instead. This method will be removed in v5.0.0.

        Args:
            name: Name to search for

        Returns:
            DirectorQueryBuilder instance

        Example:
            ```python
            # Old way (deprecated)
            results = client.director.query("Josh").get()

            # New way (preferred)
            results = client.director.search("Josh").get()
            ```
        """
        warnings.warn(
            "The .query() method is deprecated and will be removed in v5.0.0. "
            "Please use .search() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.search(name)

    def list_country_directors(self) -> CountryDirectorsResponse:
        """List directors by country (preferred name for consistency).

        Returns:
            Response containing directors grouped by country

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            directors = client.director.list_country_directors()
            for director in directors.country_directors:
                print(f"{director.name} - {director.country_name}")
            ```
        """
        response = self._http._request("GET", "/director/country")
        return CountryDirectorsResponse.model_validate(response)

    def country_directors(self) -> CountryDirectorsResponse:
        """DEPRECATED: List directors by country.

        .. deprecated:: 4.0.0
           Use :meth:`list_country_directors` instead for naming consistency.
           This method will be removed in v5.0.0.

        Returns:
            Response containing directors grouped by country

        Example:
            ```python
            # Old way (deprecated)
            directors = client.director.country_directors()

            # New way (preferred)
            directors = client.director.list_country_directors()
            ```
        """
        warnings.warn(
            "The .country_directors() method is deprecated. "
            "Use .list_country_directors() instead for naming consistency. "
            "This method will be removed in v5.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.list_country_directors()

    def get(self, director_id: int | str) -> Director:
        """Get director by ID.

        Args:
            director_id: The director's unique identifier

        Returns:
            Director object with complete director information

        Raises:
            IfpaApiError: If director not found (404) or other API error

        Example:
            ```python
            director = client.director.get(1533)
            print(f"{director.first_name} {director.last_name}")
            ```
        """
        return self(director_id).details()

    def get_or_none(self, director_id: int | str) -> Director | None:
        """Get director by ID, returning None if not found.

        Args:
            director_id: The director's unique identifier

        Returns:
            Director object if found, None if not found (404)

        Raises:
            IfpaApiError: For API errors other than 404

        Example:
            ```python
            director = client.director.get_or_none(1533)
            if director:
                print(f"Found: {director.first_name} {director.last_name}")
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
        """Check if director exists.

        Args:
            director_id: The director's unique identifier

        Returns:
            True if director exists, False otherwise

        Example:
            ```python
            if client.director.exists(1533):
                print("Director exists!")
            ```
        """
        return self.get_or_none(director_id) is not None
