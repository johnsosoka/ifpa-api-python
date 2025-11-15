# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IFPA SDK is a typed Python client for the IFPA (International Flipper Pinball Association) API. This is Commerce Architects' first public open source product, hosted on PyPI as `ifpa-sdk`.

**Key Details**:
- **Package Name**: `ifpa-sdk` (PyPI), `ifpa_sdk` (import name)
- **Python Version**: 3.11+
- **Dependency Management**: Poetry
- **License**: MIT
- **Repository**: https://github.com/jscom/ifpa-sdk
- **API Documentation**: https://api.ifpapinball.com/docs

## Development Commands

### Setup & Installation
```bash
# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Set API key for testing (use credentials file or env var)
export IFPA_API_KEY='your-api-key'
```

### Testing
```bash
# Run all unit tests (no API key required)
poetry run pytest tests/unit/

# Run all tests including integration (requires IFPA_API_KEY)
poetry run pytest

# Run with coverage report
poetry run pytest --cov=ifpa_sdk --cov-report=term-missing

# Skip integration tests
poetry run pytest -m "not integration"

# Run only integration tests
poetry run pytest -m integration

# Run specific test file
poetry run pytest tests/unit/test_players.py

# Run specific test function
poetry run pytest tests/unit/test_players.py::test_search_players -v

# Run tests with short traceback for quicker debugging
poetry run pytest tests/unit/ -v --tb=short
```

### Code Quality
```bash
# Format code (100 char line length)
poetry run black src tests

# Lint code
poetry run ruff check src tests

# Auto-fix linting issues
poetry run ruff check --fix src tests

# Type check (strict mode enabled)
poetry run mypy src

# Run all pre-commit hooks manually
poetry run pre-commit run --all-files
```

### Documentation
```bash
# Build documentation locally
poetry run mkdocs build

# Serve docs locally with auto-reload
poetry run mkdocs serve
```

## Architecture

### Three-Layer Design

1. **HTTP Core Layer** (`http.py`)
   - `_HttpClient`: Low-level HTTP client using `requests`
   - Manages sessions, authentication via `X-API-Key` header
   - Maps HTTP errors to SDK exceptions
   - Base URL: `https://api.ifpapinball.com/`

2. **Domain SDK Layer**
   - **Models** (`src/ifpa_sdk/models/`): Pydantic v2 models for requests/responses
   - **Resources** (`src/ifpa_sdk/resources/`): Resource-specific clients (Directors, Players, Rankings, Tournaments, Series, Stats)
   - **Handles**: Fluent interface pattern for resource-specific operations (e.g., `client.player(12345).get()`)

3. **Public Facade** (`client.py`)
   - `IfpaClient`: Main entry point with lazy-loaded resource clients
   - Properties for top-level resources (`.directors`, `.players`, `.rankings`, etc.)
   - Factory methods returning handles (`.player(id)`, `.director(id)`, `.tournament(id)`, `.series_handle(code)`)

### Handle Pattern

Resources with ID-based endpoints use handles for fluent access:

```python
# Player handle example
player = client.player(12345).get()
rankings = client.player(12345).rankings()
results = client.player(12345).results()
pvp = client.player(12345).pvp(67890)

# Director handle example
director = client.director(1000).get()
tournaments = client.director(1000).tournaments(TimePeriod.PAST)

# Tournament handle example
tournament = client.tournament(12345).get()
results = tournament.results()

# Series handle example
standings = client.series_handle("PAPA").standings()
card = client.series_handle("PAPA").player_card(12345)
```

### Directory Structure

```
src/ifpa_sdk/
├── __init__.py          # Public API exports
├── client.py            # IfpaClient facade
├── config.py            # Settings and env handling
├── exceptions.py        # Exception hierarchy
├── http.py              # Low-level HTTP client
├── models/              # Pydantic models
│   ├── common.py        # Shared enums (TimePeriod, RankingSystem, ResultType, TournamentType)
│   ├── director.py      # Director models
│   ├── player.py        # Player models
│   ├── rankings.py      # Rankings models
│   ├── tournaments.py   # Tournament models
│   ├── series.py        # Series models
│   └── calendar.py      # Calendar models
└── resources/           # Resource clients & handles
    ├── directors.py     # DirectorsClient, DirectorHandle
    ├── players.py       # PlayersClient, PlayerHandle
    ├── rankings.py      # RankingsClient
    ├── tournaments.py   # TournamentsClient, TournamentHandle
    └── series.py        # SeriesClient, SeriesHandle
```

## API Coverage

36 IFPA API v2.1 endpoints implemented across 6 resources:
- **Directors**: 4 endpoints (search, details, tournaments)
- **Players**: 7 endpoints (search, profile, rankings, results, PvP, history, cards)
- **Rankings**: 9 endpoints (WPPR, women, youth, virtual, pro, country, age-based, custom, group)
- **Tournaments**: 6 endpoints (search, details, results, formats, league, submissions)
- **Series**: 8 endpoints (list, standings, player cards, overview, regions, rules, stats, schedule)
- **Reference**: 2 endpoints (countries, states)

**Note**: Stats endpoints (10 endpoints) are not implemented in v0.1.0 as they return 404 from the live API. These will be implemented in v0.2.0 when the API endpoints become available.

## Authentication

API key resolution priority:
1. Constructor parameter: `IfpaClient(api_key="...")`
2. Environment variable: `IFPA_API_KEY`
3. Raises `MissingApiKeyError` if neither provided

For testing, API key can also be read from `credentials` file (gitignored).

## Exception Hierarchy

```python
IfpaError                    # Base exception
├── MissingApiKeyError       # No API key provided/found
├── IfpaApiError             # API returned non-2xx status (has status_code, response_body)
└── IfpaClientValidationError # Pydantic request validation failed
```

## Testing Strategy

### Unit Tests (`tests/unit/`)
- Use `requests-mock` to mock API responses
- No API key required
- Fast execution
- Focus on SDK logic and error handling

### Integration Tests (`tests/integration/`)
- Make real API calls
- Require valid `IFPA_API_KEY`
- Marked with `@pytest.mark.integration`
- Use shared fixture from `tests/integration/conftest.py`

### API Key Resolution for Tests
The `api_key` fixture in `tests/conftest.py` resolves API keys in this order:
1. `IFPA_API_KEY` environment variable
2. `credentials` file in project root
3. Skips test if neither available

## Code Quality Standards

### Type Hints
- 100% type coverage on all public APIs
- Strict mypy mode enabled
- Use `int | str` for flexible ID parameters
- Use `X | None` for optional fields (Python 3.11+ syntax)

### Formatting
- Black with 100 character line length
- Pre-commit hooks enforce formatting

### Linting
- Ruff with strict rules enabled (see `pyproject.toml`)
- Import sorting enforced (isort via Ruff)

### Docstrings
- Google-style docstrings on all public functions/classes
- Include Args, Returns, Raises, and Example sections
- Examples use triple-backtick code blocks

## Known Issues & Workarounds

### API Spec Inconsistencies
The OpenAPI spec (`api.json`) has some inconsistencies with the actual API:
- Field names may differ (e.g., spec says `results`, API returns `search` for player search)
- Some response structures differ from spec
- **Always test against real API** when implementing new endpoints

### Response Wrapper Patterns
Some endpoints return data wrapped in an object key:
```python
# Player details endpoint returns: {"player": [player_object]}
# Must extract: player_data[0]

# Most search endpoints return: {"search": [...]} or {"tournaments": [...]}
```

## CI/CD

### GitHub Actions Workflows
- `ci.yml`: Runs on push/PR - linting, type checking, tests (Python 3.11 & 3.12)
- `publish.yml`: Publishes to PyPI on version tags (v*)
- `security.yml`: Dependabot security scanning

### Release Process
1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create and push git tag: `git tag v0.1.0 && git push origin v0.1.0`
4. GitHub Actions automatically publishes to PyPI

## Common Development Tasks

### Adding a New Endpoint
1. Add Pydantic models to appropriate file in `models/`
2. Add method to resource client in `resources/`
3. Add unit tests with mocked responses in `tests/unit/`
4. Add integration test in `tests/integration/`
5. Update docstring with example
6. Run full test suite and quality checks

### Fixing a Bug
1. Create feature branch: `git checkout -b bugfix/description`
2. Write failing test that reproduces the bug
3. Fix the implementation
4. Verify all tests pass
5. Run quality checks (black, ruff, mypy)
6. Commit and create PR

### Testing Against Real API
```bash
# Export API key (from credentials file or own key)
export IFPA_API_KEY='your-api-key'

# Run integration tests
poetry run pytest tests/integration/ -v

# Or test specific endpoint with curl
curl -H "X-API-Key: $IFPA_API_KEY" \
     "https://api.ifpapinball.com/player/search?q=John&count=5"
```

## Project Context Files

The `llm_memory/` directory (gitignored) contains team context:
- `project_context.md`: Overall project decisions and architecture
- Various investigation reports from debugging sessions
- API analysis notes

These files are for team collaboration and not included in published package.
