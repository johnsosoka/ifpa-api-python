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

## What's New in 0.3.0

**Quality of Life Improvements** - Enhanced debugging, pagination, and error handling:

```python
from ifpa_api import (
    IfpaClient,
    IfpaApiError,
    SeriesPlayerNotFoundError,
    TournamentNotLeagueError,
)

# 1. Enhanced Error Messages - Full request context in exceptions
try:
    player = client.player(99999).details()
except IfpaApiError as e:
    print(e)  # "[404] Resource not found (URL: https://api.ifpapinball.com/player/99999)"
    print(e.request_url)  # Direct access to URL
    print(e.request_params)  # Direct access to query parameters

# 2. Pagination Helpers - Automatic pagination for large result sets
for player in client.player.query().country("US").iterate(limit=100):
    print(f"{player.first_name} {player.last_name}")

all_players = client.player.query().country("US").state("WA").get_all()

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
us_players = client.player.query().country("US")
wa_results = us_players.state("WA").limit(25).get()
or_results = us_players.state("OR").limit(25).get()  # Base query unchanged

# Chain filters naturally
tournaments = client.tournament.query("Championship") \
    .country("US") \
    .date_range("2024-01-01", "2024-12-31") \
    .limit(50) \
    .get()

# Filter without search terms
results = client.player.query() \
    .tournament("PAPA") \
    .position(1) \
    .get()
```

**Unified Callable Pattern** - All resources now follow the same intuitive pattern:

```python
# Individual resource access
player = client.player(12345).details()
director = client.director(456).details()
tournament = client.tournament(789).details()

# Collection queries
players = client.player.query("John").get()
directors = client.director.query("Josh").get()
tournaments = client.tournament.query("PAPA").get()

# Series operations
standings = client.series("NACS").standings()
```

**Breaking Changes**: Users upgrading from 0.2.x should review the [Migration Guide](#migration-from-02x).

## Features

- **Full Type Safety**: Complete type hints for IDE autocompletion and static analysis
- **Pydantic Validation**: Request and response validation with helpful error hints
- **Query Builder Pattern**: Composable, immutable queries with method chaining
- **Automatic Pagination**: Memory-efficient iteration with `.iterate()` and `.get_all()`
- **Enhanced Error Context**: All exceptions include request URLs and parameters for debugging
- **Semantic Exceptions**: Domain-specific errors (PlayersNeverMetError, SeriesPlayerNotFoundError, etc.)
- **36 API Endpoints**: Complete coverage of IFPA API v2.1 across 6 resources
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
player = client.player(2643).details()
print(f"{player.first_name} {player.last_name}")
print(f"WPPR Rank: {player.player_stats.current_wppr_rank}")
print(f"WPPR Points: {player.player_stats.current_wppr_value}")

# Query players with filters
results = client.player.query("John") \
    .country("US") \
    .state("CA") \
    .limit(10) \
    .get()

for player in results.search:
    print(f"{player.first_name} {player.last_name} - {player.city}")

# Get tournament results
tournament = client.tournament(67890).details()
print(f"{tournament.tournament_name}")
print(f"Date: {tournament.event_date}")
print(f"Players: {tournament.tournament_stats.total_players}")

results = client.tournament(67890).results()
for result in results.results[:5]:
    print(f"{result.position}. {result.player_name}: {result.points} pts")

# Automatic pagination for large datasets
for player in client.player.query().country("US").iterate(limit=100):
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
    player = client.player(12345).details()
    print(player.first_name)
# Client automatically closed
```

## Core Resources

### Players

```python
# Query with filters
results = client.player.query("Smith") \
    .country("US") \
    .tournament("PAPA") \
    .position(1) \
    .limit(25) \
    .get()

# Individual player operations
from ifpa_api.models.common import RankingSystem, ResultType

player = client.player(12345).details()
results = client.player(12345).results(RankingSystem.MAIN, ResultType.ACTIVE)
pvp = client.player(12345).pvp(67890)  # Head-to-head comparison
history = client.player(12345).history()
```

### Directors

```python
# Query for directors
results = client.director.query("Josh") \
    .city("Seattle") \
    .state("WA") \
    .get()

# Individual director operations
director = client.director(1533).details()
tournaments = client.director(1533).tournaments(TimePeriod.PAST)

# Collection operations
country_dirs = client.director.country_directors()
```

### Tournaments

```python
# Query with date range
results = client.tournament.query("Championship") \
    .country("US") \
    .date_range("2024-01-01", "2024-12-31") \
    .limit(50) \
    .get()

# Individual tournament operations
tournament = client.tournament(12345).details()
results = client.tournament(12345).results()
formats = client.tournament(12345).formats()
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

## Pagination

The SDK provides two methods for handling large result sets with automatic pagination:

### Memory-Efficient Iteration

Use `.iterate()` to process results one at a time without loading everything into memory:

```python
# Iterate through all US players efficiently
for player in client.player.query().country("US").iterate(limit=100):
    print(f"{player.first_name} {player.last_name} - {player.city}")
    # Process each player individually

# Iterate through tournament results with filters
for tournament in client.tournament.query("Championship").country("US").iterate():
    print(f"{tournament.tournament_name} - {tournament.event_date}")
```

### Collect All Results

Use `.get_all()` when you need all results in a list:

```python
# Get all players from Washington state
all_players = client.player.query().country("US").state("WA").get_all()
print(f"Total players: {len(all_players)}")

# Safety limit to prevent excessive memory usage
try:
    results = client.player.query().country("US").get_all(max_results=1000)
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
    player = client.player(99999999).details()
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
    results = client.player.query("John").country("INVALID").get()
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

| 0.2.x | 0.3.0 |
|-------|-------|
| `client.tournaments` | `client.tournament` |
| `client.player.search("name")` | `client.player.query("name").get()` |
| `client.tournament(id).get()` | `client.tournament(id).details()` |
| `client.series_handle("CODE")` | `client.series("CODE")` |

### Query Builder Migration

```python
# Before (0.2.x)
results = client.player.search(name="John", country="US")

# After (0.3.0)
results = client.player.query("John").country("US").get()

# New capabilities - query reuse
base_query = client.player.query().country("US")
wa_players = base_query.state("WA").get()
or_players = base_query.state("OR").get()

# Filter without search term
winners = client.player.query().tournament("PAPA").position(1).get()
```

### Callable Pattern Changes

```python
# Before (0.2.x)
tournament = client.tournament(12345).get()
standings = client.series_handle("NACS").standings()

# After (0.3.0)
tournament = client.tournament(12345).details()
standings = client.series("NACS").standings()
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
