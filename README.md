# IFPA API Client

[![Development Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/johnsosoka/ifpa-api-python)
[![PyPI version](https://img.shields.io/pypi/v/ifpa-api.svg)](https://pypi.org/project/ifpa-api/)
[![Python versions](https://img.shields.io/pypi/pyversions/ifpa-api.svg)](https://pypi.org/project/ifpa-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/johnsosoka/ifpa-api-python/workflows/CI/badge.svg)](https://github.com/johnsosoka/ifpa-api-python/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/johnsosoka/ifpa-api-python/branch/main/graph/badge.svg)](https://codecov.io/gh/johnsosoka/ifpa-api-python)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://johnsosoka.github.io/ifpa-api-python/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Note**: This is an unofficial client library, not affiliated with or endorsed by IFPA.

A typed Python client for the [IFPA (International Flipper Pinball Association) API](https://api.ifpapinball.com/). Access player rankings, tournament data, and statistics through a clean, type-safe Python interface with Pydantic validation.

**Complete documentation**: https://johnsosoka.github.io/ifpa-api-python/

## What's New in 1.0.0

**🚀 Full Async Support** - Modern async/await API alongside existing sync client:

```python
from ifpa_api import AsyncIfpaClient
import asyncio

async def main():
    # Async context manager for automatic cleanup
    async with AsyncIfpaClient() as client:
        # All operations use async/await
        player = await client.player.get(12345)
        rankings = await client.rankings.wppr(count=100)

        # Query builders work the same (filters are sync, execution is async)
        results = await client.player.search("Smith").country("US").get()

        # Concurrent requests for better performance
        player, director, tournament = await asyncio.gather(
            client.player.get(12345),
            client.director.get(456),
            client.tournament.get(789)
        )

asyncio.run(main())
```

**Dual Client Support** - Choose sync or async based on your needs:
- `IfpaClient` - Synchronous client (unchanged, 100% backward compatible)
- `AsyncIfpaClient` - New async client with httpx for modern async applications
- Both clients share the same API surface and models

**Quality of Life Improvements** (from 0.3.0-0.4.0) - Enhanced debugging, pagination, and error handling:

```python
from ifpa_api import (
    IfpaClient,
    IfpaApiError,
    SeriesPlayerNotFoundError,
    TournamentNotLeagueError,
)

# 1. Enhanced Error Messages - Full request context in exceptions
try:
    player = client.player.get(99999)
except IfpaApiError as e:
    print(e)  # "[404] Resource not found (URL: https://api.ifpapinball.com/player/99999)"
    print(e.request_url)  # Direct access to URL
    print(e.request_params)  # Direct access to query parameters

# 2. Pagination Helpers - Automatic pagination for large result sets
for player in client.player.search().country("US").iterate(limit=100):
    print(f"{player.first_name} {player.last_name}")

all_players = client.player.search().country("US").state("WA").get_all()

# 3. Semantic Exceptions - Clear, specific errors for common scenarios
try:
    card = client.series("PAPA").player_card(12345, "OH")
except SeriesPlayerNotFoundError as e:
    print(f"Player {e.player_id} has no results in {e.series_code}")

# 4. Better Validation Messages - Helpful hints for validation errors
# Input error now shows: "Invalid parameter 'country': Input should be a valid string
#                        Hint: Country code should be a 2-letter string like 'US' or 'CA'"
```

**Query Builder Pattern** - Build complex queries with a fluent, type-safe interface:

```python
# Immutable query builders allow reuse
us_players = client.player.search().country("US")
wa_results = us_players.state("WA").limit(25).get()
or_results = us_players.state("OR").limit(25).get()  # Base query unchanged

# Chain filters naturally
tournaments = client.tournament.search("Championship") \
    .country("US") \
    .date_range("2024-01-01", "2024-12-31") \
    .limit(50) \
    .get()

# Filter without search terms
results = client.player.search() \
    .tournament("PAPA") \
    .position(1) \
    .get()
```

**Unified Callable Pattern** - All resources now follow the same intuitive pattern:

```python
# Individual resource access (preferred methods)
player = client.player.get(12345)
director = client.director.get(456)
tournament = client.tournament.get(789)

# Collection queries
players = client.player.search("John").get()
directors = client.director.search("Josh").get()
tournaments = client.tournament.search("PAPA").get()

# Series operations
standings = client.series("NACS").standings()
```

**Migration from 0.3.x**: Version 0.4.0 introduces preferred convenience methods. See the [Migration Guide](#migration-guide) for details.

## Features

- **🔄 Async & Sync Support**: Choose between `AsyncIfpaClient` (async/await) or `IfpaClient` (synchronous) - same API, your choice
- **⚡ Modern Async**: Built with httpx for concurrent requests and better performance in async applications
- **📘 Full Type Safety**: Complete type hints for IDE autocompletion and static analysis
- **✅ Pydantic Validation**: Request and response validation with helpful error hints
- **🔗 Query Builder Pattern**: Composable, immutable queries with method chaining
- **📄 Automatic Pagination**: Memory-efficient iteration with `.iterate()` and `.get_all()`
- **🐛 Enhanced Error Context**: All exceptions include request URLs and parameters for debugging
- **🎯 Semantic Exceptions**: Domain-specific errors (PlayersNeverMetError, SeriesPlayerNotFoundError, etc.)
- **🌐 46 API Endpoints**: Complete coverage of IFPA API v2.1 across 7 resources
- **🧪 99% Test Coverage**: Comprehensive unit and integration tests (548 tests passing)
- **🔒 Context Manager Support**: Automatic resource cleanup for both sync and async
- **🛡️ Clear Error Handling**: Structured exception hierarchy for different failure modes

## Installation

```bash
pip install ifpa-api
```

Requires Python 3.11 or higher.

## Quick Start

```python
from ifpa_api import IfpaClient

# Initialize with API key
client = IfpaClient(api_key='your-api-key-here')

# Get player profile and rankings
player = client.player.get(2643)
print(f"{player.first_name} {player.last_name}")
print(f"WPPR Rank: {player.player_stats.current_wppr_rank}")
print(f"WPPR Points: {player.player_stats.current_wppr_value}")

# Search players with filters
results = client.player.search("John") \
    .country("US") \
    .state("CA") \
    .limit(10) \
    .get()

for player in results.search:
    print(f"{player.first_name} {player.last_name} - {player.city}")

# Get tournament results
tournament = client.tournament.get(67890)
print(f"{tournament.tournament_name}")
print(f"Date: {tournament.event_date}")
print(f"Players: {tournament.tournament_stats.total_players}")

results = client.tournament.get_results(67890)
for result in results.results[:5]:
    print(f"{result.position}. {result.player_name}: {result.points} pts")

# Automatic pagination for large datasets
for player in client.player.search().country("US").iterate(limit=100):
    print(f"{player.first_name} {player.last_name}")

# Close client when done
client.close()
```

### Using Environment Variable

Set `IFPA_API_KEY` to avoid passing the key in code:

```bash
export IFPA_API_KEY='your-api-key-here'
```

```python
from ifpa_api import IfpaClient

# API key automatically loaded from environment
client = IfpaClient()
```

### Context Manager Pattern

```python
from ifpa_api import IfpaClient

with IfpaClient(api_key='your-api-key-here') as client:
    player = client.player.get(12345)
    print(player.first_name)
# Client automatically closed
```

## Async Quick Start

For async applications, use `AsyncIfpaClient` with the same API:

```python
from ifpa_api import AsyncIfpaClient
import asyncio

async def main():
    # Always use async context manager
    async with AsyncIfpaClient(api_key='your-api-key-here') as client:
        # Get player profile and rankings (with await)
        player = await client.player.get(2643)
        print(f"{player.first_name} {player.last_name}")
        print(f"WPPR Rank: {player.player_stats.current_wppr_rank}")

        # Search players with filters (query builders work the same)
        results = await client.player.search("John") \
            .country("US") \
            .state("CA") \
            .limit(10) \
            .get()

        for player in results.search:
            print(f"{player.first_name} {player.last_name} - {player.city}")

        # Concurrent requests for better performance
        player, tournament = await asyncio.gather(
            client.player.get(12345),
            client.tournament.get(67890)
        )

        # Async pagination
        async for player in client.player.search().country("US").iterate(limit=100):
            print(f"{player.first_name} {player.last_name}")

    # Client automatically closed

# Run async code
asyncio.run(main())
```

**Key Differences:**
- Import `AsyncIfpaClient` instead of `IfpaClient`
- Use `async with` for context manager
- Add `await` before all client method calls
- Use `async for` for iteration
- Filter methods (`.country()`, `.state()`, `.limit()`) are still sync - only `.get()` needs `await`

## Core Resources

### Players

```python
# Search with filters
results = client.player.search("Smith") \
    .country("US") \
    .tournament("PAPA") \
    .position(1) \
    .limit(25) \
    .get()

# Individual player operations
from ifpa_api.models.common import RankingSystem, ResultType

# Preferred method
player = client.player.get(12345)

# Other player operations (still use callable pattern)
results = client.player(12345).results(RankingSystem.MAIN, ResultType.ACTIVE)
pvp = client.player(12345).pvp(67890)  # Head-to-head comparison
history = client.player(12345).history()

# Convenience methods
player_or_none = client.player.get_or_none(99999)  # Returns None if not found
exists = client.player.exists(12345)  # Boolean check
first_smith = client.player.search("Smith").first()  # Get first result
```

### Directors

```python
# Search for directors
results = client.director.search("Josh") \
    .city("Seattle") \
    .state("WA") \
    .get()

# Individual director operations
# Preferred method
director = client.director.get(1533)

# Other director operations
tournaments = client.director.get_tournaments(1533, TimePeriod.PAST)

# Collection operations
country_dirs = client.director.country_directors()

# Convenience methods
director_or_none = client.director.get_or_none(99999)  # Returns None if not found
first_josh = client.director.search("Josh").first()  # Get first result
```

### Tournaments

```python
# Search with date range
results = client.tournament.search("Championship") \
    .country("US") \
    .date_range("2024-01-01", "2024-12-31") \
    .limit(50) \
    .get()

# Individual tournament operations
# Preferred method
tournament = client.tournament.get(12345)

# Other tournament operations
results = client.tournament.get_results(12345)
formats = client.tournament.get_formats(12345)

# Convenience methods
tournament_or_none = client.tournament.get_or_none(99999)  # Returns None if not found
first_papa = client.tournament.search("PAPA").first()  # Get first result
```

### Rankings

```python
# Various ranking types
wppr = client.rankings.wppr(count=100)
women = client.rankings.women(count=50)
youth = client.rankings.youth(count=50)
country = client.rankings.by_country("US", count=100)

# Age-based rankings
seniors = client.rankings.age_based(50, 59, count=50)

# Custom rankings and lists
countries = client.rankings.country_list()
custom_systems = client.rankings.custom_list()
```

### Series

```python
# Series operations
standings = client.series("NACS").standings()
card = client.series("PAPA").player_card(12345, region_code="OH")
regions = client.series("IFPA").regions(region_code="R1")

# List all series
all_series = client.series.list()
active_only = client.series.list(active=True)
```

### Reference Data

```python
# Get countries and states
countries = client.reference.countries()
states = client.reference.state_provs(country_code="US")
```

### Stats

```python
# Get overall IFPA statistics
stats = client.stats.overall()
print(f"Active players: {stats.stats.active_player_count:,}")
print(f"Tournaments this year: {stats.stats.tournament_count_this_year:,}")

# Get top point earners for a time period
points = client.stats.points_given_period(
    start_date="2024-01-01",
    end_date="2024-12-31",
    limit=25
)
for player in points.stats[:10]:
    print(f"{player.first_name} {player.last_name}: {player.wppr_points} pts")

# Get largest tournaments
tournaments = client.stats.largest_tournaments(country_code="US")
for tourney in tournaments.stats[:10]:
    print(f"{tourney.tournament_name}: {tourney.player_count} players")

# Get player counts by country
country_stats = client.stats.country_players()
for country in country_stats.stats[:10]:
    print(f"{country.country_name}: {country.player_count:,} players")

# Get most active players in a time period
active_players = client.stats.events_attended_period(
    start_date="2024-01-01",
    end_date="2024-12-31",
    country_code="US",
    limit=25
)
```

## Pagination

The SDK provides two methods for handling large result sets with automatic pagination:

### Memory-Efficient Iteration

Use `.iterate()` to process results one at a time without loading everything into memory:

```python
# Iterate through all US players efficiently
for player in client.player.search().country("US").iterate(limit=100):
    print(f"{player.first_name} {player.last_name} - {player.city}")
    # Process each player individually

# Iterate through tournament results with filters
for tournament in client.tournament.search("Championship").country("US").iterate():
    print(f"{tournament.tournament_name} - {tournament.event_date}")
```

### Collect All Results

Use `.get_all()` when you need all results in a list:

```python
# Get all players from Washington state
all_players = client.player.search().country("US").state("WA").get_all()
print(f"Total players: {len(all_players)}")

# Safety limit to prevent excessive memory usage
try:
    results = client.player.search().country("US").get_all(max_results=1000)
except ValueError as e:
    print(f"Too many results: {e}")
```

**Best Practices:**
- Use `.iterate()` for large datasets or when processing items one at a time
- Use `.get_all()` for smaller datasets when you need the complete list
- Always set `max_results` when using `.get_all()` to prevent memory issues
- Default batch size is 100 items per request; adjust with `limit` parameter if needed

## Exception Handling

The SDK provides a structured exception hierarchy with enhanced error context for debugging.

### Basic Error Handling

```python
from ifpa_api import IfpaClient, IfpaApiError, MissingApiKeyError

try:
    client = IfpaClient()  # Raises if no API key found
    player = client.player.get(99999999)
except MissingApiKeyError:
    print("No API key provided or found in environment")
except IfpaApiError as e:
    print(f"API error [{e.status_code}]: {e.message}")
    print(f"Request URL: {e.request_url}")
    print(f"Request params: {e.request_params}")
```

### Semantic Exceptions

The SDK raises domain-specific exceptions for common error scenarios:

```python
from ifpa_api import (
    IfpaClient,
    PlayersNeverMetError,
    SeriesPlayerNotFoundError,
    TournamentNotLeagueError,
)

client = IfpaClient(api_key='your-api-key')

# Players who have never competed together
try:
    comparison = client.player.get_pvp(12345, 67890)
except PlayersNeverMetError as e:
    print(f"Players {e.player_id} and {e.opponent_id} have never met in competition")

# Player not found in series
try:
    card = client.series("PAPA").player_card(12345, "OH")
except SeriesPlayerNotFoundError as e:
    print(f"Player {e.player_id} has no results in {e.series_code} series")
    print(f"Region: {e.region_code}")

# Non-league tournament
try:
    league = client.tournament.get_league(12345)
except TournamentNotLeagueError as e:
    print(f"Tournament {e.tournament_id} is not a league-format tournament")
```

### Exception Hierarchy

```
IfpaError (base)
├── MissingApiKeyError - No API key provided
├── IfpaApiError - API returned error (has status_code, response_body, request_url, request_params)
│   ├── PlayersNeverMetError - Players have never competed together
│   ├── SeriesPlayerNotFoundError - Player not found in series/region
│   └── TournamentNotLeagueError - Tournament is not a league format
└── IfpaClientValidationError - Request validation failed (includes helpful hints)
```

### Enhanced Error Context

All API errors (v0.3.0+) include full request context:

```python
try:
    results = client.player.search("John").country("INVALID").get()
except IfpaApiError as e:
    # Access error details
    print(f"Status: {e.status_code}")
    print(f"Message: {e.message}")
    print(f"URL: {e.request_url}")
    print(f"Params: {e.request_params}")
    print(f"Response: {e.response_body}")
```

## Convenience Methods

The SDK provides several convenience methods to make common operations more ergonomic:

### Direct Resource Access

```python
# Get a resource by ID (preferred method)
player = client.player.get(12345)
director = client.director.get(1533)
tournament = client.tournament.get(7070)

# Get or None (no exception on 404)
player = client.player.get_or_none(12345)
if player:
    print(f"Found: {player.first_name} {player.last_name}")
else:
    print("Player not found")

# Check if resource exists
if client.player.exists(12345):
    print("Player exists!")
```

### Search Convenience

```python
# Get first search result (raises IndexError if none)
player = client.player.search("Smith").first()
print(f"First match: {player.first_name} {player.last_name}")

# Get first result or None (safe for empty results)
player = client.player.search("Smith").first_or_none()
if player:
    print(f"Found: {player.first_name}")
else:
    print("No matches found")

# Works with all searchable resources
director = client.director.search("Josh").first()
tournament = client.tournament.search("PAPA").first()
```

These convenience methods are available for Player, Director, and Tournament resources.

## Migration Guide

### Migration from 0.3.x to 0.4.x

Version 0.4.0 introduces preferred convenience methods. Old methods still work but issue deprecation warnings:

| Deprecated (0.3.x) | Preferred (0.4.x) | Notes |
|--------------------|-------------------|-------|
| `client.player(id).details()` | `client.player.get(id)` | More direct and intuitive |
| `client.player.query("name")` | `client.player.search("name")` | Clearer naming |
| `client.director(id).details()` | `client.director.get(id)` | Consistent pattern |
| `client.director.query("name")` | `client.director.search("name")` | Clearer naming |
| `client.tournament(id).details()` | `client.tournament.get(id)` | More direct |
| `client.tournament.query("name")` | `client.tournament.search("name")` | Clearer naming |

Example migration:

```python
# Old (0.3.x - deprecated but still works)
player = client.player(12345).details()
results = client.player.query("John").get()
tournament = client.tournament(67890).details()

# New (0.4.x - preferred)
player = client.player.get(12345)
results = client.player.search("John").get()
tournament = client.tournament.get(67890)

# New convenience methods (0.4.x only)
player = client.player.get_or_none(12345)  # Returns None on 404
exists = client.player.exists(12345)  # Boolean check
first = client.player.search("Smith").first()  # First result
maybe_first = client.player.search("Smith").first_or_none()  # First or None
```

### Migration from 0.2.x to 0.3.x

| 0.2.x | 0.3.0+ |
|-------|-------|
| `client.tournaments` | `client.tournament` |
| `client.player.search("name")` | `client.player.search("name").get()` (or use new syntax) |
| `client.tournament(id).get()` | `client.tournament.get(id)` |
| `client.series_handle("CODE")` | `client.series("CODE")` |

See the [CHANGELOG](CHANGELOG.md) for complete migration details.

## Development

### Setup

```bash
# Clone and install dependencies
git clone https://github.com/johnsosoka/ifpa-api-python.git
cd ifpa-api-python
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Set API key for integration tests
export IFPA_API_KEY='your-api-key'
```

### Testing

```bash
# Run unit tests (no API key required)
poetry run pytest tests/unit/ -v

# Run all tests including integration (requires API key)
poetry run pytest -v

# Run with coverage
poetry run pytest --cov=ifpa_api --cov-report=term-missing
```

### Code Quality

```bash
# Format code
poetry run black src tests

# Lint
poetry run ruff check src tests --fix

# Type check
poetry run mypy src

# Run all checks
poetry run pre-commit run --all-files
```

## Resources

- **Documentation**: https://johnsosoka.github.io/ifpa-api-python/
- **PyPI Package**: https://pypi.org/project/ifpa-api/
- **GitHub Repository**: https://github.com/johnsosoka/ifpa-api-python
- **Issue Tracker**: https://github.com/johnsosoka/ifpa-api-python/issues
- **IFPA API Documentation**: https://api.ifpapinball.com/docs

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:

- Setting up your development environment
- Code quality standards (Black, Ruff, mypy)
- Writing and running tests
- Submitting pull requests

You can also contribute by:
- Reporting bugs
- Requesting features
- Providing feedback on usability and documentation

## License

MIT License - Copyright (c) 2025 John Sosoka

See the [LICENSE](LICENSE) file for details.

---

**Maintainer**: [John Sosoka](https://johnsosoka.com) | [open.source@sosoka.com](mailto:open.source@sosoka.com)

Built for the worldwide pinball community.
