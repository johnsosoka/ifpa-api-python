# Exceptions Reference

The SDK provides a clear exception hierarchy for different error scenarios.

## Exception Hierarchy

```
IfpaError (base)
├── MissingApiKeyError
├── IfpaApiError
├── PlayersNeverMetError
└── IfpaClientValidationError
```

## IfpaError

Base exception for all IFPA SDK errors.

```python
class IfpaError(Exception):
    pass
```

Catch this to handle any SDK-related error:

```python
try:
    player = client.player(12345).details()
except IfpaError as e:
    print(f"SDK error: {e}")
```

## MissingApiKeyError

Raised when no API key is provided or found in environment.

```python
class MissingApiKeyError(IfpaError):
    pass
```

This occurs during client initialization when:

- No `api_key` is passed to the constructor
- The `IFPA_API_KEY` environment variable is not set

**Example:**

```python
from ifpa_api import IfpaClient, MissingApiKeyError

try:
    client = IfpaClient()
except MissingApiKeyError:
    print("Error: API key not configured")
    print("Set IFPA_API_KEY environment variable")
```

## IfpaApiError

Raised when the IFPA API returns a non-2xx HTTP status code.

```python
class IfpaApiError(IfpaError):
    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: Any | None = None,
    ) -> None
```

**Attributes:**

- `message` (str): Human-readable error message
- `status_code` (int | None): HTTP status code from API
- `response_body` (Any | None): Raw response body

**Common Status Codes:**

- `400`: Bad Request - Invalid parameters
- `401`: Unauthorized - Invalid API key
- `404`: Not Found - Resource doesn't exist
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error - API server error
- `503`: Service Unavailable - API temporarily unavailable

**Example:**

```python
from ifpa_api import IfpaClient, IfpaApiError

client = IfpaClient()

try:
    player = client.player(999999).details()
except IfpaApiError as e:
    print(f"Error [{e.status_code}]: {e.message}")

    if e.status_code == 404:
        print("Player not found")
    elif e.status_code == 401:
        print("Invalid API key")
    elif e.status_code >= 500:
        print("Server error, try again later")
```

## IfpaClientValidationError

Raised when client-side request validation fails.

```python
class IfpaClientValidationError(IfpaError):
    def __init__(
        self,
        message: str,
        validation_errors: Any | None = None
    ) -> None
```

This occurs when `validate_requests=True` and Pydantic model validation fails for request parameters.

**Attributes:**

- `message` (str): Human-readable error message
- `validation_errors` (Any | None): Pydantic validation error details

**Example:**

```python
from ifpa_api import IfpaClient, IfpaClientValidationError

client = IfpaClient(validate_requests=True)

try:
    # This will fail validation (count > 250)
    rankings = client.rankings.wppr(count=500)
except IfpaClientValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Details: {e.validation_errors}")
```

## Best Practices

### 1. Catch Specific Exceptions

Catch the most specific exception first:

```python
from ifpa_api import (
    IfpaClient,
    MissingApiKeyError,
    IfpaApiError,
    IfpaClientValidationError,
    IfpaError
)

try:
    client = IfpaClient()
    player = client.player(12345).details()
except MissingApiKeyError:
    print("API key not configured")
except IfpaClientValidationError as e:
    print(f"Invalid parameters: {e.message}")
except IfpaApiError as e:
    print(f"API error [{e.status_code}]: {e.message}")
except IfpaError as e:
    print(f"Unknown SDK error: {e}")
```

### 2. Handle Common Status Codes

```python
try:
    player = client.player(player_id).details()
except IfpaApiError as e:
    if e.status_code == 404:
        return None  # Player not found
    elif e.status_code == 401:
        raise  # Re-raise authentication errors
    elif e.status_code >= 500:
        # Retry on server errors
        time.sleep(1)
        player = client.player(player_id).details()
```

### 3. Log Errors Appropriately

```python
import logging

logger = logging.getLogger(__name__)

try:
    player = client.player(12345).details()
except IfpaApiError as e:
    logger.error(
        "API error",
        extra={
            "status_code": e.status_code,
            "message": e.message,
            "player_id": 12345
        }
    )
    raise
```

## PlayersNeverMetError

Raised when requesting PvP (player vs player) data for two players who have never competed together.

```python
class PlayersNeverMetError(IfpaError):
    def __init__(
        self,
        player_id: int | str,
        opponent_id: int | str,
        message: str | None = None
    ) -> None
```

This exception is raised by the SDK when the IFPA API returns a 404 error indicating that two players have never faced each other in any tournament. This provides a more semantic error than a generic 404 response.

**Attributes:**

- `player_id` (int | str): The first player's ID
- `opponent_id` (int | str): The second player's ID
- `message` (str): Error message explaining the players have never met

**Example:**

```python
from ifpa_api import IfpaClient
from ifpa_api.exceptions import PlayersNeverMetError, IfpaApiError

client = IfpaClient()

try:
    pvp = client.player(12345).pvp(67890)
    print(f"{pvp.player1_name} vs {pvp.player2_name}")
    print(f"Wins: {pvp.player1_wins} - {pvp.player2_wins}")
except PlayersNeverMetError as e:
    print(f"Players {e.player_id} and {e.opponent_id} have never competed together")
except IfpaApiError as e:
    print(f"API error: {e}")
```

**When This Occurs:**

This exception is raised specifically by the `PlayerHandle.pvp()` method when:
- The IFPA API returns HTTP 200 with `{"message": "...", "code": "404"}` in the response body
- The IFPA API returns HTTP 404 status code
- Both cases indicate the two players have never competed in the same tournament

For usage examples, see the [Error Handling Guide](../usage/error-handling.md).
