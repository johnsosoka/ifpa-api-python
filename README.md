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

## Full Documentation

Complete documentation is available at: **https://johnsosoka.github.io/ifpa-api-python/**

A typed Python client for the [IFPA (International Flipper Pinball Association) API](https://api.ifpapinball.com/). Access player rankings, tournament data, and statistics through a clean, modern Python interface with full type safety and Pydantic validation.

> **Alpha Release**: This library is under active development.

## Features

- **Fully Typed**: Complete type hints for IDE autocompletion and type checking
- **Pydantic Models**: Automatic request/response validation with detailed error messages
- **Comprehensive Coverage**: 36 IFPA API v2.1 endpoints across 6 resources
- **Fluent Interface**: Chainable handle pattern for resource-specific operations
- **Clear Error Handling**: Exception hierarchy for different failure scenarios
- **Well Tested**: 99% test coverage with unit and integration tests
- **Context Manager Support**: Automatic resource cleanup

## Installation

```bash
pip install ifpa-api
```

Requires Python 3.11 or higher.

## Quick Start

```python
from ifpa_api import IfpaClient

# Initialize client with API key
client = IfpaClient(api_key='your-api-key-here')

# Get player details
player = client.player(2643).details()
print(f"Name: {player.first_name} {player.last_name}")
print(f"Country: {player.country_name}")

# Get top WPPR rankings
rankings = client.rankings.wppr(count=10)
for entry in rankings.rankings[:5]:
    print(f"{entry.rank}. {entry.player_name}: {entry.rating} WPPR")

# Search for tournaments
tournaments = client.tournament.search(city="Portland", stateprov="OR")
for tournament in tournaments.tournaments[:3]:
    print(f"{tournament.tournament_name} ({tournament.event_date})")

# Close the client when done
client.close()
```

### Using Environment Variable

Alternatively, set the `IFPA_API_KEY` environment variable and initialize without passing the key:

```bash
export IFPA_API_KEY='your-api-key-here'
```

```python
from ifpa_api import IfpaClient

client = IfpaClient()
```

## Documentation

The complete documentation includes:

- **Getting Started**: Installation, authentication, and configuration
- **API Reference**: Detailed documentation for all 6 resources (Directors, Players, Rankings, Tournaments, Series, Reference)
- **Usage Examples**: Real-world workflows including player analysis, tournament tracking, and ranking comparisons
- **Error Handling**: Exception hierarchy and best practices
- **Development Guide**: Testing, contributing, and code style guidelines

Visit the full documentation: **https://johnsosoka.github.io/ifpa-api-python/**

## Resources

- **Documentation**: https://johnsosoka.github.io/ifpa-api-python/
- **PyPI Package**: https://pypi.org/project/ifpa-api/
- **GitHub Repository**: https://github.com/johnsosoka/ifpa-api-python
- **Issue Tracker**: https://github.com/johnsosoka/ifpa-api-python/issues
- **IFPA API Documentation**: https://api.ifpapinball.com/docs
- **Maintainer**: [open.source@sosoka.com](mailto:open.source@sosoka.com)
- **Website**: [johnsosoka.com](https://johnsosoka.com)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:

- Setting up your development environment
- Code quality standards (Black, Ruff, mypy)
- Writing and running tests
- Submitting pull requests

## License

MIT License - Copyright (c) 2025 John Sosoka

See the [LICENSE](LICENSE) file for details.

---

Built by [John Sosoka](https://johnsosoka.com) for the pinball community.
