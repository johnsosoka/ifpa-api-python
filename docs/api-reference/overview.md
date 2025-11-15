# API Reference Overview

The IFPA SDK is organized into several key modules that work together to provide access to the IFPA API.

## Module Structure

```
ifpa_sdk/
├── client.py          # Main IfpaClient facade
├── config.py          # Configuration management
├── exceptions.py      # Custom exceptions
├── http.py           # HTTP client layer
├── models/           # Pydantic models for all resources
│   ├── common.py     # Shared enums and models
│   ├── director.py   # Director models
│   ├── player.py     # Player models
│   ├── rankings.py   # Rankings models
│   ├── tournaments.py # Tournament models
│   ├── series.py     # Series models
│   └── calendar.py   # Calendar models
└── resources/        # Resource clients and handles
    ├── directors.py  # DirectorsClient, DirectorHandle
    ├── players.py    # PlayersClient, PlayerHandle
    ├── rankings.py   # RankingsClient
    ├── tournaments.py # TournamentsClient, TournamentHandle
    └── series.py     # SeriesClient, SeriesHandle
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
from ifpa_sdk import (
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
| `DirectorsClient` | Search directors, get country directors |
| `PlayersClient` | Search players |
| `RankingsClient` | Access ranking systems |
| `TournamentsClient` | Search tournaments |
| `SeriesClient` | List series |

## Resource Handles

| Handle | Description |
|--------|-------------|
| `DirectorHandle` | Director-specific operations |
| `PlayerHandle` | Player-specific operations |
| `TournamentHandle` | Tournament-specific operations |
| `SeriesHandle` | Series-specific operations |

For detailed documentation, see:

- [Client Reference](client.md)
- [Models Reference](models.md)
- [Exceptions Reference](exceptions.md)
