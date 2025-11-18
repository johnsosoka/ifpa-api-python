"""Tests for enum validation and invalid enum handling.

This test suite validates that enum values are properly defined and can be used
throughout the SDK. The IFPA API SDK uses Python enums (Enum class) for type safety,
and these are validated at runtime when passed to API methods.

Run with: pytest tests/unit/test_enums.py -v
"""

import pytest

from ifpa_api.models.common import RankingSystem, ResultType, TimePeriod, TournamentType


class TestEnumDefinitions:
    """Test that enum definitions are complete and properly structured."""

    def test_ranking_system_enum_values(self) -> None:
        """Test that RankingSystem enum has expected values."""
        # Verify enum has expected values
        assert hasattr(RankingSystem, "MAIN")
        assert hasattr(RankingSystem, "WOMEN")
        assert hasattr(RankingSystem, "YOUTH")
        assert hasattr(RankingSystem, "VIRTUAL")
        assert hasattr(RankingSystem, "PRO")

        # Verify values are strings
        assert isinstance(RankingSystem.MAIN.value, str)
        assert isinstance(RankingSystem.WOMEN.value, str)
        assert isinstance(RankingSystem.YOUTH.value, str)
        assert isinstance(RankingSystem.VIRTUAL.value, str)
        assert isinstance(RankingSystem.PRO.value, str)

    def test_result_type_enum_values(self) -> None:
        """Test that ResultType enum has expected values."""
        assert hasattr(ResultType, "ACTIVE")
        assert hasattr(ResultType, "NONACTIVE")
        assert hasattr(ResultType, "INACTIVE")

        # Verify values are strings
        assert isinstance(ResultType.ACTIVE.value, str)
        assert isinstance(ResultType.NONACTIVE.value, str)
        assert isinstance(ResultType.INACTIVE.value, str)

    def test_time_period_enum_values(self) -> None:
        """Test that TimePeriod enum has expected values."""
        assert hasattr(TimePeriod, "PAST")
        assert hasattr(TimePeriod, "FUTURE")

        # Verify values are strings
        assert isinstance(TimePeriod.PAST.value, str)
        assert isinstance(TimePeriod.FUTURE.value, str)

    def test_tournament_type_enum_values(self) -> None:
        """Test that TournamentType enum has expected values."""
        assert hasattr(TournamentType, "OPEN")
        assert hasattr(TournamentType, "WOMEN")

        # Verify values are strings
        assert isinstance(TournamentType.OPEN.value, str)
        assert isinstance(TournamentType.WOMEN.value, str)


class TestEnumComparison:
    """Test that enum values can be compared properly."""

    def test_ranking_system_equality(self) -> None:
        """Test that RankingSystem enum values are equal to themselves."""
        assert RankingSystem.MAIN == RankingSystem.MAIN
        assert RankingSystem.WOMEN == RankingSystem.WOMEN
        # Test inequality
        main = RankingSystem.MAIN
        women = RankingSystem.WOMEN
        assert main != women

    def test_result_type_equality(self) -> None:
        """Test that ResultType enum values are equal to themselves."""
        assert ResultType.ACTIVE == ResultType.ACTIVE
        assert ResultType.NONACTIVE == ResultType.NONACTIVE
        # Test inequality
        active = ResultType.ACTIVE
        nonactive = ResultType.NONACTIVE
        assert active != nonactive

    def test_time_period_equality(self) -> None:
        """Test that TimePeriod enum values are equal to themselves."""
        assert TimePeriod.PAST == TimePeriod.PAST
        assert TimePeriod.FUTURE == TimePeriod.FUTURE
        # Test inequality
        past = TimePeriod.PAST
        future = TimePeriod.FUTURE
        assert past != future

    def test_tournament_type_equality(self) -> None:
        """Test that TournamentType enum values are equal to themselves."""
        assert TournamentType.OPEN == TournamentType.OPEN
        assert TournamentType.WOMEN == TournamentType.WOMEN
        # Test inequality
        open_type = TournamentType.OPEN
        women = TournamentType.WOMEN
        assert open_type != women


class TestEnumIteration:
    """Test that enums can be iterated for all valid values."""

    def test_ranking_system_iteration(self) -> None:
        """Test that all RankingSystem values can be iterated."""
        systems = list(RankingSystem)
        assert len(systems) == 5  # MAIN, WOMEN, YOUTH, VIRTUAL, PRO
        assert RankingSystem.MAIN in systems
        assert RankingSystem.WOMEN in systems
        assert RankingSystem.YOUTH in systems
        assert RankingSystem.VIRTUAL in systems
        assert RankingSystem.PRO in systems

    def test_result_type_iteration(self) -> None:
        """Test that all ResultType values can be iterated."""
        types = list(ResultType)
        assert len(types) == 3  # ACTIVE, NONACTIVE, INACTIVE
        assert ResultType.ACTIVE in types
        assert ResultType.NONACTIVE in types
        assert ResultType.INACTIVE in types

    def test_time_period_iteration(self) -> None:
        """Test that all TimePeriod values can be iterated."""
        periods = list(TimePeriod)
        assert len(periods) == 2  # PAST, FUTURE
        assert TimePeriod.PAST in periods
        assert TimePeriod.FUTURE in periods

    def test_tournament_type_iteration(self) -> None:
        """Test that all TournamentType values can be iterated."""
        types = list(TournamentType)
        assert len(types) == 2  # OPEN, WOMEN
        assert TournamentType.OPEN in types
        assert TournamentType.WOMEN in types


class TestEnumStringConversion:
    """Test that enum values convert to strings properly."""

    def test_ranking_system_to_string(self) -> None:
        """Test that RankingSystem enum values have proper string representations."""
        # Enum .value gives the actual string value
        assert isinstance(RankingSystem.MAIN.value, str)
        assert len(RankingSystem.MAIN.value) > 0

    def test_result_type_to_string(self) -> None:
        """Test that ResultType enum values have proper string representations."""
        assert isinstance(ResultType.ACTIVE.value, str)
        assert len(ResultType.ACTIVE.value) > 0

    def test_time_period_to_string(self) -> None:
        """Test that TimePeriod enum values have proper string representations."""
        assert isinstance(TimePeriod.PAST.value, str)
        assert len(TimePeriod.PAST.value) > 0

    def test_tournament_type_to_string(self) -> None:
        """Test that TournamentType enum values have proper string representations."""
        assert isinstance(TournamentType.WOMEN.value, str)
        assert len(TournamentType.WOMEN.value) > 0


class TestEnumValueValidation:
    """Test that enum values are properly validated in the SDK."""

    def test_invalid_enum_string_comparison(self) -> None:
        """Test that invalid string values don't match enum values."""
        # String comparison should fail - use runtime comparison to avoid mypy overlap warnings
        invalid_system: str = "INVALID_SYSTEM"
        invalid_result: str = "invalid"
        unknown_period: str = "unknown"

        assert invalid_system != RankingSystem.MAIN
        assert invalid_result != ResultType.ACTIVE
        assert unknown_period != TimePeriod.PAST

    def test_enum_membership_check(self) -> None:
        """Test that we can check if values are valid enum members."""
        # Test that we can check membership in enum
        assert RankingSystem.MAIN in RankingSystem
        assert ResultType.ACTIVE in ResultType
        assert TimePeriod.PAST in TimePeriod

    def test_invalid_enum_access_raises_error(self) -> None:
        """Test that accessing invalid enum members raises AttributeError."""
        with pytest.raises(AttributeError):
            _ = RankingSystem.INVALID_SYSTEM

        with pytest.raises(AttributeError):
            _ = ResultType.INVALID_TYPE

        with pytest.raises(AttributeError):
            _ = TimePeriod.INVALID_PERIOD
