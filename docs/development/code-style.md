# Code Style

The IFPA SDK enforces strict code style using automated tools.

## Code Formatters and Linters

### Black

Code formatting with 100 character line length:

```bash
# Format all code
poetry run black src tests

# Check without modifying
poetry run black --check src tests
```

Configuration in `pyproject.toml`:

```toml
[tool.black]
line-length = 100
target-version = ["py311"]
```

### Ruff

Fast Python linting:

```bash
# Check linting
poetry run ruff check src tests

# Auto-fix issues
poetry run ruff check --fix src tests
```

### mypy

Static type checking with strict mode:

```bash
# Type check source code
poetry run mypy src
```

## Pre-commit Hooks

Install pre-commit hooks to automatically check code before commits:

```bash
poetry run pre-commit install
```

Hooks run automatically on `git commit`. Run manually:

```bash
poetry run pre-commit run --all-files
```

## Code Style Guidelines

### Type Hints

All public functions must have complete type hints:

```python
# Good
def get_player(player_id: int | str) -> Player:
    ...

# Bad - missing types
def get_player(player_id):
    ...
```

### Docstrings

All public APIs must have docstrings in Google style:

```python
def search_players(name: str, count: int | None = None) -> PlayerSearchResponse:
    """Search for players by name.

    Args:
        name: Player name to search for
        count: Maximum number of results

    Returns:
        Search results with player list

    Raises:
        IfpaApiError: If the API request fails

    Example:
        ```python
        results = client.player.search(name="John", count=25)
        ```
    """
```

### Function Length

Keep functions focused and under 20 lines:

```python
# Good - single responsibility
def get_player_name(player: Player) -> str:
    return f"{player.first_name} {player.last_name}"

# Bad - too long, multiple responsibilities
def process_player(player_id: int):
    # 50 lines of code doing multiple things
    ...
```

### Import Organization

Use Ruff's isort integration for consistent imports:

```python
# Standard library
import os
from typing import Any

# Third-party
import requests
from pydantic import BaseModel

# Local
from ifpa_api.config import Config
from ifpa_api.exceptions import IfpaError
```

## Editor Configuration

### VS Code

`.vscode/settings.json`:

```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.linting.mypyEnabled": true,
  "editor.formatOnSave": true
}
```

### PyCharm

1. Install Black plugin
2. Enable Ruff
3. Configure mypy as external tool

For complete guidelines, see [CONTRIBUTING.md](../contributing.md).
