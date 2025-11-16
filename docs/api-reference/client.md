# Client Reference

The `IfpaClient` is the main entry point for the IFPA SDK.

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
results = client.director.search(name="Josh")  # Search directors
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
results = client.player.search(name="Smith", stateprov="ID")  # Search Idaho Smiths
players = client.player.get_multiple([25584, 47585, 52913])  # Get multiple Idaho players

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

Returns the series resource client.

```python
@property
def series(self) -> SeriesClient
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

#### `series_handle(series_code)`

Get a handle for a specific tournament series.

```python
def series_handle(self, series_code: str) -> SeriesHandle
```

**Parameters:**

- `series_code` (str): The series code identifier

**Returns:**

- `SeriesHandle`: Handle for series-specific operations

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
