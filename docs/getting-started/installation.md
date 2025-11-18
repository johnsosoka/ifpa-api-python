# Installation

This guide covers how to install the IFPA API package and verify your installation.

## Requirements

- Python 3.11 or higher
- pip (Python package installer)

## Install from PyPI

The simplest way to install the IFPA API package is using pip:

```bash
pip install ifpa-api
```

This will install the latest stable version from [PyPI](https://pypi.org/project/ifpa-api/).

## Verify Installation

After installation, verify that the package is installed correctly:

```python
import ifpa_api

print(ifpa_api.__version__)  # Should print: 0.3.0
```

You can also check the installed version using pip:

```bash
pip show ifpa-api
```

## Install in a Virtual Environment (Recommended)

It's recommended to install the package in a virtual environment to avoid dependency conflicts:

### Using venv (Standard Library)

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install the package
pip install ifpa-api
```

### Using Poetry

If you're using Poetry for dependency management:

```bash
# Add to your project
poetry add ifpa-api

# Or install in a new project
poetry init
poetry add ifpa-api
poetry install
```

## Install from Source

To install the latest development version from GitHub:

```bash
pip install git+https://github.com/johnsosoka/ifpa-api-python.git
```

Or clone the repository and install locally:

```bash
git clone https://github.com/johnsosoka/ifpa-api-python.git
cd ifpa-api-python
pip install -e .
```

## Development Installation

If you want to contribute to the package, follow the [Contributing Guide](../contributing.md) for development setup instructions.

Quick version:

```bash
# Clone the repository
git clone https://github.com/johnsosoka/ifpa-api-python.git
cd ifpa-api-python

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
pip install --upgrade ifpa-api
```

With Poetry:

```bash
poetry update ifpa-api
```

## Uninstalling

To remove the package:

```bash
pip uninstall ifpa-api
```

With Poetry:

```bash
poetry remove ifpa-api
```

## Dependencies

The package has minimal dependencies:

- **requests** (^2.31.0) - HTTP library for API requests
- **pydantic** (^2.0.0) - Data validation and settings management

These dependencies will be automatically installed when you install the package.

## Python Version Support

The package requires Python 3.11 or higher. Support for Python versions follows the official Python release cycle:

- **Supported**: Python 3.11, 3.12
- **Not Supported**: Python 3.10 and earlier

## Platform Support

The package is platform-independent and works on:

- macOS
- Linux
- Windows

## Troubleshooting

### "No module named 'ifpa_api'"

If you get this error, ensure:

1. The package is installed in the correct environment
2. You're using the correct Python interpreter
3. The installation completed successfully

```bash
# Check which Python you're using
which python3
python3 --version

# Check if package is installed
pip list | grep ifpa-api
```

### Import Errors

If you encounter import errors with dependencies:

```bash
# Reinstall with --force-reinstall
pip install --force-reinstall ifpa-api

# Or with --no-cache-dir
pip install --no-cache-dir ifpa-api
```

### Permission Denied

If you get permission errors during installation:

```bash
# Install for current user only
pip install --user ifpa-api

# Or use a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install ifpa-api
```

## Next Steps

Now that you have the package installed:

1. [Set up authentication](authentication.md)
2. [Follow the quick start guide](quickstart.md)
3. [Explore usage examples](../usage/director.md)
