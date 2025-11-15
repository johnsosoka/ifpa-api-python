# Configuration

This guide covers all configuration options available in the IFPA SDK.

## Client Configuration

The `IfpaClient` constructor accepts several configuration parameters:

```python
from ifpa_sdk import IfpaClient

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

```python
from ifpa_sdk import IfpaClient, IfpaClientValidationError

client = IfpaClient(validate_requests=True)

try:
    # This will fail validation before making the request
    rankings = client.rankings.wppr(count=500)  # Max is 250
except IfpaClientValidationError as e:
    print(f"Validation error: {e.message}")
```

## Environment Variables

The SDK reads these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `IFPA_API_KEY` | API key for authentication | None (required) |

Future environment variables (not currently used):
- `IFPA_BASE_URL` - Override base URL
- `IFPA_TIMEOUT` - Default timeout
- `IFPA_LOG_LEVEL` - Logging level

## Complete Configuration Example

```python
import os
from ifpa_sdk import IfpaClient

# Load from environment
api_key = os.getenv('IFPA_API_KEY')
timeout = float(os.getenv('IFPA_TIMEOUT', '10.0'))

# Configure client
client = IfpaClient(
    api_key=api_key,
    timeout=timeout,
    validate_requests=True
)

# Use the client
player = client.player(12345).get()
```

## Configuration Patterns

### Development Configuration

```python
from ifpa_sdk import IfpaClient

# Development: Longer timeout, strict validation
dev_client = IfpaClient(
    timeout=30.0,
    validate_requests=True
)
```

### Production Configuration

```python
from ifpa_sdk import IfpaClient

# Production: Balanced timeout, optional validation
prod_client = IfpaClient(
    api_key=os.environ['IFPA_API_KEY'],  # Explicit for production
    timeout=15.0,
    validate_requests=True  # Keep enabled for safety
)
```

### Testing Configuration

```python
from ifpa_sdk import IfpaClient

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

```python
from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class IfpaConfig:
    """IFPA SDK configuration."""
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
            timeout=float(os.getenv('IFPA_TIMEOUT', cls.timeout)),
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

The SDK uses the `requests` library internally. The HTTP client:

- Maintains a persistent session for connection pooling
- Sets the `X-API-Key` header automatically
- Handles timeouts and retries
- Parses JSON responses

**Connection pooling**: The SDK reuses HTTP connections for better performance. Always close the client when done:

```python
# Option 1: Manual close
client = IfpaClient()
try:
    player = client.player(12345).get()
finally:
    client.close()

# Option 2: Context manager (recommended)
with IfpaClient() as client:
    player = client.player(12345).get()
```

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
from ifpa_sdk import IfpaClient, IfpaApiError

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
from ifpa_sdk import IfpaClient

# Check base URL
client = IfpaClient()
print(f"Using base URL: {client._config.base_url}")

# Test connectivity
try:
    stats = client.stats.global_stats()
    print("Connection successful")
except Exception as e:
    print(f"Connection failed: {e}")
```

## Next Steps

- [Quick Start Guide](quickstart.md)
- [Usage Examples](../usage/directors.md)
- [Error Handling](../usage/error-handling.md)
