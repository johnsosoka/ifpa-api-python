# Client Reference

The `IfpaClient` is the main entry point for the IFPA SDK.

## SDK Architecture

The IFPA SDK is organized into several key modules that work together to provide access to the IFPA API.

### Module Structure

```
ifpa_api/
├── client.py          # Main IfpaClient facade
├── core/              # Core infrastructure
│   ├── base.py        # Base classes and mixins
│   ├── config.py      # Configuration management
│   ├── exceptions.py  # Custom exceptions
│   ├── http.py        # HTTP client layer
│   └── query_builder.py # Query builder base
├── models/            # Pydantic models for all resources
│   ├── common.py      # Shared enums and models
│   ├── director.py    # Director models
│   ├── player.py      # Player models
│   ├── rankings.py    # Rankings models
│   ├── tournaments.py # Tournament models
│   ├── series.py      # Series models
│   ├── stats.py       # Stats models
│   ├── reference.py   # Reference data models
│   └── calendar.py    # Calendar models
└── resources/         # Resource clients and handles
    ├── director.py    # DirectorClient (callable pattern)
    ├── player.py      # PlayerClient (callable pattern)
    ├── rankings.py    # RankingsClient
    ├── tournaments.py # TournamentsClient, TournamentHandle
    ├── series.py      # SeriesClient, SeriesHandle
    ├── stats.py       # StatsClient
    └── reference.py   # ReferenceClient
```

### Public API

The SDK exposes the following public API:

**Client:**
- `IfpaClient` - Main client facade

**Enums:**
- `TimePeriod` - PAST, FUTURE
- `RankingSystem` - MAIN, WOMEN, YOUTH, VIRTUAL, PRO
- `ResultType` - ACTIVE, NONACTIVE, INACTIVE
- `TournamentType` - OPEN, WOMEN, YOUTH, etc.

**Exceptions:**
- `IfpaError` - Base exception
- `MissingApiKeyError` - No API key
- `IfpaApiError` - API error
- `IfpaClientValidationError` - Validation error

**Quick Reference:**

```python
from ifpa_api import (
    IfpaClient,
    TimePeriod,
    RankingSystem,
    ResultType,
    TournamentType,
    IfpaError,
    IfpaApiError,
    MissingApiKeyError,
    IfpaClientValidationError,
)
```

## IfpaClient

### Constructor

```python
def __init__(
    self,
    api_key: str | None = None,
    *,
    base_url: str | None = None,
    timeout: float = 10.0,
    validate_requests: bool = True,
) -> None
```

**Parameters:**

- `api_key` (str | None): API key for authentication. If not provided, reads from `IFPA_API_KEY` environment variable.
- `base_url` (str | None): Base URL for the API. Defaults to `https://api.ifpapinball.com`.
- `timeout` (float): Request timeout in seconds. Defaults to 10.0.
- `validate_requests` (bool): Enable request parameter validation. Defaults to True.

**Raises:**

- `MissingApiKeyError`: If no API key is provided and `IFPA_API_KEY` environment variable is not set.

### Properties

#### `director`

Returns the director resource client. Supports both collection operations and callable pattern for individual director access.

```python
@property
def director(self) -> DirectorClient
```

**Usage:**

```python
# Collection operations
results = client.director.query("Josh").get()  # Query directors
results = client.director.query("Josh").country("US").state("IL").get()  # With filters
country_dirs = client.director.country_directors()  # Get country directors

# Individual director operations (callable pattern)
director = client.director(1533).details()  # Get Josh Rainwater's details
tournaments = client.director(1533).tournaments(TimePeriod.PAST)  # Get tournaments
```

#### `player`

Returns the players resource client. Supports both collection operations and callable pattern for individual player access.

```python
@property
def player(self) -> PlayersClient
```

**Usage:**

```python
# Collection operations
results = client.player.query("Smith").state("ID").get()  # Query Idaho Smiths
results = client.player.query("Smith").state("ID").country("US").limit(10).get()  # With filters

# Individual player operations (callable pattern)
player = client.player(25584).details()  # Get Dwayne Smith's details
pvp = client.player(25584).pvp(47585)    # Compare Dwayne vs Debbie
```

#### `rankings`

Returns the rankings resource client.

```python
@property
def rankings(self) -> RankingsClient
```

#### `tournaments`

Returns the tournaments resource client.

```python
@property
def tournaments(self) -> TournamentsClient
```

#### `series`

Returns the series resource client. Supports both collection operations and callable pattern for individual series access.

```python
@property
def series(self) -> SeriesClient
```

**Usage:**

```python
# Collection operations
all_series = client.series.list()  # List all series
active = client.series.list(active_only=True)  # List active series only

# Individual series operations (callable pattern)
standings = client.series("NACS").standings()  # Get overall standings
card = client.series("PAPA").player_card(12345, "OH")  # Get player's series card
region = client.series("NACS").region_standings("OH")  # Get region standings
```

#### `stats`

Returns the stats resource client.

```python
@property
def stats(self) -> StatsClient
```

**Usage:**

```python
# Geographic statistics
country_stats = client.stats.country_players(rank_type="OPEN")
state_stats = client.stats.state_players()

# Historical trends
events = client.stats.events_by_year()
players = client.stats.players_by_year()

# Tournament rankings
largest = client.stats.largest_tournaments()
lucrative = client.stats.lucrative_tournaments(major="Y")

# Player activity over time
points = client.stats.points_given_period(
    start_date="2024-01-01",
    end_date="2024-12-31"
)
active = client.stats.events_attended_period(
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# Overall IFPA statistics
overall = client.stats.overall(system_code="OPEN")
```

#### `reference`

Returns the reference data client.

```python
@property
def reference(self) -> ReferenceClient
```

### Methods

#### Accessing Individual Directors

Individual director operations are accessed through the callable pattern on the `director` property:

```python
# Access via callable pattern - Example with Josh Rainwater (1533)
director_handle = client.director(1533)

# Then call methods on the handle
director = director_handle.details()  # Get director profile
past = director_handle.tournaments(TimePeriod.PAST)  # Get past tournaments
future = director_handle.tournaments(TimePeriod.FUTURE)  # Get upcoming tournaments
```

**Note:** The `client.director` property returns a `DirectorClient` which is callable, providing a unified interface for both collection and resource-specific operations.

#### Accessing Individual Players

Individual player operations are accessed through the callable pattern on the `player` property:

```python
# Access via callable pattern - Example with Dwayne Smith (25584)
player_handle = client.player(25584)

# Then call methods on the handle
player = player_handle.details()  # Get player profile
results = player_handle.results(RankingSystem.MAIN, ResultType.ACTIVE)  # Get tournament results
pvp = player_handle.pvp(47585)  # Compare with Debbie Smith
history = player_handle.history()  # Get ranking history
```

**Note:** The `client.player` property returns a `PlayersClient` which is callable, providing a unified interface for both collection and resource-specific operations.

#### `tournament(tournament_id)`

Get a handle for a specific tournament.

```python
def tournament(self, tournament_id: int | str) -> TournamentHandle
```

**Parameters:**

- `tournament_id` (int | str): The tournament's unique identifier

**Returns:**

- `TournamentHandle`: Handle for tournament-specific operations

#### `close()`

Close the HTTP client session.

```python
def close(self) -> None
```

### Context Manager Support

The client supports Python's context manager protocol:

```python
def __enter__(self) -> IfpaClient
def __exit__(self, exc_type, exc_val, exc_tb) -> None
```

**Usage:**

```python
with IfpaClient() as client:
    player = client.player(12345).details()
# Client automatically closed
```

For detailed usage examples, see the [Quick Start Guide](../getting-started/quickstart.md).
