# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - TBD

### Changed

**Tournament Resource Refactoring (BREAKING CHANGES)**

The Tournament resource has been refactored to match the callable pattern established by Player and Director resources, providing a unified interface for collection and resource-level operations.

**Breaking Changes:**

1. **Property renamed**: `client.tournaments` → `client.tournament` (singular)
   ```python
   # Before (v0.2.x)
   results = client.tournaments.search(name="PAPA")

   # After (v0.3.0)
   results = client.tournament.search(name="PAPA")
   ```

2. **Method renamed**: `.get()` → `.details()` (consistent with Player and Director)
   ```python
   # Before (v0.2.x)
   tournament = client.tournament(12345).get()

   # After (v0.3.0)
   tournament = client.tournament(12345).details()
   ```

3. **Class renamed**: `TournamentsClient` → `TournamentClient` (singular)
   ```python
   # Before (v0.2.x)
   from ifpa_api.resources.tournaments import TournamentsClient

   # After (v0.3.0)
   from ifpa_api.resources.tournament import TournamentClient
   ```

4. **Class removed**: `TournamentHandle` is now private (`_TournamentContext`)
   - This internal class should not be directly imported by users
   - Access tournament operations via the callable pattern: `client.tournament(id).details()`

**Unified Pattern:**

The tournament resource now follows the same callable pattern as player and director:
```python
# Collection-level operations
tournaments = client.tournament.search(name="PAPA")
formats = client.tournament.list_formats()

# Resource-level operations via callable pattern
tournament = client.tournament(12345).details()
results = client.tournament(12345).results()
league = client.tournament(12345).league()
```

**Series Resource Refactoring (BREAKING CHANGES)**

The Series resource has been migrated to use the callable pattern, completing the unification effort across all resources.

**Breaking Changes:**

1. **Method removed**: `client.series_handle()` method removed
   ```python
   # Before (v0.2.x)
   standings = client.series_handle("NACS").standings()
   card = client.series_handle("PAPA").player_card(12345, "OH")

   # After (v0.3.0)
   standings = client.series("NACS").standings()
   card = client.series("PAPA").player_card(12345, "OH")
   ```

2. **Class renamed**: `SeriesHandle` is now private (`_SeriesContext`)
   - This internal class should not be directly imported by users
   - Access series operations via the callable pattern: `client.series("CODE").standings()`

**Unified Pattern:**

All resources now follow the same callable pattern:
```python
# Player
client.player(123).details()

# Director
client.director(456).details()

# Tournament
client.tournament(789).details()

# Series (NEW)
client.series("NACS").standings()
```

**Migration Guide:**

Simple find-replace in your codebase:
- Replace: `client.series_handle(` → `client.series(`

### Fixed

- Consolidated integration tests from 3 files into 1 organized file (`test_tournament_integration.py`)
- Updated all documentation to reflect new callable pattern
- Fixed helper function `get_test_tournament_id()` to use correct callable pattern

## [0.2.1] - TBD

### Added

**Phase 2 - New Features & Enhanced API Coverage**

- **Reference Resource** (NEW):
  - `ReferenceClient.countries()` - Get list of all countries in IFPA system (62 countries)
  - `ReferenceClient.state_provs()` - Get states/provinces by country (67 regions across AU, CA, US)

- **Rankings Resource**:
  - `RankingsClient.country_list()` - List all countries with player counts (51 countries)
  - `RankingsClient.custom_list()` - List all custom ranking systems (84 custom rankings)

- **Tournaments Resource**:
  - `TournamentHandle.related()` - Get related tournaments (same venue or series)
  - `TournamentsClient.list_formats()` - List all tournament format types (25 formats)

- **Exceptions**:
  - `PlayersNeverMetError` - Custom exception for when PVP data unavailable between two players who have never competed together

### Fixed

- **Rankings Resource**:
  - Fixed age field validation to handle empty string values returned by API
  - Fixed `by_country()` response model to correctly return player rankings (was incorrectly expecting country-level statistics)

- **Directors Resource**:
  - Fixed `country_directors()` to handle nested `player_profile` structure in API response

- **Tournaments Resource**:
  - Fixed search response to correctly map API's `search` key to model's `tournaments` field
  - Added validation requiring both `start_date` and `end_date` parameters together (API returns 400 if only one provided)

- **Series Resource**:
  - Fixed `standings()` to call correct `/series/{code}/overall_standings` endpoint (was calling wrong endpoint)
  - Added required `region_code` parameter to `regions()`, `stats()`, and `tournaments()` methods

- **Players Resource**:
  - Improved `pvp()` error handling with clearer exception for players who have never competed together

### Removed

- **Series Resource**:
  - Removed `overview()` method (endpoint does not exist in API)
  - Removed `rules()` method (endpoint does not exist in API)
  - Removed `schedule()` method (endpoint does not exist in API)

### Testing

- Added 154 comprehensive integration tests across all 6 resources
- Increased code coverage from 95% to 97%
- All fixes verified against live IFPA API
- Test pass rate improved from 52% to 100% (unit tests)
- Integration test pass rate: 88% (180/209 tests passing)

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

# After (v0.2.0+) - Both parameters required
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

# After (v0.2.0+) - Separate arrays
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

# After (v0.2.0+) - No replacement
# Player rankings data is available in the player profile
profile = client.player(123).details()
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
  - `DirectorClient` - Search directors, get country directors, director details, tournaments (callable pattern)
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

**Note**: v0.1.0 incorrectly included `rankings()` and `cards()` methods that mapped to non-existent API endpoints. These were removed in v0.2.0+.

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

[Unreleased]: https://github.com/johnsosoka/ifpa-api-python/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/johnsosoka/ifpa-api-python/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/johnsosoka/ifpa-api-python/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/johnsosoka/ifpa-api-python/releases/tag/v0.1.0
