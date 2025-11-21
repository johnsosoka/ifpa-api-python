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

=== "Async"
    ```python
    from ifpa_api import AsyncIfpaClient, IfpaApiError
    import asyncio

    async def main():
        async with AsyncIfpaClient() as client:
            try:
                player = await client.player.get(25584)
            except IfpaApiError as e:
                print(f"API error [{e.status_code}]: {e.message}")
                print(f"Response body: {e.response_body}")

    asyncio.run(main())
    ```

=== "Sync"
    ```python
    from ifpa_api import IfpaClient, IfpaApiError

    with IfpaClient() as client:
        try:
            player = client.player.get(25584)
        except IfpaApiError as e:
            print(f"API error [{e.status_code}]: {e.message}")
            print(f"Response body: {e.response_body}")
    ```

## Handling Missing API Key

=== "Async"
    ```python
    from ifpa_api import AsyncIfpaClient, MissingApiKeyError

    try:
        client = AsyncIfpaClient()
    except MissingApiKeyError:
        print("Error: IFPA_API_KEY environment variable not set")
    ```

=== "Sync"
    ```python
    from ifpa_api import IfpaClient, MissingApiKeyError

    try:
        client = IfpaClient()
    except MissingApiKeyError:
        print("Error: IFPA_API_KEY environment variable not set")
    ```

## Handling Validation Errors

=== "Async"
    ```python
    from ifpa_api import AsyncIfpaClient, IfpaClientValidationError
    import asyncio

    async def main():
        async with AsyncIfpaClient(validate_requests=True) as client:
            try:
                # This will fail validation (count > 250)
                rankings = await client.rankings.wppr(count=500)
            except IfpaClientValidationError as e:
                print(f"Validation error: {e.message}")
                print(f"Details: {e.validation_errors}")

    asyncio.run(main())
    ```

=== "Sync"
    ```python
    from ifpa_api import IfpaClient, IfpaClientValidationError

    with IfpaClient(validate_requests=True) as client:
        try:
            # This will fail validation (count > 250)
            rankings = client.rankings.wppr(count=500)
        except IfpaClientValidationError as e:
            print(f"Validation error: {e.message}")
            print(f"Details: {e.validation_errors}")
    ```

## Catch-All Error Handling

=== "Async"
    ```python
    from ifpa_api import AsyncIfpaClient, IfpaError
    import asyncio

    async def main():
        async with AsyncIfpaClient() as client:
            try:
                player = await client.player.get(25584)
            except IfpaError as e:
                # Catches all SDK errors
                print(f"SDK error: {e}")

    asyncio.run(main())
    ```

=== "Sync"
    ```python
    from ifpa_api import IfpaClient, IfpaError

    with IfpaClient() as client:
        try:
            player = client.player.get(25584)
        except IfpaError as e:
            # Catches all SDK errors
            print(f"SDK error: {e}")
    ```

## Best Practices

### 1. Always Handle Authentication Errors

=== "Async"
    ```python
    from ifpa_api import AsyncIfpaClient, MissingApiKeyError, IfpaApiError
    import asyncio

    async def main():
        try:
            async with AsyncIfpaClient() as client:
                player = await client.player.get(25584)
        except MissingApiKeyError:
            print("Configure IFPA_API_KEY environment variable")
        except IfpaApiError as e:
            if e.status_code == 401:
                print("Invalid API key")

    asyncio.run(main())
    ```

=== "Sync"
    ```python
    from ifpa_api import IfpaClient, MissingApiKeyError, IfpaApiError

    try:
        with IfpaClient() as client:
            player = client.player.get(25584)
    except MissingApiKeyError:
        print("Configure IFPA_API_KEY environment variable")
    except IfpaApiError as e:
        if e.status_code == 401:
            print("Invalid API key")
    ```

### 2. Handle 404 Not Found

=== "Async"
    ```python
    async with AsyncIfpaClient() as client:
        try:
            player = await client.player.get(999999)
        except IfpaApiError as e:
            if e.status_code == 404:
                print("Player not found")

        # Or use the convenience method
        player = await client.player.get_or_none(999999)
        if player is None:
            print("Player not found")
    ```

=== "Sync"
    ```python
    with IfpaClient() as client:
        try:
            player = client.player.get(999999)
        except IfpaApiError as e:
            if e.status_code == 404:
                print("Player not found")

        # Or use the convenience method
        player = client.player.get_or_none(999999)
        if player is None:
            print("Player not found")
    ```

### 3. Retry on Temporary Errors

=== "Async"
    ```python
    import asyncio
    from ifpa_api import AsyncIfpaClient, IfpaApiError


    async def get_player_with_retry(player_id: int, max_retries: int = 3):
        """Get player with retry logic."""
        async with AsyncIfpaClient() as client:
            for attempt in range(max_retries):
                try:
                    return await client.player.get(player_id)
                except IfpaApiError as e:
                    if e.status_code in (500, 502, 503, 504):  # Server errors
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue
                    raise


    async def main():
        player = await get_player_with_retry(25584)
        print(f"Found: {player.first_name} {player.last_name}")


    asyncio.run(main())
    ```

=== "Sync"
    ```python
    import time
    from ifpa_api import IfpaClient, IfpaApiError


    def get_player_with_retry(player_id: int, max_retries: int = 3):
        """Get player with retry logic."""
        with IfpaClient() as client:
            for attempt in range(max_retries):
                try:
                    return client.player.get(player_id)
                except IfpaApiError as e:
                    if e.status_code in (500, 502, 503, 504):  # Server errors
                        if attempt < max_retries - 1:
                            time.sleep(2 ** attempt)  # Exponential backoff
                            continue
                    raise


    player = get_player_with_retry(25584)
    print(f"Found: {player.first_name} {player.last_name}")
    ```

For more examples, see the [README](https://github.com/johnsosoka/ifpa-api-python#error-handling).
