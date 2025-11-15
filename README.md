# IFPA SDK

[![PyPI version](https://img.shields.io/pypi/v/ifpa-sdk.svg)](https://pypi.org/project/ifpa-sdk/)
[![Python versions](https://img.shields.io/pypi/pyversions/ifpa-sdk.svg)](https://pypi.org/project/ifpa-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A typed Python client for the [IFPA (International Flipper Pinball Association) API](https://api.ifpapinball.com/). Access player rankings, tournament data, statistics, and more with a clean, modern Python interface.

## Features

- **Fully Typed**: Complete type hints for IDE autocompletion and type checking
- **Pydantic Models**: Automatic request/response validation with detailed error messages
- **Resource-Oriented API**: Intuitive access patterns matching the IFPA API structure
- **Comprehensive Coverage**: All 46 IFPA API v2.1 endpoints implemented
- **Handle Pattern**: Fluent interface for resource-specific operations
- **Pagination Support**: Built-in support for paginated endpoints
- **Error Handling**: Clear exception hierarchy for different failure scenarios
- **Well Tested**: 98% test coverage with unit and integration tests

## Installation

```bash
pip install ifpa-sdk
```

Requires Python 3.11 or higher.

## Quick Start

```python
from ifpa_sdk import IfpaClient

# Initialize client (uses IFPA_API_KEY environment variable)
client = IfpaClient()

# Search for players
players = client.players.search(name="John", city="Seattle")
for player in players.players:
    print(f"{player.player_id}: {player.first_name} {player.last_name}")

# Get player details and rankings
player = client.player(12345).get()
print(f"Name: {player.first_name} {player.last_name}")
print(f"Current WPPR Rank: {player.current_wppr_rank}")

# Get top WPPR rankings
rankings = client.rankings.wppr(start_pos=0, count=100)
for entry in rankings.rankings:
    print(f"{entry.rank}. {entry.player_name}: {entry.rating} WPPR")

# Close the client when done
client.close()
```

## Authentication

The SDK requires an IFPA API key. You can obtain one from the [IFPA API documentation](https://api.ifpapinball.com/docs).

### Option 1: Environment Variable (Recommended)

Set the `IFPA_API_KEY` environment variable:

```bash
export IFPA_API_KEY='your-api-key-here'
```

Then initialize the client without parameters:

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()
```

### Option 2: Constructor Parameter

Pass the API key directly to the constructor:

```python
from ifpa_sdk import IfpaClient

client = IfpaClient(api_key='your-api-key-here')
```

## Usage Examples

### Directors

Search for tournament directors and access their tournament history:

```python
from ifpa_sdk import IfpaClient, TimePeriod

client = IfpaClient()

# Search for directors
directors = client.directors.search(name="Josh")
for director in directors.directors:
    print(f"{director.director_id}: {director.first_name} {director.last_name}")

# Get director details
director = client.director(1000).get()
print(f"Director: {director.first_name} {director.last_name}")
print(f"Email: {director.email}")

# Get director's past tournaments
past_tournaments = client.director(1000).tournaments(TimePeriod.PAST)
for tournament in past_tournaments.tournaments:
    print(f"{tournament.tournament_name} ({tournament.event_date})")

# Get director's upcoming tournaments
upcoming = client.director(1000).tournaments(TimePeriod.FUTURE)
```

### Players

Access comprehensive player information, rankings, and tournament history:

```python
from ifpa_sdk import IfpaClient, RankingSystem, ResultType

client = IfpaClient()

# Search for players with filters
players = client.players.search(
    name="Smith",
    city="Portland",
    stateprov="OR",
    start_pos=0,
    count=25
)

# Get player profile
player = client.player(12345).get()
print(f"Name: {player.first_name} {player.last_name}")
print(f"Location: {player.city}, {player.stateprov}")
print(f"Current Rank: {player.current_wppr_rank}")
print(f"Rating: {player.current_wppr_value}")
print(f"Active Events: {player.active_events}")

# Get player rankings across all systems
rankings = client.player(12345).rankings()
for ranking in rankings:
    print(f"{ranking['system']}: Rank {ranking['rank']}")

# Get player's tournament results
results = client.player(12345).results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE,
    start_pos=0,
    count=50
)
for result in results.results:
    print(f"{result.tournament_name}: Placed {result.position}")

# Compare two players head-to-head
pvp = client.player(12345).pvp(67890)
print(f"Player 1 Wins: {pvp.player1_wins}")
print(f"Player 2 Wins: {pvp.player2_wins}")
print(f"Ties: {pvp.ties}")

# Get player's ranking history
history = client.player(12345).history()
for entry in history.history:
    print(f"{entry.date}: Rank {entry.rank}, WPPR {entry.rating}")

# Get player's achievement cards
cards = client.player(12345).cards()
print(f"Total Cards: {len(cards.cards)}")
```

### Rankings

Access various IFPA ranking systems:

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# Get main WPPR rankings
wppr = client.rankings.wppr(start_pos=0, count=100)
for entry in wppr.rankings:
    print(f"{entry.rank}. {entry.player_name}: {entry.rating}")

# Get rankings filtered by country
us_rankings = client.rankings.wppr(country="US", count=50)

# Get women's rankings
women = client.rankings.women(start_pos=0, count=50)

# Get youth rankings
youth = client.rankings.youth(start_pos=0, count=50)

# Get professional circuit rankings
pro = client.rankings.pro(start_pos=0, count=50)

# Get virtual tournament rankings
virtual = client.rankings.virtual(start_pos=0, count=50)

# Get country rankings
countries = client.rankings.by_country(start_pos=0, count=25)
for entry in countries.country_rankings:
    print(f"{entry.rank}. {entry.country_name}: {entry.total_players} players")

# Get age-based rankings
under_18 = client.rankings.age_based("u18", start_pos=0, count=50)

# Get custom ranking system
custom = client.rankings.custom("regional-2024", start_pos=0, count=50)

# Get group rankings
group = client.rankings.group("northwest-league", start_pos=0, count=50)
```

### Tournaments

Search for tournaments and access detailed information:

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# Search for tournaments
tournaments = client.tournaments.search(
    name="Pinball",
    city="Portland",
    stateprov="OR",
    start_pos=0,
    count=25
)
for tournament in tournaments.tournaments:
    print(f"{tournament.tournament_name} ({tournament.event_date})")

# Get tournament details
tournament = client.tournament(12345).get()
print(f"Name: {tournament.tournament_name}")
print(f"Location: {tournament.city}, {tournament.stateprov}")
print(f"Date: {tournament.event_date}")
print(f"Players: {tournament.player_count}")

# Get tournament results
results = client.tournament(12345).results()
for result in results.results:
    print(f"{result.position}. {result.player_name}: {result.points} points")

# Get tournament formats
formats = client.tournament(12345).formats()

# Get league information (if applicable)
league = client.tournament(12345).league()
```

### Series

Access tournament series standings, player cards, and statistics:

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# List all series
all_series = client.series.list()
for series in all_series.series:
    print(f"{series.series_code}: {series.series_name}")

# List only active series
active_series = client.series.list(active_only=True)

# Get series standings
standings = client.series_handle("PAPA").standings(start_pos=0, count=50)
for entry in standings.standings:
    print(f"{entry.position}. {entry.player_name}: {entry.points} points")

# Get player's series card
card = client.series_handle("PAPA").player_card(12345)
print(f"Position: {card.current_position}")
print(f"Total Points: {card.total_points}")
for event in card.events:
    print(f"{event.tournament_name}: {event.points_earned} points")

# Get series overview
overview = client.series_handle("PAPA").overview()
print(f"Series: {overview.series_name}")
print(f"Total Events: {overview.total_events}")
print(f"Total Players: {overview.total_players}")

# Get series regions
regions = client.series_handle("PAPA").regions()
for region in regions.regions:
    print(f"{region.region_name}: {region.player_count} players")

# Get series rules
rules = client.series_handle("PAPA").rules()
print(f"Scoring System: {rules.scoring_system}")

# Get series statistics
stats = client.series_handle("PAPA").stats()
print(f"Total Events: {stats.total_events}")

# Get series schedule
schedule = client.series_handle("PAPA").schedule()
for event in schedule.events:
    print(f"{event.event_date}: {event.event_name}")
```

### Statistics

Access global pinball statistics and trends:

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# Get global statistics
global_stats = client.stats.global_stats()
print(f"Total Players: {global_stats.total_players}")
print(f"Total Tournaments: {global_stats.total_tournaments}")
print(f"Total Countries: {global_stats.total_countries}")

# Get top countries
top_countries = client.stats.top_countries(limit=10)
for country in top_countries.countries:
    print(f"{country.country_name}: {country.player_count} players")

# Get machine popularity
machines = client.stats.machine_popularity(period="year")
for machine in machines.machines:
    print(f"{machine.machine_name}: {machine.play_count} plays")
```

## Configuration

The `IfpaClient` constructor accepts several configuration options:

```python
from ifpa_sdk import IfpaClient

client = IfpaClient(
    api_key='your-api-key',  # API key (or use IFPA_API_KEY env var)
    base_url='https://api.ifpapinball.com',  # Override base URL
    timeout=30.0,  # Request timeout in seconds (default: 10.0)
    validate_requests=True  # Enable Pydantic request validation (default: True)
)
```

### Request Validation

By default, the SDK validates request parameters using Pydantic models before sending requests to the API. This catches invalid parameters early with clear error messages.

To disable validation:

```python
client = IfpaClient(validate_requests=False)
```

## Error Handling

The SDK provides a clear exception hierarchy for different failure scenarios:

```python
from ifpa_sdk import (
    IfpaClient,
    IfpaError,  # Base exception for all SDK errors
    MissingApiKeyError,  # No API key provided or found in environment
    IfpaApiError,  # API returned non-2xx status code
    IfpaClientValidationError  # Request validation failed (when validate_requests=True)
)

client = IfpaClient()

try:
    player = client.player(12345).get()
except MissingApiKeyError:
    print("API key not configured")
except IfpaApiError as e:
    print(f"API error [{e.status_code}]: {e.message}")
except IfpaClientValidationError as e:
    print(f"Invalid request parameters: {e.message}")
except IfpaError as e:
    print(f"SDK error: {e}")
```

## Context Manager

The client supports Python's context manager protocol for automatic resource cleanup:

```python
from ifpa_sdk import IfpaClient

with IfpaClient() as client:
    player = client.player(12345).get()
    rankings = client.rankings.wppr(count=100)
    # Client automatically closed when exiting the context
```

## Testing

The SDK includes comprehensive unit and integration tests.

### Running Unit Tests

Unit tests use `requests-mock` and do not require an API key:

```bash
poetry run pytest tests/unit/
```

### Running Integration Tests

Integration tests make real API calls and require a valid API key:

```bash
export IFPA_API_KEY='your-api-key'
poetry run pytest tests/integration/
```

### Running All Tests with Coverage

```bash
poetry run pytest --cov=ifpa_sdk --cov-report=term-missing
```

### Running Specific Test Markers

```bash
# Skip integration tests
poetry run pytest -m "not integration"

# Only integration tests
poetry run pytest -m integration
```

## Development

### Setup

1. Clone the repository:
```bash
git clone https://github.com/jscom/ifpa-sdk.git
cd ifpa-sdk
```

2. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies:
```bash
poetry install
```

4. Install pre-commit hooks:
```bash
poetry run pre-commit install
```

### Code Quality

The project uses several tools to maintain code quality:

- **Black**: Code formatting (100 character line length)
- **Ruff**: Fast Python linting
- **mypy**: Static type checking
- **pytest**: Testing framework

Run all checks:

```bash
# Format code
poetry run black src tests

# Lint code
poetry run ruff check src tests

# Type check
poetry run mypy src

# Run tests
poetry run pytest
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Key points:
- Fork the repository and create a feature branch
- Write tests for new features
- Ensure all tests pass and code is formatted
- Submit a pull request with a clear description

## API Coverage

The SDK implements all 46 endpoints from IFPA API v2.1:

- **Directors**: 4 endpoints (search, details, tournaments)
- **Players**: 7 endpoints (search, profile, rankings, results, PvP, history, cards)
- **Rankings**: 9 endpoints (WPPR, women, youth, virtual, pro, country, age-based, custom, group)
- **Tournaments**: 6 endpoints (search, details, results, formats, league, submissions)
- **Series**: 8 endpoints (list, standings, player cards, overview, regions, rules, stats, schedule)
- **Stats**: 10 endpoints (global stats, counts, trends, machine popularity)
- **Reference**: 2 endpoints (countries, states)

## Resources

- **IFPA Website**: https://www.ifpapinball.com/
- **IFPA API Documentation**: https://api.ifpapinball.com/docs
- **SDK Documentation**: https://github.com/jscom/ifpa-sdk
- **Issue Tracker**: https://github.com/jscom/ifpa-sdk/issues
- **PyPI Package**: https://pypi.org/project/ifpa-sdk/

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built by [Commerce Architects](https://github.com/jscom) for the pinball community
- Thanks to IFPA for providing the public API
- Special thanks to all contributors and users

## Support

- **Bug Reports**: Open an issue on [GitHub Issues](https://github.com/jscom/ifpa-sdk/issues)
- **Feature Requests**: Open an issue with the `enhancement` label
- **Questions**: Check the [API documentation](https://api.ifpapinball.com/docs) or open a discussion

---

Made with care for the pinball community by [Commerce Architects](https://github.com/jscom)
