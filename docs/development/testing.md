# Testing

The IFPA SDK includes comprehensive unit and integration tests.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── helpers.py               # Test utilities
├── unit/                    # Unit tests (mocked)
│   ├── conftest.py
│   ├── test_client.py
│   ├── test_config.py
│   ├── test_directors.py
│   ├── test_exceptions.py
│   ├── test_http.py
│   ├── test_player.py
│   ├── test_rankings.py
│   ├── test_series.py
│   ├── test_stats.py
│   └── test_tournaments.py
└── integration/             # Integration tests (real API)
    ├── conftest.py
    ├── helpers.py
    ├── test_directors_integration.py
    ├── test_player_integration.py
    ├── test_rankings_integration.py
    ├── test_series_integration.py
    └── test_tournaments_integration.py
```

## Running Tests

### All Tests

```bash
# Run all tests with coverage
poetry run pytest --cov=ifpa_api --cov-report=term-missing

# Run with verbose output
poetry run pytest -v
```

### Unit Tests Only

Unit tests use `requests-mock` and don't require an API key:

```bash
poetry run pytest tests/unit/
```

### Integration Tests Only

Integration tests make real API calls and require `IFPA_API_KEY`:

```bash
export IFPA_API_KEY='your-api-key'
poetry run pytest tests/integration/
```

### Skip Integration Tests

```bash
poetry run pytest -m "not integration"
```

### Run Specific Test File

```bash
poetry run pytest tests/unit/test_player.py
```

### Run Specific Test

```bash
poetry run pytest tests/unit/test_player.py::test_search_players
```

## Coverage

The project maintains 98% test coverage. View coverage report:

```bash
# Terminal report
poetry run pytest --cov=ifpa_api --cov-report=term-missing

# HTML report
poetry run pytest --cov=ifpa_api --cov-report=html
open htmlcov/index.html
```

## Writing Tests

### Unit Test Example

```python
import requests_mock
from ifpa_api import IfpaClient


def test_search_players():
    """Test searching for players."""
    with requests_mock.Mocker() as m:
        # Mock the API response
        m.get(
            "https://api.ifpapinball.com/player/search",
            json={
                "search": [
                    {
                        "player_id": 12345,
                        "first_name": "John",
                        "last_name": "Doe"
                    }
                ],
                "total_count": 1
            }
        )

        client = IfpaClient(api_key="test-key")
        result = client.player.query("John").get()

        assert len(result.search) == 1
        assert result.search[0].player_id == 12345
        assert result.search[0].first_name == "John"
```

### Integration Test Example

```python
import pytest
from ifpa_api import IfpaClient


@pytest.mark.integration
def test_search_players_integration(client: IfpaClient):
    """Test querying for real players."""
    result = client.player.query("Josh").get()

    assert len(result.search) > 0
    assert all(hasattr(p, "player_id") for p in result.search)
    assert all(hasattr(p, "first_name") for p in result.search)
```

## Test Markers

Tests are marked for organization:

```python
@pytest.mark.integration  # Integration test
```

Use markers to filter tests:

```bash
# Run only integration tests
poetry run pytest -m integration

# Skip integration tests
poetry run pytest -m "not integration"
```

## Fixtures

Common fixtures are available in `conftest.py`:

```python
@pytest.fixture
def client() -> IfpaClient:
    """Configured client for integration tests."""
    return IfpaClient()

@pytest.fixture
def mock_http_client():
    """Mock HTTP client for unit tests."""
    # ...
```

For complete details, see [CONTRIBUTING.md](../contributing.md).
