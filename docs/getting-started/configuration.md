# Configuration

This guide covers all configuration options available in the IFPA API package.

## Client Configuration

Both `IfpaClient` (sync) and `AsyncIfpaClient` (async) accept the same configuration parameters:

=== "Async"
    ```python
    from ifpa_api import AsyncIfpaClient

    client = AsyncIfpaClient(
        api_key='your-api-key',  # API key for authentication
        base_url='https://api.ifpapinball.com',  # API base URL
        timeout=10.0,  # Request timeout in seconds
        validate_requests=True  # Enable request validation
    )
    ```

=== "Sync"
    ```python
    from ifpa_api import IfpaClient

    client = IfpaClient(
        api_key='your-api-key',  # API key for authentication
        base_url='https://api.ifpapinball.com',  # API base URL
        timeout=10.0,  # Request timeout in seconds
        validate_requests=True  # Enable request validation
    )
    ```

## Configuration Options

### API Key

**Type**: `str | None`
**Default**: `None` (reads from `IFPA_API_KEY` environment variable)

Your IFPA API key for authentication.

=== "Async"
    ```python
    # From environment variable (recommended)
    client = AsyncIfpaClient()

    # Explicit key
    client = AsyncIfpaClient(api_key='your-api-key')
    ```

=== "Sync"
    ```python
    # From environment variable (recommended)
    client = IfpaClient()

    # Explicit key
    client = IfpaClient(api_key='your-api-key')
    ```

See [Authentication](authentication.md) for detailed API key setup.

### Base URL

**Type**: `str | None`
**Default**: `https://api.ifpapinball.com`

The base URL for the IFPA API. You typically don't need to change this unless:

- Using a proxy or gateway
- Testing against a mock server
- IFPA changes their base URL

=== "Async"
    ```python
    # Default - no need to specify
    client = AsyncIfpaClient()

    # Custom base URL
    client = AsyncIfpaClient(base_url='https://custom-api.example.com')
    ```

=== "Sync"
    ```python
    # Default - no need to specify
    client = IfpaClient()

    # Custom base URL
    client = IfpaClient(base_url='https://custom-api.example.com')
    ```

### Timeout

**Type**: `float`
**Default**: `10.0` seconds

Maximum time to wait for API responses. Applies to each individual request.

=== "Async"
    ```python
    # Default 10 second timeout
    client = AsyncIfpaClient()

    # Custom timeout
    client = AsyncIfpaClient(timeout=30.0)  # 30 seconds

    # Shorter timeout for fast-fail behavior
    client = AsyncIfpaClient(timeout=5.0)   # 5 seconds
    ```

=== "Sync"
    ```python
    # Default 10 second timeout
    client = IfpaClient()

    # Custom timeout
    client = IfpaClient(timeout=30.0)  # 30 seconds

    # Shorter timeout for fast-fail behavior
    client = IfpaClient(timeout=5.0)   # 5 seconds
    ```

**Recommendations**:
- **Fast operations** (search, single resource): 5-10 seconds
- **Slow operations** (large result sets): 15-30 seconds
- **Production**: 10-15 seconds with retry logic
- **Development**: 30+ seconds for debugging

### Request Validation

**Type**: `bool`
**Default**: `True`

Enable or disable Pydantic validation of request parameters before sending to the API.

=== "Async"
    ```python
    # Validation enabled (recommended)
    client = AsyncIfpaClient(validate_requests=True)

    # Validation disabled (not recommended)
    client = AsyncIfpaClient(validate_requests=False)
    ```

=== "Sync"
    ```python
    # Validation enabled (recommended)
    client = IfpaClient(validate_requests=True)

    # Validation disabled (not recommended)
    client = IfpaClient(validate_requests=False)
    ```

**When to enable** (default):
- Development and testing
- When you want early error detection
- When you want clear validation error messages

**When to disable**:
- Performance-critical production code (marginal gain)
- When you're certain parameters are valid
- When debugging validation issues

**Example with validation**:

=== "Async"
    ```python
    from ifpa_api import AsyncIfpaClient, IfpaClientValidationError
    import asyncio

    async def main():
        async with AsyncIfpaClient(validate_requests=True) as client:
            try:
                # This will fail validation before making the request
                rankings = await client.rankings.wppr(count=500)  # Max is 250
            except IfpaClientValidationError as e:
                print(f"Validation error: {e.message}")

    asyncio.run(main())
    ```

=== "Sync"
    ```python
    from ifpa_api import IfpaClient, IfpaClientValidationError

    with IfpaClient(validate_requests=True) as client:
        try:
            # This will fail validation before making the request
            rankings = client.rankings.wppr(count=500)  # Max is 250
        except IfpaClientValidationError as e:
            print(f"Validation error: {e.message}")
    ```

## Environment Variables

The package reads these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `IFPA_API_KEY` | API key for authentication | None (required) |

Future environment variables (not currently used):
- `IFPA_BASE_URL` - Override base URL
- `IFPA_TIMEOUT` - Default timeout
- `IFPA_LOG_LEVEL` - Logging level

## Complete Configuration Example

=== "Async"
    ```python
    import os
    import asyncio
    from ifpa_api import AsyncIfpaClient

    # Load from environment
    api_key = os.getenv('IFPA_API_KEY')
    timeout = float(os.getenv('IFPA_TIMEOUT', '10.0'))

    async def main():
        # Configure client
        async with AsyncIfpaClient(
            api_key=api_key,
            timeout=timeout,
            validate_requests=True
        ) as client:
            # Use the client
            player = await client.player.get(25584)

    asyncio.run(main())
    ```

=== "Sync"
    ```python
    import os
    from ifpa_api import IfpaClient

    # Load from environment
    api_key = os.getenv('IFPA_API_KEY')
    timeout = float(os.getenv('IFPA_TIMEOUT', '10.0'))

    # Configure client
    with IfpaClient(
        api_key=api_key,
        timeout=timeout,
        validate_requests=True
    ) as client:
        # Use the client
        player = client.player.get(25584)
    ```

## Configuration Patterns

### Development Configuration

=== "Async"
    ```python
    from ifpa_api import AsyncIfpaClient

    # Development: Longer timeout, strict validation
    dev_client = AsyncIfpaClient(
        timeout=30.0,
        validate_requests=True
    )
    ```

=== "Sync"
    ```python
    from ifpa_api import IfpaClient

    # Development: Longer timeout, strict validation
    dev_client = IfpaClient(
        timeout=30.0,
        validate_requests=True
    )
    ```

### Production Configuration

=== "Async"
    ```python
    import os
    from ifpa_api import AsyncIfpaClient

    # Production: Balanced timeout, optional validation
    prod_client = AsyncIfpaClient(
        api_key=os.environ['IFPA_API_KEY'],  # Explicit for production
        timeout=15.0,
        validate_requests=True  # Keep enabled for safety
    )
    ```

=== "Sync"
    ```python
    import os
    from ifpa_api import IfpaClient

    # Production: Balanced timeout, optional validation
    prod_client = IfpaClient(
        api_key=os.environ['IFPA_API_KEY'],  # Explicit for production
        timeout=15.0,
        validate_requests=True  # Keep enabled for safety
    )
    ```

### Testing Configuration

=== "Async"
    ```python
    from ifpa_api import AsyncIfpaClient

    # Testing: Mock server, fast timeout
    test_client = AsyncIfpaClient(
        api_key='test-key',
        base_url='http://localhost:8000',  # Mock server
        timeout=5.0,
        validate_requests=True
    )
    ```

=== "Sync"
    ```python
    from ifpa_api import IfpaClient

    # Testing: Mock server, fast timeout
    test_client = IfpaClient(
        api_key='test-key',
        base_url='http://localhost:8000',  # Mock server
        timeout=5.0,
        validate_requests=True
    )
    ```

## Configuration Class Pattern

For complex applications, create a configuration class:

=== "Async"
    ```python
    from dataclasses import dataclass
    import os
    from ifpa_api import AsyncIfpaClient

    @dataclass
    class IfpaConfig:
        """IFPA API client configuration."""
        api_key: str
        base_url: str = 'https://api.ifpapinball.com'
        timeout: float = 10.0
        validate_requests: bool = True

        @classmethod
        def from_env(cls) -> 'IfpaConfig':
            """Load configuration from environment variables."""
            api_key = os.getenv('IFPA_API_KEY')
            if not api_key:
                raise ValueError("IFPA_API_KEY not set")

            return cls(
                api_key=api_key,
                base_url=os.getenv('IFPA_BASE_URL', cls.base_url),
                timeout=float(os.getenv('IFPA_TIMEOUT', str(cls.timeout))),
                validate_requests=os.getenv('IFPA_VALIDATE', 'true').lower() == 'true'
            )

        def create_async_client(self) -> AsyncIfpaClient:
            """Create a configured async client."""
            return AsyncIfpaClient(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
                validate_requests=self.validate_requests
            )

    # Usage
    config = IfpaConfig.from_env()
    client = config.create_async_client()
    ```

=== "Sync"
    ```python
    from dataclasses import dataclass
    import os
    from ifpa_api import IfpaClient

    @dataclass
    class IfpaConfig:
        """IFPA API client configuration."""
        api_key: str
        base_url: str = 'https://api.ifpapinball.com'
        timeout: float = 10.0
        validate_requests: bool = True

        @classmethod
        def from_env(cls) -> 'IfpaConfig':
            """Load configuration from environment variables."""
            api_key = os.getenv('IFPA_API_KEY')
            if not api_key:
                raise ValueError("IFPA_API_KEY not set")

            return cls(
                api_key=api_key,
                base_url=os.getenv('IFPA_BASE_URL', cls.base_url),
                timeout=float(os.getenv('IFPA_TIMEOUT', str(cls.timeout))),
                validate_requests=os.getenv('IFPA_VALIDATE', 'true').lower() == 'true'
            )

        def create_client(self) -> IfpaClient:
            """Create a configured client."""
            return IfpaClient(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
                validate_requests=self.validate_requests
            )

    # Usage
    config = IfpaConfig.from_env()
    client = config.create_client()
    ```

## HTTP Session Configuration

The sync client uses `requests` internally, while the async client uses `httpx`. Both:

- Maintain persistent sessions for connection pooling
- Set the `X-API-Key` header automatically
- Handle timeouts
- Parse JSON responses

**Connection pooling**: Both clients reuse HTTP connections for better performance. Always close the client when done:

=== "Async"
    ```python
    import asyncio

    # Option 1: Manual close
    async def main():
        client = AsyncIfpaClient()
        try:
            player = await client.player.get(25584)
        finally:
            await client.close()  # Must use await with async client!

    # Option 2: Context manager (recommended)
    async def main():
        async with AsyncIfpaClient() as client:
            player = await client.player.get(25584)

    asyncio.run(main())
    ```

=== "Sync"
    ```python
    # Option 1: Manual close
    client = IfpaClient()
    try:
        player = client.player.get(25584)
    finally:
        client.close()

    # Option 2: Context manager (recommended)
    with IfpaClient() as client:
        player = client.player.get(25584)
    ```

!!! warning "Async Client Cleanup"
    The async client **must** be closed with `await client.close()` if not using a context manager. Failing to close it will leak HTTP connections and cause `ResourceWarning`s.

## Performance Considerations

### Timeout Tuning

Balance between reliability and user experience:

- **Too short**: Requests fail unnecessarily on slow networks
- **Too long**: Users wait too long for failed requests

Recommendations by use case:

| Use Case | Recommended Timeout |
|----------|-------------------|
| Interactive UI | 5-10 seconds |
| Background jobs | 30-60 seconds |
| Bulk operations | 60+ seconds |
| Mobile apps | 5-15 seconds |

### Request Validation

Request validation has minimal performance impact (< 1ms per request). Keep it enabled unless you're making thousands of requests per second and have verified all inputs are valid.

## Troubleshooting

### Timeout Errors

If you're getting timeout errors:

```python
from ifpa_api import IfpaClient, IfpaApiError

client = IfpaClient(timeout=30.0)  # Increase timeout

try:
    rankings = client.rankings.wppr(count=250)
except IfpaApiError as e:
    if e.status_code is None:  # Likely a timeout
        print("Request timed out - consider increasing timeout")
```

### Validation Errors

If validation is too strict:

```python
# Temporary: Disable validation
client = IfpaClient(validate_requests=False)

# Better: Fix the parameters
rankings = client.rankings.wppr(count=250)  # Max allowed
```

### Connection Issues

If you're having connection issues:

```python
from ifpa_api import IfpaClient

# Check base URL
client = IfpaClient()
print(f"Using base URL: {client._config.base_url}")

# Test connectivity
try:
    rankings = client.rankings.wppr(count=1)
    print("Connection successful")
except Exception as e:
    print(f"Connection failed: {e}")
```

## Next Steps

- [Quick Start Guide](quickstart.md)
- [Usage Examples](../resources/directors.md)
- [Error Handling](../guides/error-handling.md)
