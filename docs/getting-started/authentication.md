# Authentication

The IFPA SDK requires an API key to authenticate with the IFPA API. This guide explains how to obtain and configure your API key.

## Obtaining an API Key

To use the IFPA API, you need to obtain an API key from IFPA:

1. Visit the [IFPA API Documentation](https://api.ifpapinball.com/docs)
2. Follow the instructions to request an API key
3. IFPA will provide you with an API key string

!!! note
    API keys are free and required for all API requests. Keep your API key secure and never commit it to version control.

## Configuration Methods

There are two ways to provide your API key to the SDK:

### Method 1: Environment Variable (Recommended)

Set the `IFPA_API_KEY` environment variable:

=== "Bash/Zsh (macOS/Linux)"

    ```bash
    export IFPA_API_KEY='your-api-key-here'
    ```

    To make this permanent, add it to your shell profile:

    ```bash
    # For bash
    echo 'export IFPA_API_KEY="your-api-key-here"' >> ~/.bashrc
    source ~/.bashrc

    # For zsh
    echo 'export IFPA_API_KEY="your-api-key-here"' >> ~/.zshrc
    source ~/.zshrc
    ```

=== "Windows Command Prompt"

    ```cmd
    set IFPA_API_KEY=your-api-key-here
    ```

=== "Windows PowerShell"

    ```powershell
    $env:IFPA_API_KEY = "your-api-key-here"
    ```

=== "Python dotenv"

    Use `python-dotenv` to load from a `.env` file:

    ```bash
    pip install python-dotenv
    ```

    Create a `.env` file:

    ```
    IFPA_API_KEY=your-api-key-here
    ```

    Load it in your code:

    ```python
    from dotenv import load_dotenv
    from ifpa_sdk import IfpaClient

    load_dotenv()  # Load .env file
    client = IfpaClient()  # Uses IFPA_API_KEY from environment
    ```

Then initialize the client without parameters:

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()  # Automatically uses IFPA_API_KEY
```

### Method 2: Constructor Parameter

Pass the API key directly to the constructor:

```python
from ifpa_sdk import IfpaClient

client = IfpaClient(api_key='your-api-key-here')
```

!!! warning
    Avoid hardcoding API keys in your source code. Use environment variables or secure configuration management instead.

## Best Practices

### 1. Never Commit API Keys

Add your `.env` file or any files containing API keys to `.gitignore`:

```gitignore
# .gitignore
.env
secrets.py
credentials.json
```

### 2. Use Environment Variables in Production

In production environments, configure API keys through your deployment platform:

- **Heroku**: `heroku config:set IFPA_API_KEY=your-key`
- **AWS Lambda**: Environment variables in Lambda configuration
- **Docker**: Pass via `-e` flag or docker-compose
- **Kubernetes**: Store in Secrets

### 3. Rotate Keys Regularly

If you suspect your API key has been compromised:

1. Contact IFPA to rotate your key
2. Update the key in your environment
3. Restart your application

### 4. Use Different Keys for Different Environments

Maintain separate API keys for:

- Development
- Testing
- Production

## Verifying Authentication

Test that your API key is configured correctly:

```python
from ifpa_sdk import IfpaClient, MissingApiKeyError

try:
    client = IfpaClient()
    # Make a simple request
    stats = client.stats.global_stats()
    print(f"Authentication successful! Total players: {stats.total_players}")
except MissingApiKeyError:
    print("Error: API key not configured")
except Exception as e:
    print(f"Error: {e}")
```

## Troubleshooting

### "MissingApiKeyError: No API key provided"

This error occurs when:

1. `IFPA_API_KEY` environment variable is not set
2. No `api_key` parameter was passed to the constructor

**Solution**:

```python
# Check if environment variable is set
import os
print(os.getenv('IFPA_API_KEY'))  # Should print your key, not None

# Or pass explicitly
client = IfpaClient(api_key='your-key')
```

### "IfpaApiError: [401] Unauthorized"

This means your API key is invalid or has been revoked.

**Solution**:

1. Verify you're using the correct API key
2. Check that the key hasn't expired
3. Request a new key from IFPA if needed

### Environment Variable Not Loading

If your environment variable isn't being recognized:

```python
import os

# Debug: Check all environment variables
print(os.environ)

# Debug: Check specific variable
api_key = os.getenv('IFPA_API_KEY')
print(f"API Key: {api_key}")

if api_key:
    client = IfpaClient(api_key=api_key)
else:
    print("IFPA_API_KEY not found in environment")
```

## Security Considerations

### API Key Storage

- **DO**: Store in environment variables or secure secret management systems
- **DO**: Use different keys for different environments
- **DO**: Rotate keys regularly
- **DON'T**: Hardcode in source code
- **DON'T**: Commit to version control
- **DON'T**: Share keys in public forums or logs

### Logging

Be careful not to log your API key:

```python
import logging

# Bad - logs the key
logging.info(f"Using API key: {api_key}")

# Good - doesn't expose the key
logging.info("API client initialized")
```

### CI/CD Pipelines

In CI/CD environments, use secret management:

=== "GitHub Actions"

    ```yaml
    - name: Run tests
      env:
        IFPA_API_KEY: ${{ secrets.IFPA_API_KEY }}
      run: pytest
    ```

=== "GitLab CI"

    ```yaml
    test:
      script:
        - pytest
      variables:
        IFPA_API_KEY: $CI_IFPA_API_KEY
    ```

=== "CircleCI"

    ```yaml
    jobs:
      test:
        steps:
          - run:
              name: Run tests
              command: pytest
              environment:
                IFPA_API_KEY: ${IFPA_API_KEY}
    ```

## Example: Secure Configuration Class

Here's a pattern for secure API key management:

```python
from dataclasses import dataclass
import os
from typing import Optional

@dataclass
class Config:
    """Application configuration."""
    ifpa_sdk_key: str

    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables."""
        api_key = os.getenv('IFPA_API_KEY')
        if not api_key:
            raise ValueError("IFPA_API_KEY environment variable not set")
        return cls(ifpa_sdk_key=api_key)

# Usage
config = Config.from_env()
client = IfpaClient(api_key=config.ifpa_sdk_key)
```

## Next Steps

Now that you have authentication configured:

1. [Follow the quick start guide](quickstart.md)
2. [Explore usage examples](../usage/directors.md)
3. [Learn about configuration options](configuration.md)
