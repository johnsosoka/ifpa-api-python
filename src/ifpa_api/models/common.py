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


class StatsRankType(str, Enum):
    """Ranking type filter for statistical queries.

    Attributes:
        OPEN: All players/tournaments
        WOMEN: Women's division only
    """

    OPEN = "OPEN"
    WOMEN = "WOMEN"


class SystemCode(str, Enum):
    """System code for overall statistics queries.

    Note: As of 2025-11, API bug causes WOMEN to return OPEN data.

    Attributes:
        OPEN: Open division statistics
        WOMEN: Women's division statistics (currently returns OPEN data due to API bug)
    """

    OPEN = "OPEN"
    WOMEN = "WOMEN"


class MajorTournament(str, Enum):
    """Major tournament filter for tournament value queries.

    Attributes:
        YES: Major tournaments only
        NO: Non-major tournaments only
    """

    YES = "Y"
    NO = "N"


class RankingDivision(str, Enum):
    """Division filter for rankings queries.

    Used in rankings endpoints to filter by player division.

    Attributes:
        OPEN: Open division (all players)
        WOMEN: Women's division only

    Example:
        ```python
        from ifpa_api import RankingDivision

        # Get women's rankings for open tournaments
        rankings = client.rankings.women(
            tournament_type=RankingDivision.OPEN,
            count=50
        )
        ```
    """

    OPEN = "OPEN"
    WOMEN = "WOMEN"


class TournamentSearchType(str, Enum):
    """Tournament type filter for search queries.

    Used in tournament search to filter by tournament type/format.

    Attributes:
        OPEN: Open tournaments (all players)
        WOMEN: Women-only tournaments
        YOUTH: Youth tournaments
        LEAGUE: League-format tournaments

    Example:
        ```python
        from ifpa_api import TournamentSearchType

        # Search for women's tournaments
        results = (client.tournament.search("Championship")
            .tournament_type(TournamentSearchType.WOMEN)
            .get())
        ```
    """

    OPEN = "open"
    WOMEN = "women"
    YOUTH = "youth"
    LEAGUE = "league"


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
