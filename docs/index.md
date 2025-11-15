# IFPA SDK

Welcome to the IFPA SDK documentation! This library provides a typed Python client for the [IFPA (International Flipper Pinball Association) API](https://api.ifpapinball.com/).

## Overview

The IFPA SDK enables Python developers to easily access pinball rankings, tournament data, player statistics, and more through a clean, modern interface. Whether you're building a tournament management system, a statistics dashboard, or analyzing player performance, this SDK provides all the tools you need.

## Key Features

- **Fully Typed**: Complete type hints for IDE autocompletion and type checking
- **Pydantic Models**: Automatic request/response validation with detailed error messages
- **Resource-Oriented API**: Intuitive access patterns matching the IFPA API structure
- **Comprehensive Coverage**: All 46 IFPA API v2.1 endpoints implemented
- **Handle Pattern**: Fluent interface for resource-specific operations
- **Pagination Support**: Built-in support for paginated endpoints
- **Error Handling**: Clear exception hierarchy for different failure scenarios
- **Well Tested**: 98% test coverage with unit and integration tests

## Quick Example

```python
from ifpa_sdk import IfpaClient

# Initialize client (uses IFPA_API_KEY environment variable)
client = IfpaClient()

# Get player information
player = client.player(12345).get()
print(f"Name: {player.first_name} {player.last_name}")
print(f"Current Rank: {player.current_wppr_rank}")

# Get top WPPR rankings
rankings = client.rankings.wppr(start_pos=0, count=100)
for entry in rankings.rankings:
    print(f"{entry.rank}. {entry.player_name}: {entry.rating}")

# Search for tournaments
tournaments = client.tournaments.search(city="Portland", stateprov="OR")
for tournament in tournaments.tournaments:
    print(f"{tournament.tournament_name} ({tournament.event_date})")
```

## Installation

Install the SDK using pip:

```bash
pip install ifpa-sdk
```

Requires Python 3.11 or higher.

## API Resources

The SDK provides access to all IFPA API resources:

| Resource | Description | Endpoints |
|----------|-------------|-----------|
| **Directors** | Search tournament directors, view their events | 4 |
| **Players** | Player profiles, rankings, tournament history | 7 |
| **Rankings** | WPPR, women, youth, pro, and custom rankings | 9 |
| **Tournaments** | Search tournaments, view results and details | 6 |
| **Series** | Tournament series standings and statistics | 8 |

## Getting Help

- **Documentation**: Browse the [Getting Started](getting-started/installation.md) guide
- **Examples**: Check the [Usage Guide](usage/directors.md) for code examples
- **Issues**: Report bugs on [GitHub Issues](https://github.com/jscom/ifpa-sdk/issues)
- **API Reference**: See the [IFPA API docs](https://api.ifpapinball.com/docs)

## Next Steps

- [Install the SDK](getting-started/installation.md)
- [Quick Start Guide](getting-started/quickstart.md)
- [Authentication Setup](getting-started/authentication.md)
- [Usage Examples](usage/directors.md)

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/jscom/ifpa-sdk/blob/main/LICENSE) file for details.

## Acknowledgments

Built by [Commerce Architects](https://github.com/jscom) for the pinball community. Thanks to IFPA for providing the public API.
