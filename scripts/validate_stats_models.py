#!/usr/bin/env python3
"""Validate stats models against real API responses.

This script validates all stats Pydantic models by parsing real API
response files captured from the IFPA Stats API.
"""

import json
from pathlib import Path
from typing import Any

from ifpa_api.models.stats import (
    CountryPlayersResponse,
    EventsAttendedPeriodResponse,
    EventsByYearResponse,
    LargestTournamentsResponse,
    LucrativeTournamentsResponse,
    OverallStatsResponse,
    PlayersByYearResponse,
    PointsGivenPeriodResponse,
    StatePlayersResponse,
    StateTournamentsResponse,
)


def validate_model(model_class: type[Any], json_file: Path) -> bool:
    """Validate a model against a JSON response file.

    Args:
        model_class: The Pydantic model class to validate
        json_file: Path to the JSON response file

    Returns:
        True if validation succeeds, False otherwise
    """
    try:
        with open(json_file) as f:
            data = json.load(f)

        model = model_class.model_validate(data)

        # Additional validation: ensure we parsed some stats
        if hasattr(model, "stats"):
            if isinstance(model.stats, list):
                stats_count = len(model.stats)
            else:
                # Overall endpoint has single stats object
                stats_count = 1 if model.stats else 0

            print(f"✓ {model_class.__name__:40s} | {json_file.name:45s} | {stats_count:4d} records")
            return True
        print(f"✗ {model_class.__name__:40s} | {json_file.name:45s} | No stats field")
        return False

    except Exception as e:
        print(f"✗ {model_class.__name__:40s} | {json_file.name:45s} | {str(e)[:50]}")
        return False


def main() -> int:
    """Validate all stats models against saved API responses."""
    responses_dir = Path(__file__).parent / "stats_responses"

    print("Validating Stats Models Against Real API Responses")
    print("=" * 100)
    print(f"{'Model':<40} | {'File':<45} | {'Records':>10}")
    print("-" * 100)

    # Define test cases: (model_class, file_pattern)
    test_cases = [
        # Country players
        (CountryPlayersResponse, "country_players_open.json"),
        (CountryPlayersResponse, "country_players_women.json"),
        # State players
        (StatePlayersResponse, "state_players_open.json"),
        (StatePlayersResponse, "state_players_women.json"),
        # State tournaments
        (StateTournamentsResponse, "state_tournaments_open.json"),
        (StateTournamentsResponse, "state_tournaments_women.json"),
        # Events by year
        (EventsByYearResponse, "events_by_year_open.json"),
        (EventsByYearResponse, "events_by_year_women.json"),
        (EventsByYearResponse, "events_by_year_us.json"),
        # Players by year
        (PlayersByYearResponse, "players_by_year.json"),
        # Largest tournaments
        (LargestTournamentsResponse, "largest_tournaments_open.json"),
        (LargestTournamentsResponse, "largest_tournaments_women.json"),
        (LargestTournamentsResponse, "largest_tournaments_us.json"),
        # Lucrative tournaments
        (LucrativeTournamentsResponse, "lucrative_tournaments_major_open.json"),
        (LucrativeTournamentsResponse, "lucrative_tournaments_non_major.json"),
        (LucrativeTournamentsResponse, "lucrative_tournaments_women.json"),
        # Points given period
        (PointsGivenPeriodResponse, "points_given_period_default.json"),
        (PointsGivenPeriodResponse, "points_given_period_2024.json"),
        (PointsGivenPeriodResponse, "points_given_period_2024_limit10.json"),
        (PointsGivenPeriodResponse, "points_given_period_us_2024.json"),
        # Events attended period
        (EventsAttendedPeriodResponse, "events_attended_period_default.json"),
        (EventsAttendedPeriodResponse, "events_attended_period_2024.json"),
        (EventsAttendedPeriodResponse, "events_attended_period_2024_limit10.json"),
        (EventsAttendedPeriodResponse, "events_attended_period_us_2024.json"),
        # Overall stats
        (OverallStatsResponse, "overall_open.json"),
        (OverallStatsResponse, "overall_women.json"),
    ]

    passed = 0
    failed = 0

    for model_class, filename in test_cases:
        json_file = responses_dir / filename
        if validate_model(model_class, json_file):
            passed += 1
        else:
            failed += 1

    print("-" * 100)
    print(f"\nResults: {passed} passed, {failed} failed out of {passed + failed} tests")

    if failed > 0:
        print("\n⚠️  Some validations failed. Review errors above.")
        return 1
    print("\n✅ All validations passed!")
    return 0


if __name__ == "__main__":
    exit(main())
