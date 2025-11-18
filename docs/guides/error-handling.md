# Error Handling

Learn how to handle errors when using the IFPA SDK.

## Exception Hierarchy

The SDK provides a clear exception hierarchy:

```python
from ifpa_api import (
    IfpaError,  # Base exception
    MissingApiKeyError,  # No API key configured
    IfpaApiError,  # API returned error
    IfpaClientValidationError  # Request validation failed
)
```

## Handling API Errors

```python
from ifpa_api import IfpaClient, IfpaApiError

client = IfpaClient()

try:
    player = client.player(12345).details()
except IfpaApiError as e:
    print(f"API error [{e.status_code}]: {e.message}")
    print(f"Response body: {e.response_body}")
```

## Handling Missing API Key

```python
from ifpa_api import IfpaClient, MissingApiKeyError

try:
    client = IfpaClient()
except MissingApiKeyError:
    print("Error: IFPA_API_KEY environment variable not set")
```

## Handling Validation Errors

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

## Catch-All Error Handling

```python
from ifpa_api import IfpaClient, IfpaError

client = IfpaClient()

try:
    player = client.player(12345).details()
except IfpaError as e:
    # Catches all SDK errors
    print(f"SDK error: {e}")
```

## Best Practices

### 1. Always Handle Authentication Errors

```python
from ifpa_api import IfpaClient, MissingApiKeyError, IfpaApiError

try:
    client = IfpaClient()
    player = client.player(12345).details()
except MissingApiKeyError:
    print("Configure IFPA_API_KEY environment variable")
except IfpaApiError as e:
    if e.status_code == 401:
        print("Invalid API key")
```

### 2. Handle 404 Not Found

```python
try:
    player = client.player(999999).details()
except IfpaApiError as e:
    if e.status_code == 404:
        print("Player not found")
```

### 3. Retry on Temporary Errors

```python
import time
from ifpa_api import IfpaClient, IfpaApiError


def get_player_with_retry(player_id: int, max_retries: int = 3):
    """Get player with retry logic."""
    client = IfpaClient()

    for attempt in range(max_retries):
        try:
            return client.player(player_id).details()
        except IfpaApiError as e:
            if e.status_code in (500, 502, 503, 504):  # Server errors
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
            raise
```

For more examples, see the [README](https://github.com/johnsosoka/ifpa-api-python#error-handling).
