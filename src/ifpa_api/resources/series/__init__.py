"""Series resource package.

Provides access to tournament series information, standings, player cards,
and statistics.
"""

from .client import SeriesClient
from .context import _SeriesContext
from .query_builder import SeriesQueryBuilder

__all__ = ["SeriesClient", "_SeriesContext", "SeriesQueryBuilder"]
