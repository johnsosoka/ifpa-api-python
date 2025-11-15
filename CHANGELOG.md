# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2024-11-14

### Added
- `PlayersClient.get_multiple()` method to fetch up to 50 players in a single request
- `PlayerHandle.pvp_all()` method to get PVP competitor summary
- `tournament` parameter to `PlayersClient.search()` for filtering by tournament name
- `tourpos` parameter to `PlayersClient.search()` for filtering by tournament position

### Changed
- **BREAKING**: `PlayerHandle.results()` now requires both `ranking_system` and `result_type` parameters (were optional)
- **BREAKING**: `PlayerHandle.history()` response structure now has separate `rank_history` and `rating_history` arrays (was single `history` array)
- **BREAKING**: `RankingHistory` model field renamed: `ranking_system` → `system`
- **BREAKING**: `RankingHistory` model now has `active_flag` field
- Fixed critical bug: `PlayersClient.search()` parameter mapping (name now correctly maps to "name" query parameter)

### Removed
- **BREAKING**: `PlayerHandle.rankings()` method (endpoint returns 404 - not in API spec)
- **BREAKING**: `PlayerHandle.cards()` method (endpoint returns 404 - not in API spec)

### Migration Guide

#### results() Method

```python
# Before (v0.1.x)
results = client.player(123).results()

# After (v0.2.0) - Both parameters required
from ifpa_api.models.common import RankingSystem, ResultType

results = client.player(123).results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE
)
```

#### history() Method
```python
# Before (v0.1.x)
history = client.player(123).history()
for entry in history.history:
    print(entry.rank, entry.rating)

# After (v0.2.0) - Separate arrays
history = client.player(123).history()
for entry in history.rank_history:
    print(entry.rank_position, entry.wppr_points)
for entry in history.rating_history:
    print(entry.rating)
```

#### Removed Methods
```python
# Before (v0.1.x)
rankings = client.player(123).rankings()  # Will raise AttributeError in v0.2.0
cards = client.player(123).cards()        # Will raise AttributeError in v0.2.0

# After (v0.2.0) - No replacement
# Player rankings data is available in the player profile
profile = client.player(123).get()
# Player cards are only available via series: client.series_handle("CODE").player_card(123)
```

## [0.1.0] - 2024-11-14

### Added

- Initial release of IFPA SDK
- Complete implementation of IFPA API v2.1 with all 46 endpoints
- `IfpaClient` main client facade with context manager support
- HTTP client layer with session management, authentication, and error handling
- Comprehensive Pydantic models for all API resources:
  - Directors models and enums
  - Players models and enums
  - Rankings models and enums
  - Tournaments models and enums
  - Series models and enums
  - Statistics models and enums
  - Calendar models and enums
  - Common models and enums (TimePeriod, RankingSystem, ResultType, TournamentType)
- Resource clients for all IFPA API resources:
  - `DirectorsClient` - Search directors, get country directors
  - `DirectorHandle` - Get director details, past/upcoming tournaments
  - `PlayersClient` - Search players with multiple filters
  - `PlayerHandle` - Get player profile, rankings, results, PvP, history, cards
  - `RankingsClient` - WPPR, women, youth, virtual, pro, country, age-based, custom, group rankings
  - `TournamentsClient` - Search tournaments with filters
  - `TournamentHandle` - Get tournament details, results, formats, league info
  - `SeriesClient` - List all series or filter to active only
  - `SeriesHandle` - Get standings, player cards, overview, regions, rules, stats, schedule
  - `StatsClient` - Global stats, top countries, machine popularity
- Handle pattern for resource-specific operations with fluent API
- Configuration system with environment variable support
- Custom exception hierarchy:
  - `IfpaError` - Base exception
  - `MissingApiKeyError` - No API key provided or found
  - `IfpaApiError` - API returned error response
  - `IfpaClientValidationError` - Request validation failed
- Request validation using Pydantic models (configurable)
- Pagination support for all paginated endpoints
- Comprehensive test suite:
  - 180+ unit tests using requests-mock
  - 40+ integration tests with real API calls
  - 98% code coverage
- Complete type hints throughout the codebase
- Development tools configuration:
  - Black formatter (100 char line length)
  - Ruff linter with strict rules
  - mypy strict type checking
  - pre-commit hooks for automated checks
  - pytest with coverage reporting
- Project documentation:
  - Comprehensive README with examples for all resources
  - CONTRIBUTING guide with development workflow
  - Complete docstrings on all public APIs
  - MkDocs configuration for documentation site
- Poetry-based dependency management
- MIT License

### Technical Details

- **Python Version**: 3.11+
- **Dependencies**: requests, pydantic 2.0+
- **API Version**: IFPA API v2.1
- **Base URL**: https://api.ifpapinball.com
- **Authentication**: X-API-Key header

### Supported Endpoints

**Directors (4 endpoints)**:
- `GET /director/search` - Search for tournament directors
- `GET /director/{director_id}` - Get director details
- `GET /director/{director_id}/tournaments/past` - Get past tournaments
- `GET /director/{director_id}/tournaments/upcoming` - Get upcoming tournaments

**Players (5 endpoints in v0.1.0)**:
- `GET /player/search` - Search for players
- `GET /player/{player_id}` - Get player profile
- `GET /player/{player_id}/pvp/{other_player_id}` - Head-to-head comparison
- `GET /player/{player_id}/results` - Tournament results history
- `GET /player/{player_id}/rank_history` - WPPR ranking history

**Note**: v0.1.0 incorrectly included `rankings()` and `cards()` methods that mapped to non-existent API endpoints. These were removed in v0.2.0.

**Rankings (9 endpoints)**:
- `GET /rankings/wppr` - Main WPPR rankings
- `GET /rankings/women` - Women's rankings
- `GET /rankings/youth` - Youth rankings
- `GET /rankings/virtual` - Virtual tournament rankings
- `GET /rankings/pro` - Professional circuit rankings
- `GET /rankings/country` - Country rankings
- `GET /rankings/age_based/{age_group}` - Age-based rankings
- `GET /rankings/custom/{ranking_id}` - Custom ranking systems
- `GET /rankings/group/{group_id}` - Group rankings

**Tournaments (6 endpoints)**:
- `GET /tournament/search` - Search tournaments
- `GET /tournament/{tournament_id}` - Get tournament details
- `GET /tournament/{tournament_id}/results` - Tournament results
- `GET /tournament/{tournament_id}/formats` - Tournament formats
- `GET /tournament/{tournament_id}/league` - League information
- `GET /tournament/{tournament_id}/submissions` - Tournament submissions

**Series (8 endpoints)**:
- `GET /series/list` - List all series
- `GET /series/{series_code}/standings` - Series standings
- `GET /series/{series_code}/player_card/{player_id}` - Player's series card
- `GET /series/{series_code}/overview` - Series overview
- `GET /series/{series_code}/regions` - Series regions
- `GET /series/{series_code}/rules` - Series rules
- `GET /series/{series_code}/stats` - Series statistics
- `GET /series/{series_code}/schedule` - Series schedule

**Stats (10 endpoints)**:
- `GET /stats/global` - Global statistics
- `GET /stats/player_counts` - Player count statistics
- `GET /stats/tournament_counts` - Tournament count statistics
- `GET /stats/top_countries` - Top countries by player count
- `GET /stats/top_tournaments` - Top tournaments
- `GET /stats/recent_tournaments` - Recent tournament statistics
- `GET /stats/machine_popularity` - Machine popularity statistics
- `GET /stats/trends` - Various trend statistics
- `GET /stats/historical` - Historical statistics
- `GET /stats/participation` - Participation statistics

**Reference (2 endpoints)**:
- `GET /reference/countries` - List of countries
- `GET /reference/states` - List of states/provinces

[Unreleased]: https://github.com/johnsosoka/ifpa-api-python/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/johnsosoka/ifpa-api-python/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/johnsosoka/ifpa-api-python/releases/tag/v0.1.0
