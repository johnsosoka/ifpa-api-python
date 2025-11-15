"""Common models and enums shared across multiple resources.

This module contains base models, shared enums, and common structures used
throughout the SDK.
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict


class TimePeriod(str, Enum):
    """Time period filter for tournament and event queries.

    Attributes:
        PAST: Historical/completed tournaments
        FUTURE: Upcoming/scheduled tournaments
    """

    PAST = "past"
    FUTURE = "future"


class RankingSystem(str, Enum):
    """IFPA ranking system types.

    Attributes:
        MAIN: Main WPPR (World Pinball Player Rankings)
        WOMEN: Women's rankings
        YOUTH: Youth rankings
        VIRTUAL: Virtual tournament rankings
        PRO: Professional circuit rankings
    """

    MAIN = "main"
    WOMEN = "women"
    YOUTH = "youth"
    VIRTUAL = "virtual"
    PRO = "pro"


class ResultType(str, Enum):
    """Tournament result activity status.

    Attributes:
        ACTIVE: Currently counting toward rankings
        NONACTIVE: Not currently active (but not yet inactive)
        INACTIVE: No longer counting toward rankings
    """

    ACTIVE = "active"
    NONACTIVE = "nonactive"
    INACTIVE = "inactive"


class TournamentType(str, Enum):
    """Tournament category types.

    Attributes:
        OPEN: Open tournament (all players)
        WOMEN: Women-only tournament
    """

    OPEN = "open"
    WOMEN = "women"


class IfpaBaseModel(BaseModel):
    """Base model for all IFPA SDK Pydantic models.

    Provides common configuration for all models, including:
    - Allowing extra fields from API responses (forward compatibility)
    - Strict validation
    - Support for field aliases
    """

    model_config = ConfigDict(
        extra="ignore",  # Ignore unknown fields from API for forward compatibility
        validate_assignment=True,  # Validate on assignment
        use_enum_values=False,  # Keep enum instances, don't convert to values
        populate_by_name=True,  # Allow populating by field name or alias
    )
