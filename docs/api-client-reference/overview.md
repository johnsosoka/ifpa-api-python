# API Reference Overview

The IFPA SDK is organized into several key modules that work together to provide access to the IFPA API.

## Module Structure

```
ifpa_api/
├── client.py          # Main IfpaClient facade
├── core/              # Core infrastructure
│   ├── base.py        # Base classes and mixins
│   ├── config.py      # Configuration management
│   ├── exceptions.py  # Custom exceptions
│   ├── http.py        # HTTP client layer
│   └── query_builder.py # Query builder base
├── models/            # Pydantic models for all resources
│   ├── common.py      # Shared enums and models
│   ├── director.py    # Director models
│   ├── player.py      # Player models
│   ├── rankings.py    # Rankings models
│   ├── tournaments.py # Tournament models
│   ├── series.py      # Series models
│   ├── reference.py   # Reference data models
│   └── calendar.py    # Calendar models
└── resources/         # Resource clients and handles
    ├── director.py    # DirectorClient (callable pattern)
    ├── player.py      # PlayerClient (callable pattern)
    ├── rankings.py    # RankingsClient
    ├── tournaments.py # TournamentsClient, TournamentHandle
    ├── series.py      # SeriesClient, SeriesHandle
    └── reference.py   # ReferenceClient
```

## Public API

The SDK exposes the following public API:

### Client

- `IfpaClient` - Main client facade

### Enums

- `TimePeriod` - PAST, FUTURE
- `RankingSystem` - MAIN, WOMEN, YOUTH, VIRTUAL, PRO
- `ResultType` - ACTIVE, NONACTIVE, INACTIVE
- `TournamentType` - OPEN, WOMEN, YOUTH, etc.

### Exceptions

- `IfpaError` - Base exception
- `MissingApiKeyError` - No API key
- `IfpaApiError` - API error
- `IfpaClientValidationError` - Validation error

## Quick Reference

```python
from ifpa_api import (
    IfpaClient,
    TimePeriod,
    RankingSystem,
    ResultType,
    TournamentType,
    IfpaError,
    IfpaApiError,
    MissingApiKeyError,
    IfpaClientValidationError,
)
```

## Resource Clients

| Client | Description |
|--------|-------------|
| `DirectorClient` | Search directors, get country directors |
| `PlayersClient` | Search players |
| `RankingsClient` | Access ranking systems |
| `TournamentsClient` | Search tournaments |
| `SeriesClient` | List series |
| `ReferenceClient` | Get countries and state/province data |

## Resource Handles

Director and Player resources use a callable pattern for resource-specific operations:
- `client.director(id)` returns a context for director operations
- `client.player(id)` returns a context for player operations

Other resources use traditional handle classes:

| Handle | Description |
|--------|-------------|
| `TournamentHandle` | Tournament-specific operations |
| `SeriesHandle` | Series-specific operations |

For detailed documentation, see:

- [Client Reference](client.md)
- [Models Reference](models.md)
- [Exceptions Reference](exceptions.md)
