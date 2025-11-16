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

#### `directors`

Returns the directors resource client.

```python
@property
def directors(self) -> DirectorsClient
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

#### `director(director_id)`

Get a handle for a specific tournament director.

```python
def director(self, director_id: int | str) -> DirectorHandle
```

**Parameters:**

- `director_id` (int | str): The director's unique identifier

**Returns:**

- `DirectorHandle`: Handle for director-specific operations

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
