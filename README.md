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
- **Pydantic Validation**: Request and response validation with detailed error messages
- **Query Builder Pattern**: Composable, immutable queries with method chaining
- **36 API Endpoints**: Complete coverage of IFPA API v2.1 across 6 resources
- **96% Test Coverage**: Comprehensive unit and integration tests
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
    print(f"{result.position}. {result.player_name}: {result.wppr_points} pts")

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
all_series = client.series.list_series()
active_only = client.series.list_series(active=True)
```

### Reference Data

```python
# Get countries and states
countries = client.reference.countries()
states = client.reference.state_provs(country_code="US")
```

## Exception Handling

```python
from ifpa_api import IfpaClient, IfpaApiError, MissingApiKeyError

try:
    client = IfpaClient()  # Raises if no API key found
    player = client.player(99999999).details()
except MissingApiKeyError:
    print("No API key provided or found in environment")
except IfpaApiError as e:
    print(f"API error: {e.status_code} - {e.response_body}")
```

Exception hierarchy:

```
IfpaError (base)
├── MissingApiKeyError - No API key provided
├── IfpaApiError - API returned error (has status_code, response_body)
└── IfpaClientValidationError - Request validation failed
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
