# Resource API Standards

**Version:** 0.5.0
**Last Updated:** 2025-11-22
**Status:** Active Standard

## Purpose

This document defines architectural patterns, naming conventions, and implementation requirements for resource clients in the IFPA API Python SDK. These standards ensure API consistency, type safety, and maintainability across all resources.

Engineers implementing new resources or refactoring existing ones must follow these requirements.

## Table of Contents

1. [Architecture](#architecture)
2. [Naming Conventions](#naming-conventions)
3. [QueryBuilder Implementation](#querybuilder-implementation)
4. [Error Handling](#error-handling)
5. [Type Safety](#type-safety-standards)
6. [Testing Requirements](#testing-requirements)
7. [Deprecation Strategy](#deprecation-strategy)
8. [Documentation Standards](#documentation-standards)
9. [Implementation Checklist](#checklist-for-new-resources)

---

## Architecture

### File Organization

Resources must be organized as Python packages with clear separation of concerns:

```
src/ifpa_api/resources/<resource>/
├── __init__.py          # Public exports (Client, QueryBuilder)
├── client.py            # Resource client with collection operations
├── context.py           # Context for ID-based operations (optional)
└── query_builder.py     # Fluent query interface (optional)
```

**Component Decision Matrix:**

| Component | Required When | Example |
|-----------|---------------|---------|
| `client.py` | Always | All resources |
| `context.py` | Resource has ID-based operations | Player, Director, Tournament |
| `query_builder.py` | Resource supports search/filtering | Player search, Tournament search |

### Inheritance Requirements

All resource components must inherit from base classes in `ifpa_api.core.base`:

```python
from ifpa_api.core.base import BaseResourceClient, BaseResourceContext

class ResourceClient(BaseResourceClient):
    """
    Inherits:
    - _http: _HttpClient instance
    - _validate_requests: bool flag
    """
    pass

class _ResourceContext(BaseResourceContext[int | str]):
    """
    Inherits:
    - _http: _HttpClient instance
    - _resource_id: Generic ID type
    - _validate_requests: bool flag
    """
    pass
```

**Benefits:**
- Eliminates ~200 lines of boilerplate per resource
- Enforces consistent initialization patterns
- Provides type-safe generic ID handling

### Three-Layer Pattern

Resources follow a consistent three-layer architecture:

```
┌─────────────────────────────────────────┐
│         IfpaClient (Facade)             │
│  - Single entry point                   │
│  - Lazy-loaded resource properties      │
└────────────────┬────────────────────────┘
                 │
┌────────────────┴────────────────────────┐
│    Resource Client (Collection Ops)     │
│  - .search() → QueryBuilder             │
│  - .get(id) → Resource                  │
│  - .list_*() → Collections              │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼──────────────┐  ┌───────▼─────────────┐
│  QueryBuilder    │  │  Context (ID-based) │
│  - Fluent search │  │  - .details()       │
│  - Filters       │  │  - .results()       │
│  - Pagination    │  │  - Domain methods   │
└──────────────────┘  └─────────────────────┘
```

**Usage Examples:**

```python
# Layer 1: Facade entry
client = IfpaClient(api_key="...")

# Layer 2: Collection operations
results = client.player.search("Smith")  # Returns QueryBuilder
player = client.player.get(12345)        # Direct access

# Layer 3: Fluent building & ID-based operations
results = client.player.search("Smith").country("US").get()
rankings = client.player(12345).rankings()  # Context pattern
```

---

## Naming Conventions

Consistent naming eliminates API confusion and improves discoverability.

### Client Method Names

#### Search Operations

**Standard:** `.search(name="")`

```python
def search(self, name: str = "") -> ResourceQueryBuilder:
    """Search for resources by name with optional filters.

    Args:
        name: Search term (optional for collection browsing)

    Returns:
        Query builder for chaining filters

    Example:
        >>> results = client.player.search("John").country("US").get()
        >>> all_players = client.player.search().limit(100).get()
    """
```

**Deprecated:** `.query()` (use `.search()` instead as of v0.4.0)

#### Direct Access

**Standard:** `.get(id)`, `.get_or_none(id)`, `.exists(id)`

```python
def get(self, resource_id: int | str) -> Resource:
    """Get resource by ID.

    Args:
        resource_id: Unique resource identifier

    Returns:
        Resource instance

    Raises:
        IfpaApiError: If resource not found (404) or API error

    Example:
        >>> player = client.player.get(12345)
        >>> print(f"{player.first_name} {player.last_name}")
    """
    return self(resource_id).details()

def get_or_none(self, resource_id: int | str) -> Resource | None:
    """Get resource by ID, returning None if not found.

    Args:
        resource_id: Unique resource identifier

    Returns:
        Resource instance or None if 404

    Example:
        >>> player = client.player.get_or_none(99999)
        >>> if player:
        ...     print(f"Found: {player.first_name}")
        ... else:
        ...     print("Player not found")
    """
    try:
        return self.get(resource_id)
    except IfpaApiError as e:
        if e.status_code == 404:
            return None
        raise

def exists(self, resource_id: int | str) -> bool:
    """Check if resource exists.

    Args:
        resource_id: Unique resource identifier

    Returns:
        True if resource exists, False otherwise

    Example:
        >>> if client.player.exists(12345):
        ...     print("Player exists in database")
    """
    return self.get_or_none(resource_id) is not None
```

#### Collection Operations

**Standard:** `list_<collection_name>()`

Always use the `list_` prefix for consistency:

```python
# Good
def list_formats(self) -> TournamentFormatsListResponse:
    """List available tournament formats."""

def list_country_directors(self) -> CountryDirectorsResponse:
    """List directors by country."""

def list_series(self, active_only: bool = True) -> SeriesListResponse:
    """List active series."""

# Avoid
def formats(self) -> ...        # Missing 'list_' prefix
def country_directors(self) -> ...  # Missing 'list_' prefix
def get_all(self) -> ...       # Ambiguous, use list_*
```

### Context Method Names

**Standard:** `.details()` for primary resource info, domain-specific names for operations

```python
class _PlayerContext(BaseResourceContext[int | str]):
    def details(self) -> Player:
        """Get player profile details."""

    def rankings(self) -> PlayerRankingsResponse:
        """Get player's current rankings."""

    def results(self, system: RankingSystem, ...) -> PlayerResultsResponse:
        """Get player's tournament results."""

    def pvp(self, opponent_id: int) -> PvpComparison:
        """Get head-to-head comparison with opponent."""
```

**Naming Rules:**
- `.details()` always returns primary resource representation
- Use nouns for data retrieval (`.rankings()`, `.results()`, `.history()`)
- Use verbs only when operation performs an action
- Match domain terminology (PvP, not "versus" or "compare")

### QueryBuilder Method Names

#### Filter Methods

```python
# Location filters (via LocationFiltersMixin)
.country(code: str)      # Country filter
.state(code: str)        # State/province filter
.city(name: str)         # City filter

# Pagination (via PaginationMixin)
.limit(count: int)       # Result limit (maps to 'count' param)
.offset(position: int)   # Result offset (maps to 'start_pos' param)

# Domain-specific filters
.tournament(name: str)           # Filter by tournament participation
.date_range(start: str, end: str)  # Date range (YYYY-MM-DD)
.tournament_type(type: Enum)     # Type filter with enum support
```

#### Execution Methods

```python
# From QueryBuilder base class
.get() -> Response              # Execute query, return full response
.first() -> Item                # Get first result, raise if empty
.first_or_none() -> Item | None # Get first result, None if empty
.iterate() -> Iterator[Item]    # Memory-efficient pagination
.get_all() -> list[Item]        # Collect all results (memory intensive)
```

---

## QueryBuilder Implementation

### The Immutable Pattern

**CRITICAL:** All QueryBuilder implementations must use the immutable pattern via `._clone()`.

```python
def filter_method(self, value: str) -> Self:
    """Apply filter (creates new instance)."""
    clone = self._clone()  # REQUIRED: Create new instance
    clone._params["key"] = value
    return clone
```

**Why Immutable?**

The immutable pattern enables query reuse without side effects:

```python
# Create base query
us_query = client.player.search().country("US")

# Derive multiple queries from base - each creates new instance
wa_players = us_query.state("WA").get()
or_players = us_query.state("OR").get()
ca_players = us_query.state("CA").get()

# Base query unchanged - can be reused safely
midwest_query = us_query.state("IL")
```

Without immutability, modifying a derived query would corrupt the base query, leading to unpredictable results.

### Parameter Overwriting Detection

**Standard:** Raise `ValueError` when a parameter is set multiple times in the same chain.

```python
def country(self, country_code: str) -> Self:
    """Filter by country.

    Raises:
        ValueError: If country() called multiple times in same chain
    """
    clone = self._clone()

    # Detect duplicate parameter
    if "country" in clone._params:
        raise ValueError(
            f"country() called multiple times in query chain. "
            f"Previous value: '{clone._params['country']}', "
            f"Attempted value: '{country_code}'. "
            f"This is likely a mistake. Create a new query to change filters."
        )

    clone._params["country"] = country_code
    return clone
```

**Why Detect Overwrites?**

Silent overwriting leads to debugging nightmares:

```python
# Without detection - last value silently wins
query = (client.player.search()
    .country("US")  # User expects US results
    .country("CA")  # Oops! Now searching CA, no error
    .get())

# With detection - immediate feedback
>>> query = client.player.search().country("US").country("CA")
ValueError: country() called multiple times in query chain.
Previous value: 'US', Attempted value: 'CA'.
```

### Response Extraction

Override `._extract_results()` when the response field name differs from `search`:

```python
def _extract_results(self, response: DirectorSearchResponse) -> list[Any]:
    """Override to use correct response field.

    Args:
        response: The search response

    Returns:
        List of results from the response
    """
    return response.directors  # Not response.search
```

**Response Field Mapping:**

| Resource | Response Field | Override Required? |
|----------|---------------|-------------------|
| Player | `response.search` | No (default) |
| Director | `response.directors` | **Yes** |
| Tournament | `response.tournaments` | **Yes** |
| Series | `response.series` | **Yes** |

Overriding ensures `.iterate()`, `.get_all()`, `.first()`, and `.first_or_none()` work correctly.

### Using Mixins

Leverage mixins for common functionality:

```python
from ifpa_api.core.base import LocationFiltersMixin, PaginationMixin
from ifpa_api.core.query_builder import QueryBuilder

class PlayerQueryBuilder(
    QueryBuilder[PlayerSearchResponse],
    LocationFiltersMixin,  # Adds .country(), .state(), .city()
    PaginationMixin,       # Adds .limit(), .offset()
):
    def __init__(self, http: _HttpClient) -> None:
        super().__init__()
        self._http = http

    def tournament(self, tournament_name: str) -> Self:
        """Filter by tournament participation."""
        clone = self._clone()
        if "tournament" in clone._params:
            raise ValueError(
                f"tournament() called multiple times. "
                f"Previous: '{clone._params['tournament']}', "
                f"New: '{tournament_name}'"
            )
        clone._params["tournament"] = tournament_name
        return clone

    def get(self) -> PlayerSearchResponse:
        """Execute query and return results."""
        response = self._http._request("GET", "/player/search", params=self._params)
        return PlayerSearchResponse.model_validate(response)
```

**Available Mixins:**

| Mixin | Methods | Use Case |
|-------|---------|----------|
| `LocationFiltersMixin` | `.country()`, `.state()`, `.city()` | Geographic filtering |
| `PaginationMixin` | `.limit()`, `.offset()` | Result pagination |

---

## Error Handling

### Input Validation

**When to Validate:**
- Date formats and ranges
- Mutually required parameters
- Invalid parameter combinations

**Where to Validate:**
- In filter methods for immediate feedback
- In `.get()` method as final check before API call

```python
def date_range(self, start_date: str, end_date: str) -> Self:
    """Set date range filter.

    Args:
        start_date: Start date (YYYY-MM-DD format)
        end_date: End date (YYYY-MM-DD format)

    Raises:
        ValueError: If dates missing or invalid format
        IfpaClientValidationError: If dates fail validation
    """
    # Check both provided
    if not start_date or not end_date:
        raise ValueError("Both start_date and end_date must be provided")

    # Validate format
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(date_pattern, start_date):
        raise IfpaClientValidationError(
            f"Invalid start_date format: '{start_date}'. Expected YYYY-MM-DD"
        )
    if not re.match(date_pattern, end_date):
        raise IfpaClientValidationError(
            f"Invalid end_date format: '{end_date}'. Expected YYYY-MM-DD"
        )

    clone = self._clone()
    clone._params["start_date"] = start_date
    clone._params["end_date"] = end_date
    return clone
```

### Semantic Exceptions

Create domain-specific exceptions for expected error conditions:

```python
# Good - semantic exceptions
class PlayersNeverMetError(IfpaApiError):
    """Raised when PvP query finds no shared tournament history."""

class TournamentNotLeagueError(IfpaApiError):
    """Raised when league data requested for non-league tournament."""

class SeriesPlayerNotFoundError(IfpaApiError):
    """Raised when player has no results in specified series."""

# Usage in context methods
def pvp(self, opponent_id: int | str) -> PvpComparison:
    """Get head-to-head comparison with another player."""
    response = self._http._request(
        "GET",
        f"/player/{self._resource_id}/pvp/{opponent_id}"
    )

    # API returns 200 with error message when players never met
    if isinstance(response, dict) and response.get("code") == "404":
        raise PlayersNeverMetError(
            f"Players {self._resource_id} and {opponent_id} have never "
            f"competed in the same tournament"
        )

    return PvpComparison.model_validate(response)
```

**Benefits:**
- Enables targeted exception handling
- Self-documenting error conditions
- Better error messages for users

### 404 Handling Pattern

Standard pattern for `.get_or_none()` convenience methods:

```python
def get_or_none(self, resource_id: int | str) -> Resource | None:
    """Get resource, return None on 404."""
    try:
        return self.get(resource_id)
    except IfpaApiError as e:
        if e.status_code == 404:
            return None
        raise  # Re-raise other errors (5xx, 403, etc.)
```

---

## Type Safety Standards

### 100% Type Coverage Required

- All public APIs must have complete type hints
- Run mypy in strict mode (`mypy --strict src/`)
- No `Any` types without documented justification

```python
# Good - fully typed
def search(self, name: str = "") -> PlayerQueryBuilder:
    """Search players by name."""
    return PlayerQueryBuilder(self._http, name)

def get(self, player_id: int | str) -> Player:
    """Get player by ID."""
    return self(player_id).details()

# Avoid - missing types
def search(self, name=""):  # Missing return type
    return PlayerQueryBuilder(self._http, name)

def get(self, player_id):  # Missing parameter and return types
    return self(player_id).details()
```

### Union Types for Backward Compatibility

Accept both enum and string values for flexibility:

```python
def tournament_type(
    self,
    tournament_type: TournamentSearchType | str
) -> Self:
    """Filter by tournament type.

    Args:
        tournament_type: Tournament type (enum or string)

    Example:
        >>> # Using enum (preferred)
        >>> results = (client.tournament.search()
        ...     .tournament_type(TournamentSearchType.LEAGUE)
        ...     .get())
        >>>
        >>> # Using string (backward compatible)
        >>> results = (client.tournament.search()
        ...     .tournament_type("league")
        ...     .get())
    """
    clone = self._clone()

    # Convert enum to string if needed
    type_value = (
        tournament_type.value
        if isinstance(tournament_type, TournamentSearchType)
        else tournament_type
    )

    clone._params["tournament_type"] = type_value
    return clone
```

### Generic Type Parameters

Use generics for type-safe QueryBuilder implementations:

```python
from typing import Generic, TypeVar

T = TypeVar("T")  # Response type

class QueryBuilder(ABC, Generic[T]):
    """Base query builder with type-safe response."""

    @abstractmethod
    def get(self) -> T:
        """Return type matches generic parameter."""

# Concrete implementation specifies response type
class PlayerQueryBuilder(QueryBuilder[PlayerSearchResponse]):
    def get(self) -> PlayerSearchResponse:
        """Inherits type safety from generic."""
        response = self._http._request("GET", "/player/search", params=self._params)
        return PlayerSearchResponse.model_validate(response)
```

---

## Testing Requirements

### Unit Test Coverage

**Required tests for each resource:**

#### 1. QueryBuilder Tests

```python
class TestPlayerQueryBuilder:
    """Test QueryBuilder functionality."""

    def test_simple_search(self, mock_requests: requests_mock.Mocker):
        """Test basic search operation."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"query": "John", "search": [sample_player_data]}
        )

        client = IfpaClient(api_key="test-key")
        results = client.player.search("John").get()

        assert isinstance(results, PlayerSearchResponse)
        assert len(results.search) == 1
        assert results.search[0].first_name == "John"

    def test_filter_chaining(self, mock_requests: requests_mock.Mocker):
        """Test multiple filters can be chained."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"query": "Smith", "search": [sample_player_data]}
        )

        client = IfpaClient(api_key="test-key")
        results = (client.player.search("Smith")
            .country("US")
            .state("WA")
            .limit(25)
            .get())

        # Verify all parameters sent
        assert "name=smith" in mock_requests.last_request.query.lower()
        assert "country=us" in mock_requests.last_request.query.lower()
        assert "stateprov=wa" in mock_requests.last_request.query.lower()
        assert "count=25" in mock_requests.last_request.query

    def test_query_immutability(self, mock_requests: requests_mock.Mocker):
        """Test that base query remains unchanged."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"query": "", "search": []}
        )

        client = IfpaClient(api_key="test-key")
        base = client.player.search().country("US")

        # Create derived queries
        wa_query = base.state("WA")
        or_query = base.state("OR")

        wa_query.get()
        or_query.get()

        # Verify base unchanged by checking last two requests
        requests = mock_requests.request_history[-2:]
        assert "stateprov=wa" in requests[0].query.lower()
        assert "stateprov=or" in requests[1].query.lower()
        # Both should still have country=US from base
        assert all("country=us" in r.query.lower() for r in requests)

    def test_parameter_overwriting_raises_error(self):
        """Test that duplicate parameters raise ValueError."""
        client = IfpaClient(api_key="test-key")
        query = client.player.search()

        with pytest.raises(ValueError, match="country\\(\\) called multiple times"):
            query.country("US").country("CA")

    def test_first_method(self, mock_requests: requests_mock.Mocker):
        """Test .first() returns first result."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"query": "Smith", "search": [sample_player_data]}
        )

        client = IfpaClient(api_key="test-key")
        player = client.player.search("Smith").first()

        assert player.first_name == "John"

    def test_first_or_none_empty(self, mock_requests: requests_mock.Mocker):
        """Test .first_or_none() returns None when empty."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"query": "NonexistentName", "search": []}
        )

        client = IfpaClient(api_key="test-key")
        result = client.player.search("NonexistentName").first_or_none()

        assert result is None
```

#### 2. Client Method Tests

```python
class TestPlayerClient:
    """Test client convenience methods."""

    def test_get_success(self, mock_requests: requests_mock.Mocker):
        """Test .get() with valid ID."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/12345",
            json={"player": [sample_player_data]}
        )

        client = IfpaClient(api_key="test-key")
        player = client.player.get(12345)

        assert isinstance(player, Player)
        assert player.player_id == 12345

    def test_get_not_found(self, mock_requests: requests_mock.Mocker):
        """Test .get() raises IfpaApiError on 404."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/99999",
            status_code=404,
            json={"error": "Player not found"}
        )

        client = IfpaClient(api_key="test-key")

        with pytest.raises(IfpaApiError) as exc_info:
            client.player.get(99999)

        assert exc_info.value.status_code == 404

    def test_get_or_none_returns_none(self, mock_requests: requests_mock.Mocker):
        """Test .get_or_none() returns None on 404."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/99999",
            status_code=404,
            json={"error": "Player not found"}
        )

        client = IfpaClient(api_key="test-key")
        result = client.player.get_or_none(99999)

        assert result is None

    def test_exists_true(self, mock_requests: requests_mock.Mocker):
        """Test .exists() returns True when resource found."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/12345",
            json={"player": [sample_player_data]}
        )

        client = IfpaClient(api_key="test-key")
        assert client.player.exists(12345) is True

    def test_exists_false(self, mock_requests: requests_mock.Mocker):
        """Test .exists() returns False on 404."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/99999",
            status_code=404
        )

        client = IfpaClient(api_key="test-key")
        assert client.player.exists(99999) is False
```

#### 3. Deprecation Warning Tests

```python
class TestPlayerDeprecations:
    """Test deprecation warnings."""

    def test_query_method_deprecated(self, mock_requests: requests_mock.Mocker):
        """Test .query() issues deprecation warning."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"query": "John", "search": []}
        )

        client = IfpaClient(api_key="test-key")

        with pytest.warns(DeprecationWarning, match="Use .search\\(\\) instead"):
            client.player.query("John").get()

    def test_warning_stacklevel(self, mock_requests: requests_mock.Mocker):
        """Test warning points to caller's code (stacklevel=2)."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"query": "", "search": []}
        )

        client = IfpaClient(api_key="test-key")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client.player.query().get()  # Line that should be reported

            assert len(w) == 1
            assert "query" in str(w[0].filename).lower()  # Points to this file
```

### Integration Test Requirements

When API key available, test against real API:

```python
@pytest.mark.integration
class TestPlayerIntegration:
    """Integration tests against live API."""

    def test_search_real_player(self, api_key: str):
        """Test search returns real player data."""
        client = IfpaClient(api_key=api_key)
        results = client.player.search("Smith").limit(5).get()

        assert len(results.search) > 0
        assert all(hasattr(p, "player_id") for p in results.search)

    def test_pagination_offset(self, api_key: str):
        """Test pagination with offset works."""
        client = IfpaClient(api_key=api_key)

        page1 = client.player.search("Smith").limit(10).offset(0).get()
        page2 = client.player.search("Smith").limit(10).offset(10).get()

        # Verify different results
        page1_ids = {p.player_id for p in page1.search}
        page2_ids = {p.player_id for p in page2.search}
        assert page1_ids.isdisjoint(page2_ids)
```

---

## Deprecation Strategy

### Adding Deprecation Warnings

Use `warnings.warn()` with `DeprecationWarning` and `stacklevel=2`:

```python
import warnings

def query(self, name: str = "") -> PlayerQueryBuilder:
    """DEPRECATED: Use search() instead.

    .. deprecated:: 0.4.0
       Use :meth:`search` instead. This method will be removed in v1.0.0.

    Example:
        # Old way (deprecated)
        results = client.player.query("John").get()

        # New way (preferred)
        results = client.player.search("John").get()
    """
    warnings.warn(
        "The .query() method is deprecated and will be removed in v1.0.0. "
        "Please use .search() instead for consistent naming across all resources.",
        DeprecationWarning,
        stacklevel=2  # CRITICAL: Points warning to caller's code, not this line
    )
    return self.search(name)
```

**Why `stacklevel=2`?**

```python
# With stacklevel=1 (default) - points to warning line
>>> client.player.query("John")
/path/to/ifpa_api/resources/player/client.py:45: DeprecationWarning
  warnings.warn(...)  # Not helpful for users

# With stacklevel=2 - points to user's code
>>> client.player.query("John")
<stdin>:1: DeprecationWarning: Use .search() instead
  # User sees exactly which line to fix
```

### Deprecation Timeline

```
v0.4.0 (Current)
├─ Add new methods (.search(), .get(), .first())
├─ Add deprecation warnings to old methods (.query())
└─ Both APIs work fully

v0.5.0 - v0.9.x
├─ Maintain both APIs
├─ Continue deprecation warnings
└─ Update documentation to show new methods

v1.0.0 (Breaking)
├─ Remove deprecated methods
├─ Update minimum Python version if needed
└─ Finalize stable API
```

---

## Documentation Standards

### Docstring Format

Use Google-style docstrings with complete sections:

```python
def search(
    self,
    name: str = "",
    limit: int = 50
) -> PlayerQueryBuilder:
    """Search for players by name with optional filters.

    This method returns a QueryBuilder instance that can be further refined
    with filters before executing the query.

    Args:
        name: Player name to search for (partial match supported). Leave empty
            to browse all players.
        limit: Maximum results per page (default: 50). Note: Search endpoints
            ignore this parameter and return fixed 50-result pages.

    Returns:
        Query builder for chaining additional filters and executing search

    Raises:
        IfpaClientValidationError: If parameters fail validation
        IfpaApiError: If API request fails

    Example:
        >>> # Simple search
        >>> results = client.player.search("Smith").get()
        >>> print(f"Found {len(results.search)} players")

        >>> # With filters
        >>> results = (client.player.search("Smith")
        ...     .country("US")
        ...     .state("WA")
        ...     .limit(25)
        ...     .get())

        >>> # Query reuse
        >>> us_query = client.player.search().country("US")
        >>> wa_players = us_query.state("WA").get()
        >>> or_players = us_query.state("OR").get()

    Note:
        Search endpoints return fixed 50-result pages. Use .offset() to
        paginate through results, not .limit().

    See Also:
        - :meth:`get`: Get player by ID directly
        - :meth:`exists`: Check if player exists
    """
```

### Code Example Requirements

All examples must be:
- **Copy-paste ready**: Use actual API patterns, not pseudocode
- **Realistic**: Use plausible values (real player IDs, tournament names)
- **Self-contained**: Include necessary imports and setup
- **Demonstrative**: Show both simple and advanced usage

```python
# Good example - copy-paste ready
>>> from ifpa_api import IfpaClient
>>> client = IfpaClient(api_key="your-key")
>>>
>>> # Get player details
>>> player = client.player.get(12345)
>>> print(f"{player.first_name} {player.last_name}")
John Smith

# Avoid - pseudocode
# Get a player
player = get_player(id)
print(player.name)
```

---

## Checklist for New Resources

When implementing a new resource, verify:

### Architecture
- [ ] Inherits from `BaseResourceClient` or `BaseResourceContext`
- [ ] Follows three-layer pattern (Facade → Client → Context/QueryBuilder)
- [ ] Uses appropriate mixins (`LocationFiltersMixin`, `PaginationMixin`)

### Naming
- [ ] Search method named `.search()`, not `.query()`
- [ ] Direct access uses `.get()`, `.get_or_none()`, `.exists()`
- [ ] Collection methods use `list_*` prefix
- [ ] Context methods use `.details()` for primary resource info

### QueryBuilder
- [ ] Uses immutable pattern via `._clone()`
- [ ] Detects parameter overwriting with `ValueError`
- [ ] Overrides `._extract_results()` if response field != 'search'
- [ ] Implements `.first()` and `.first_or_none()` (inherited from base)

### Error Handling
- [ ] Input validation on complex parameters (dates, ranges)
- [ ] Semantic exceptions for domain-specific errors
- [ ] Standard 404 handling pattern in `.get_or_none()`

### Type Safety
- [ ] 100% type coverage on all public APIs
- [ ] Passes `mypy --strict` without errors
- [ ] Uses union types for enum parameters (Enum | str)
- [ ] Generic type parameters for QueryBuilder responses

### Testing
- [ ] Unit tests for all QueryBuilder methods (15+ tests)
- [ ] Unit tests for client convenience methods (5+ tests)
- [ ] Deprecation warning tests if applicable
- [ ] Integration tests for real API validation

### Documentation
- [ ] Google-style docstrings on all public methods
- [ ] Copy-paste ready examples in docstrings
- [ ] Args, Returns, Raises, Example sections complete
- [ ] Migration guide if deprecating old patterns

---

## References

- **Base Classes:** `src/ifpa_api/core/base.py`
- **QueryBuilder Base:** `src/ifpa_api/core/query_builder.py`
- **Example Implementation:** `src/ifpa_api/resources/player/`
- **Type Safety Guide:** Python typing best practices
- **Testing Guide:** `tests/unit/test_player.py` for patterns

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.5.0 | 2025-11-22 | Initial standard document based on v0.4.0 implementation audit |
