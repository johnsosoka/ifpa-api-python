"""Director resource package.

Provides access to tournament director information, their tournament history,
and search capabilities.
"""

from .client import DirectorClient

__all__ = ["DirectorClient"]
