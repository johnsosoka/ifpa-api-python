# Installation

This guide covers how to install the IFPA SDK and verify your installation.

## Requirements

- Python 3.11 or higher
- pip (Python package installer)

## Install from PyPI

The simplest way to install the IFPA SDK is using pip:

```bash
pip install ifpa-sdk
```

This will install the latest stable version from [PyPI](https://pypi.org/project/ifpa-sdk/).

## Verify Installation

After installation, verify that the SDK is installed correctly:

```python
import ifpa_sdk

print(ifpa_sdk.__version__)  # Should print: 0.1.0
```

You can also check the installed version using pip:

```bash
pip show ifpa-sdk
```

## Install in a Virtual Environment (Recommended)

It's recommended to install the SDK in a virtual environment to avoid dependency conflicts:

### Using venv (Standard Library)

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install the SDK
pip install ifpa-sdk
```

### Using Poetry

If you're using Poetry for dependency management:

```bash
# Add to your project
poetry add ifpa-sdk

# Or install in a new project
poetry init
poetry add ifpa-sdk
poetry install
```

## Install from Source

To install the latest development version from GitHub:

```bash
pip install git+https://github.com/jscom/ifpa-sdk.git
```

Or clone the repository and install locally:

```bash
git clone https://github.com/jscom/ifpa-sdk.git
cd ifpa-sdk
pip install -e .
```

## Development Installation

If you want to contribute to the SDK, follow the [Contributing Guide](../contributing.md) for development setup instructions.

Quick version:

```bash
# Clone the repository
git clone https://github.com/jscom/ifpa-sdk.git
cd ifpa-sdk

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

## Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade ifpa-sdk
```

With Poetry:

```bash
poetry update ifpa-sdk
```

## Uninstalling

To remove the SDK:

```bash
pip uninstall ifpa-sdk
```

With Poetry:

```bash
poetry remove ifpa-sdk
```

## Dependencies

The SDK has minimal dependencies:

- **requests** (^2.31.0) - HTTP library for API requests
- **pydantic** (^2.0.0) - Data validation and settings management

These dependencies will be automatically installed when you install the SDK.

## Python Version Support

The SDK requires Python 3.11 or higher. Support for Python versions follows the official Python release cycle:

- **Supported**: Python 3.11, 3.12
- **Not Supported**: Python 3.10 and earlier

## Platform Support

The SDK is platform-independent and works on:

- macOS
- Linux
- Windows

## Troubleshooting

### "No module named 'ifpa_sdk'"

If you get this error, ensure:

1. The SDK is installed in the correct environment
2. You're using the correct Python interpreter
3. The installation completed successfully

```bash
# Check which Python you're using
which python3
python3 --version

# Check if SDK is installed
pip list | grep ifpa-sdk
```

### Import Errors

If you encounter import errors with dependencies:

```bash
# Reinstall with --force-reinstall
pip install --force-reinstall ifpa-sdk

# Or with --no-cache-dir
pip install --no-cache-dir ifpa-sdk
```

### Permission Denied

If you get permission errors during installation:

```bash
# Install for current user only
pip install --user ifpa-sdk

# Or use a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install ifpa-sdk
```

## Next Steps

Now that you have the SDK installed:

1. [Set up authentication](authentication.md)
2. [Follow the quick start guide](quickstart.md)
3. [Explore usage examples](../usage/directors.md)
