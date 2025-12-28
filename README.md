# IFPA API Client

[![Development Status](https://img.shields.io/badge/status-beta-blue.svg)](https://github.com/johnsosoka/ifpa-api-python)
[![PyPI version](https://img.shields.io/pypi/v/ifpa-api.svg)](https://pypi.org/project/ifpa-api/)
[![Python versions](https://img.shields.io/pypi/pyversions/ifpa-api.svg)](https://pypi.org/project/ifpa-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/johnsosoka/ifpa-api-python/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/johnsosoka/ifpa-api-python/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/johnsosoka/ifpa-api-python/branch/main/graph/badge.svg)](https://codecov.io/gh/johnsosoka/ifpa-api-python)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue.svg)](https://johnsosoka.github.io/ifpa-api-python/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Note**: This is an unofficial client library, not affiliated with or endorsed by IFPA.

A typed Python client for the [IFPA (International Flipper Pinball Association) API](https://api.ifpapinball.com/). Access player rankings, tournament data, and statistics through a clean, type-safe Python interface with Pydantic validation.

**Complete documentation**: https://johnsosoka.github.io/ifpa-api-python/

## What's New in 0.4.0

**GitHub Pages Documentation** - Professional documentation hosting:

The complete documentation is now hosted on GitHub Pages for improved accessibility and discoverability. Visit https://johnsosoka.github.io/ifpa-api-python/ for guides, API reference, and examples.

**Type-Safe Enums** - Enhanced type safety for rankings and tournaments:

```python
from ifpa_api import IfpaClient, RankingDivision, TournamentSearchType

client = IfpaClient(api_key="your-api-key")

# Rankings with type-safe enum
rankings = client.rankings.women(
    tournament_type=RankingDivision.OPEN,
    count=50
)

# Tournament search with type-safe enum
tournaments = (client.tournament.search("Championship")
    .tournament_type(TournamentSearchType.WOMEN)
    .country("US")
    .get())

# IDE autocomplete shows available options
# - RankingDivision.OPEN / RankingDivision.WOMEN
# - TournamentSearchType.OPEN / WOMEN / YOUTH / LEAGUE

# Strings still work (backward compatible)
rankings = client.rankings.women(tournament_type="OPEN", count=50)
```

**Benefits:**
- Type safety: Catch invalid values at development time
- IDE autocomplete: Discover available division types
- Self-documenting: Clear what values are valid
- No breaking changes: Existing code continues to work

This release includes stats resource with 10 endpoints, type-safe enums for stats parameters, enhanced error messages, pagination helpers, and query builder pattern. See [CHANGELOG](CHANGELOG.md) for details.

## Features

- **Full Type Safety**: Complete type hints for IDE autocompletion and static analysis
- **Pydantic Validation**: Request and response validation with helpful error hints
- **Query Builder Pattern**: Composable, immutable queries with method chaining
- **Automatic Pagination**: Memory-efficient iteration with `.iterate()` and `.get_all()`
- **Enhanced Error Context**: All exceptions include request URLs and parameters for debugging
- **Semantic Exceptions**: Domain-specific errors (PlayersNeverMetError, SeriesPlayerNotFoundError, etc.)
- **46 API Endpoints**: Complete coverage of IFPA API v2.1 across 7 resources
- **99% Test Coverage**: Comprehensive unit and integration tests
- **Context Manager Support**: Automatic resource cleanup
- **Clear Error Handling**: Structured exception hierarchy for different failure modes

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

# Search for players with filters
results = client.player.search("John") \
    .country("US") \
    .state("CA") \
    .limit(10) \
    .get()

for player in results.search:
    print(f"{player.first_name} {player.last_name} - {player.city}")

# Get tournament details
tournament = client.tournament.get(67890)
print(f"{tournament.tournament_name}")
print(f"Date: {tournament.event_date}")
print(f"Players: {tournament.tournament_stats.total_players}")

# Get tournament results
results = client.tournament(67890).results()
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

# Convenience methods for individual players
player = client.player.get(12345)
player = client.player.get_or_none(12345)  # Returns None if not found
if client.player.exists(12345):
    print("Player exists!")

# Get first search result
first = client.player.search("Smith").first()
maybe_first = client.player.search("Rare Name").first_or_none()

# Individual player operations (using context)
from ifpa_api.models.common import RankingSystem, ResultType

results = client.player(12345).results(RankingSystem.MAIN, ResultType.ACTIVE)
pvp = client.player(12345).pvp(67890)  # Head-to-head comparison
history = client.player(12345).history()
```

### Directors

```python
# Search for directors
results = client.director.search("Josh") \
    .city("Seattle") \
    .state("WA") \
    .get()

# Convenience methods for individual directors
director = client.director.get(1533)
director = client.director.get_or_none(1533)  # Returns None if not found
if client.director.exists(1533):
    print("Director exists!")

# Individual director operations (using context)
from ifpa_api.models.common import TimePeriod

tournaments = client.director(1533).tournaments(TimePeriod.PAST)

# Collection operations
country_dirs = client.director.list_country_directors()
```

### Tournaments

```python
# Search with date range
results = client.tournament.search("Championship") \
    .country("US") \
    .date_range("2024-01-01", "2024-12-31") \
    .limit(50) \
    .get()

# Convenience methods for individual tournaments
tournament = client.tournament.get(12345)
tournament = client.tournament.get_or_none(12345)  # Returns None if not found
if client.tournament.exists(12345):
    print("Tournament exists!")

# Individual tournament operations (using context)
results = client.tournament(12345).results()
formats = client.tournament(12345).formats()
league = client.tournament(12345).league()  # For league-format tournaments

# List all tournament formats
all_formats = client.tournament.list_formats()
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
# Convenience methods for series
standings = client.series.get("NACS")
standings = client.series.get_or_none("NACS")  # Returns None if not found
if client.series.exists("NACS"):
    print("Series exists!")

# Individual series operations (using context)
from ifpa_api.models.common import TimePeriod

card = client.series("PAPA").player_card(12345, region_code="OH")
regions = client.series("IFPA").regions(region_code="R1", year=2024)
overview = client.series("NACS").overview(time_period=TimePeriod.CURRENT)

# List all series
all_series = client.series.list_series()
active_only = client.series.list_series(active_only=True)
```

### Stats

```python
from ifpa_api import IfpaClient, StatsRankType, SystemCode, MajorTournament

client = IfpaClient()

# Get overall IFPA statistics
stats = client.stats.overall(system_code=SystemCode.OPEN)
print(f"Active players: {stats.stats.active_player_count:,}")
print(f"Tournaments this year: {stats.stats.tournament_count_this_year:,}")

# Get top point earners for a time period
points = client.stats.points_given_period(
    rank_type=StatsRankType.OPEN,
    start_date="2024-01-01",
    end_date="2024-12-31",
    limit=25
)
for player in points.stats[:10]:
    print(f"{player.first_name} {player.last_name}: {player.wppr_points} pts")

# Get largest tournaments
tournaments = client.stats.largest_tournaments(
    rank_type=StatsRankType.OPEN,
    country_code="US"
)
for tourney in tournaments.stats[:10]:
    print(f"{tourney.tournament_name}: {tourney.player_count} players")

# Get player counts by country (women's rankings)
country_stats = client.stats.country_players(rank_type=StatsRankType.WOMEN)
for country in country_stats.stats[:10]:
    print(f"{country.country_name}: {country.player_count:,} players")

# Get most active players in a time period
active_players = client.stats.events_attended_period(
    rank_type=StatsRankType.OPEN,
    start_date="2024-01-01",
    end_date="2024-12-31",
    country_code="US",
    limit=25
)
```

**Type Safety**: Stats methods accept typed enums (e.g., `StatsRankType.WOMEN`) or strings for backwards compatibility.

### Reference Data

```python
# Get countries and states
countries = client.reference.countries()
states = client.reference.state_provs(country_code="US")
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
    comparison = client.player(12345).pvp(67890)
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
    league = client.tournament(12345).league()
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

## Migration from 0.2.x

### Quick Reference

| 0.2.x | 0.4.0 (Preferred) |
|-------|-------|
| `client.tournaments` | `client.tournament` |
| `client.player.search("name")` | `client.player.search("name").get()` |
| `client.player(id).details()` | `client.player.get(id)` |
| `client.tournament(id).get()` | `client.tournament.get(id)` |
| `client.series_handle("CODE")` | `client.series.get("CODE")` |
| `client.director.country_directors()` | `client.director.list_country_directors()` |

### Query Builder Migration

```python
# Before (0.2.x)
results = client.player.search(name="John", country="US")

# After (0.4.0 - Preferred)
results = client.player.search("John").country("US").get()

# New capabilities - query reuse with immutable pattern
base_query = client.player.search().country("US")
wa_players = base_query.state("WA").get()
or_players = base_query.state("OR").get()  # Original query unchanged

# Filter without search term
winners = client.player.search().tournament("PAPA").position(1).get()

# Convenience methods for getting first result
first = client.player.search("Smith").first()
maybe_first = client.player.search("Rare").first_or_none()
```

### Resource Access Pattern Changes

```python
# Before (0.2.x and 0.3.0)
tournament = client.tournament(12345).details()
player = client.player(12345).details()
standings = client.series_handle("NACS").standings()

# After (0.4.0 - Preferred)
tournament = client.tournament.get(12345)
player = client.player.get(12345)
standings = client.series.get("NACS")

# New convenience methods
player = client.player.get_or_none(12345)  # Returns None instead of raising
if client.player.exists(12345):
    print("Player exists!")
```

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
