"""Core infrastructure for the IFPA API client.

This package contains base classes, mixins, and utilities that form
the foundation of the IFPA API client architecture.
"""

from ifpa_api.core.base import (
    BaseResourceClient,
    BaseResourceContext,
    LocationFiltersMixin,
    PaginationMixin,
)
from ifpa_api.core.deprecation import deprecated, issue_deprecation_warning

__all__ = [
    "BaseResourceClient",
    "BaseResourceContext",
    "LocationFiltersMixin",
    "PaginationMixin",
    "deprecated",
    "issue_deprecation_warning",
]
