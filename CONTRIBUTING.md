# Contributing to IFPA SDK

Thank you for your interest in contributing to the IFPA SDK! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

This project welcomes contributions from everyone. We expect all contributors to:

- Be respectful and constructive in discussions
- Focus on what is best for the community
- Show empathy towards other community members
- Accept constructive feedback gracefully

## How to Report Bugs

If you find a bug in the package, please open an issue on [GitHub Issues](https://github.com/johnsosoka/ifpa-api-python/issues) with:

1. **Clear Title**: Describe the bug in one sentence
2. **Description**: Detailed description of the issue
3. **Steps to Reproduce**: Minimal steps to reproduce the problem
4. **Expected Behavior**: What you expected to happen
5. **Actual Behavior**: What actually happened
6. **Environment**:
   - Python version
   - IFPA SDK version
   - Operating system
7. **Code Sample**: Minimal code that demonstrates the issue

Example:

```markdown
## Bug: Player search fails with special characters

**Description**: When searching for players with names containing special characters (e.g., accented letters), the API returns an error.

**Steps to Reproduce**:
1. Initialize client with valid API key
2. Call `client.players.search(name="José")`
3. Observe error

**Expected**: Returns players matching "José"
**Actual**: Raises `IfpaApiError` with status 400

**Environment**:
- Python 3.11.5
- ifpa-api 0.2.1
- macOS 14.0

**Code**:
```python
from ifpa_api import IfpaClient
client = IfpaClient()
players = client.players.search(name="José")  # Fails
```
```

## How to Suggest Features

Feature requests are welcome! Please open an issue with the `enhancement` label and include:

1. **Use Case**: Describe the problem you're trying to solve
2. **Proposed Solution**: Your idea for how to solve it
3. **Alternatives**: Other approaches you've considered
4. **Additional Context**: Any other relevant information

## Development Setup

### Prerequisites

- Python 3.11 or higher
- [Poetry](https://python-poetry.org/) for dependency management
- Git

### Setup Steps

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ifpa-api.git
   cd ifpa-api
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/johnsosoka/ifpa-api-python.git
   ```

4. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

5. **Install dependencies**:
   ```bash
   poetry install
   ```

6. **Install pre-commit hooks**:
   ```bash
   poetry run pre-commit install
   ```

7. **Set up your API key** for integration tests:
   ```bash
   export IFPA_API_KEY='your-api-key-here'
   ```

   Add this to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.) to persist across sessions.

### Verify Setup

Run the test suite to ensure everything is working:

```bash
# Run unit tests (no API key required)
poetry run pytest tests/unit/

# Run all tests including integration tests (requires API key)
poetry run pytest
```

## Development Workflow

### 1. Create a Feature Branch

Always create a new branch for your work:

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b bugfix/issue-description
```

Branch naming conventions:
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring
- `test/description` - Test additions/improvements

### 2. Make Your Changes

Follow these guidelines when writing code:

#### Code Style

The project enforces strict code style using automated tools:

- **Black**: Code formatting with 100 character line length
- **Ruff**: Fast Python linting
- **mypy**: Static type checking with strict mode enabled

Run formatters before committing:

```bash
# Format code
poetry run black src tests

# Check linting
poetry run ruff check src tests

# Auto-fix linting issues
poetry run ruff check --fix src tests

# Type check
poetry run mypy src
```

The pre-commit hooks will automatically run these checks before each commit.

#### Type Hints

All public functions and methods must have complete type hints:

```python
# Good
def search_players(name: str, count: int | None = None) -> PlayerSearchResponse:
    """Search for players by name."""
    ...

# Bad - missing type hints
def search_players(name, count=None):
    ...
```

#### Docstrings

All public modules, classes, and functions must have docstrings following Google style:

```python
def get_player(player_id: int | str) -> Player:
    """Get detailed information about a specific player.

    Args:
        player_id: The player's unique identifier

    Returns:
        Player information including profile and rankings

    Raises:
        IfpaApiError: If the API request fails

    Example:
        ```python
        player = client.player(12345).get()
        print(f"{player.first_name} {player.last_name}")
        ```
    """
    ...
```

#### Code Organization

Follow the established project structure:

- **Models** (`src/ifpa_api/models/`): Pydantic models for requests/responses
- **Resources** (`src/ifpa_api/resources/`): Resource clients and handles
- **Core** (`src/ifpa_api/`): Client, HTTP, config, exceptions

Keep functions small and focused:
- Single responsibility principle
- Aim for functions under 20 lines
- Extract complex logic into helper functions

### 3. Write Tests

All new features must include tests. The project maintains 98% code coverage.

#### Unit Tests

Unit tests use `requests-mock` to mock API responses:

```python
# tests/unit/test_players.py
import requests_mock
from ifpa_api import IfpaClient


def test_search_players():
    """Test searching for players."""
    with requests_mock.Mocker() as m:
        # Mock the API response
        m.get(
            "https://api.ifpapinball.com/player/search",
            json={"players": [{"player_id": 12345, "first_name": "John"}]}
        )

        client = IfpaClient(api_key="test-key")
        result = client.players.search(name="John")

        assert len(result.players) == 1
        assert result.players[0].player_id == 12345
```

#### Integration Tests

Integration tests make real API calls and are marked with `@pytest.mark.integration`:

```python
# tests/integration/test_players_integration.py
import pytest
from ifpa_api import IfpaClient


@pytest.mark.integration
def test_search_players_integration(client: IfpaClient):
    """Test searching for real players."""
    result = client.players.search(name="Josh")
    assert len(result.players) > 0
    assert all(hasattr(p, "player_id") for p in result.players)
```

Integration tests use a fixture that provides a configured client (see `tests/integration/conftest.py`).

#### Running Tests

```bash
# Run all tests with coverage
poetry run pytest --cov=ifpa_api --cov-report=term-missing

# Run only unit tests
poetry run pytest tests/unit/

# Run only integration tests (requires IFPA_API_KEY)
poetry run pytest tests/integration/

# Skip integration tests
poetry run pytest -m "not integration"

# Run a specific test file
poetry run pytest tests/unit/test_players.py

# Run a specific test function
poetry run pytest tests/unit/test_players.py::test_search_players

# Run tests with verbose output
poetry run pytest -v
```

#### Coverage Requirements

- New code should maintain or improve the current 98% coverage
- Critical paths must have 100% coverage
- Use `# pragma: no cover` sparingly and only for unreachable code

### 4. Update Documentation

If your changes affect the public API or add new features:

1. **Update docstrings** in the code
2. **Add examples** to the README.md if appropriate
3. **Update CHANGELOG.md** under the `[Unreleased]` section
4. **Add usage examples** in the relevant resource section

### 5. Run Pre-Commit Checks

Before committing, ensure all checks pass:

```bash
# Run all pre-commit hooks manually
poetry run pre-commit run --all-files

# Or just commit - hooks run automatically
git add .
git commit -m "feat: add player search filtering"
```

The pre-commit hooks will:
- Format code with Black
- Lint with Ruff
- Check type hints with mypy
- Validate YAML/JSON files
- Check for trailing whitespace
- Ensure files end with newline

### 6. Commit Your Changes

Follow these commit message guidelines:

**Format**:
```
<type>: <subject>

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring (no functional changes)
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, config, etc.)
- `perf`: Performance improvements

**Examples**:
```bash
git commit -m "feat: add support for custom ranking systems"
git commit -m "fix: handle special characters in player search"
git commit -m "docs: add examples for series resource"
git commit -m "test: add integration tests for tournaments"
```

**Good commit messages**:
- Keep subject line under 72 characters
- Use imperative mood ("add" not "added" or "adds")
- Capitalize subject line
- No period at end of subject
- Separate subject from body with blank line
- Wrap body at 72 characters
- Explain what and why, not how

### 7. Push and Create Pull Request

```bash
# Push your branch to your fork
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:

1. **Clear title** describing the change
2. **Description** including:
   - What changed and why
   - Link to related issue (if applicable)
   - Breaking changes (if any)
   - How to test the changes
3. **Checklist**:
   - [ ] Tests added/updated
   - [ ] Documentation updated
   - [ ] CHANGELOG.md updated
   - [ ] All tests pass
   - [ ] Code formatted with Black
   - [ ] No linting errors
   - [ ] Type checking passes

**Pull Request Template**:

```markdown
## Summary

Brief description of the change.

## Changes

- Bullet list of changes made
- Each item describes a specific change

## Related Issue

Closes #123

## Breaking Changes

None / List any breaking changes

## Testing

Describe how the changes were tested:
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing performed

## Checklist

- [ ] Tests pass locally
- [ ] Code formatted with Black
- [ ] Linting passes (Ruff)
- [ ] Type checking passes (mypy)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

## Adding New Endpoints

If IFPA adds new API endpoints, follow this process:

### 1. Update Models

Add Pydantic models to the appropriate file in `src/ifpa_api/models/`:

```python
# src/ifpa_api/models/player.py
from pydantic import BaseModel

class NewFeatureResponse(BaseModel):
    """Response from new feature endpoint."""
    feature_id: int
    feature_name: str
    ...
```

### 2. Add Resource Method

Add the method to the appropriate resource client in `src/ifpa_api/resources/`:

```python
# src/ifpa_api/resources/players.py
def new_feature(self, player_id: int) -> NewFeatureResponse:
    """Get new feature data for a player.

    Args:
        player_id: The player's unique identifier

    Returns:
        New feature data

    Raises:
        IfpaApiError: If the API request fails

    Example:
        ```python
        data = client.player(12345).new_feature()
        print(f"Feature: {data.feature_name}")
        ```
    """
    response = self._http._request("GET", f"/player/{player_id}/new-feature")
    return NewFeatureResponse.model_validate(response)
```

### 3. Add Tests

Add unit and integration tests:

```python
# tests/unit/test_players.py
def test_new_feature(mock_http_client):
    """Test new feature endpoint."""
    # Test implementation

# tests/integration/test_players_integration.py
@pytest.mark.integration
def test_new_feature_integration(client):
    """Test new feature with real API."""
    # Test implementation
```

### 4. Update Documentation

- Add example to README.md
- Update API coverage count
- Document in CHANGELOG.md

## Code Review Process

All pull requests require review before merging:

1. **Automated Checks**: GitHub Actions runs tests, linting, and type checking
2. **Code Review**: A maintainer reviews the code for quality and correctness
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, a maintainer will merge the PR

**Review Criteria**:
- Code follows style guidelines
- Tests are comprehensive
- Documentation is clear and complete
- No breaking changes (or clearly documented)
- Performance implications considered
- Error handling is appropriate

## Release Process

Maintainers handle releases:

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md with release date
3. Create git tag: `git tag v0.1.0`
4. Push tag: `git push origin v0.1.0`
5. GitHub Actions builds and publishes to PyPI

## Getting Help

- **Questions**: Open a GitHub Discussion or Issue
- **Chat**: Contact maintainers via email or GitHub
- **Documentation**: Check the [API documentation](https://api.ifpapinball.com/docs)

## Recognition

Contributors are recognized in:
- CHANGELOG.md release notes
- GitHub contributor graph
- Project acknowledgments

Thank you for contributing to the IFPA SDK and supporting the pinball community!
