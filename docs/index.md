# IFPA API Client

> **Note**: This is an unofficial client library, not affiliated with or endorsed by IFPA.

Welcome to the IFPA API documentation! This library provides a typed Python client for the [IFPA (International Flipper Pinball Association) API](https://api.ifpapinball.com/).

## Overview

The IFPA API client enables Python developers to access pinball rankings, tournament data, and player statistics through a clean, modern interface. Whether you're building a tournament management system, statistics dashboard, or analyzing player performance, this client provides the tools you need.

## Key Features

- **Fully Typed**: Complete type hints for IDE autocompletion and type checking
- **Pydantic Models**: Automatic request/response validation with detailed error messages
- **Resource-Oriented**: Intuitive access patterns matching the IFPA API structure
- **Comprehensive Coverage**: 36 IFPA API v2.1 endpoints across 6 resources
- **Fluent Interface**: Chainable handle pattern for resource-specific operations
- **Pagination Support**: Built-in support for paginated endpoints
- **Clear Error Handling**: Exception hierarchy for different failure scenarios
- **Well Tested**: 99% test coverage with unit and integration tests

> **Alpha Release**: This library is under active development. The API is stable but may evolve based on community feedback. Production use is supported, but you may encounter occasional updates to the interface.

## Quick Example

```python
from ifpa_api import IfpaClient

# Initialize client with API key
client = IfpaClient(api_key='your-api-key-here')

# Get player information
player = client.player(2643).get()
print(f"Name: {player.first_name} {player.last_name}")
print(f"Country: {player.country_name}")

# Get top WPPR rankings
rankings = client.rankings.wppr(count=100)
for entry in rankings.rankings[:5]:
    print(f"{entry.rank}. {entry.player_name}: {entry.rating}")

# Search for tournaments
tournaments = client.tournaments.search(city="Portland", stateprov="OR")
for tournament in tournaments.tournaments:
    print(f"{tournament.tournament_name} ({tournament.event_date})")

# Close the client when done
client.close()
```

## Installation

Install the client using pip:

```bash
pip install ifpa-api
```

Requires Python 3.11 or higher.

## API Resources

The client provides access to 36 of 46 IFPA API endpoints:

| Resource | Description | Endpoints |
|----------|-------------|-----------|
| **Directors** | Search tournament directors, view their events | 4 |
| **Players** | Player profiles, rankings, tournament history | 7 |
| **Rankings** | WPPR, women, youth, pro, and custom rankings | 9 |
| **Tournaments** | Search tournaments, view results and details | 6 |
| **Series** | Tournament series standings and statistics | 8 |
| **Reference** | Countries and states lookup | 2 |

## Getting Help

- **Documentation**: Browse the [Getting Started](getting-started/installation.md) guide
- **Examples**: Check the [Usage Guide](usage/directors.md) for code examples
- **Issues**: Report bugs on [GitHub Issues](https://github.com/johnsosoka/ifpa-api-python/issues)
- **API Reference**: See the [IFPA API docs](https://api.ifpapinball.com/docs)

## Next Steps

- [Install the client](getting-started/installation.md)
- [Quick Start Guide](getting-started/quickstart.md)
- [Authentication Setup](getting-started/authentication.md)
- [Usage Examples](usage/directors.md)

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/johnsosoka/ifpa-api-python/blob/main/LICENSE) file for details.

## Acknowledgments

Built by [John Sosoka](https://johnsosoka.com) for the pinball community. Thanks to IFPA for providing the public API.

**Maintainer**: [open.source@sosoka.com](mailto:open.source@sosoka.com)
