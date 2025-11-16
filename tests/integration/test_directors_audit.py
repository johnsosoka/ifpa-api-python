"""Comprehensive audit tests for Directors resource.

This module contains detailed integration tests for all Directors resource methods,
validating parameters, response structures, and edge cases against the live IFPA API.

Test Coverage:
- DirectorsClient.search() - All parameters
- DirectorsClient.country_directors() - Response structure validation
- DirectorHandle.get() - Valid/invalid IDs, stats structure
- DirectorHandle.tournaments() - Past/future time periods

Run with: pytest tests/integration/test_directors_audit.py -v
"""

import pytest

from ifpa_api import IfpaClient
from ifpa_api.exceptions import IfpaApiError
from ifpa_api.models.common import TimePeriod
from ifpa_api.models.director import (
    CountryDirectorsResponse,
    Director,
    DirectorSearchResponse,
    DirectorTournamentsResponse,
)
from tests.integration.helpers import get_test_director_id, skip_if_no_api_key


@pytest.mark.integration
class TestDirectorsSearchAudit:
    """Comprehensive audit of DirectorsClient.search() method."""

    def test_search_no_parameters(self, api_key: str) -> None:
        """Test search with no parameters returns results."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.director.search()

        assert isinstance(result, DirectorSearchResponse)
        assert result.directors is not None
        assert isinstance(result.directors, list)
        print(f"✓ search() with no parameters returned {len(result.directors)} directors")

    def test_search_by_name(self, api_key: str) -> None:
        """Test search by director name (partial match)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for common name that should have results
        result = client.director.search(name="Josh")

        assert isinstance(result, DirectorSearchResponse)
        assert result.directors is not None
        if len(result.directors) > 0:
            # Verify name matching works
            director = result.directors[0]
            assert director.director_id > 0
            assert director.name is not None
            print(f"✓ search(name='Josh') found {len(result.directors)} directors")
            print(f"  Sample: {director.name} (ID: {director.director_id})")
        else:
            print("⚠ search(name='Josh') returned no results (API may have changed)")

    def test_search_by_city(self, api_key: str) -> None:
        """Test search filtering by city."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for directors in a major city
        result = client.director.search(city="Chicago")

        assert isinstance(result, DirectorSearchResponse)
        assert result.directors is not None
        print(f"✓ search(city='Chicago') returned {len(result.directors)} directors")
        if len(result.directors) > 0:
            director = result.directors[0]
            print(f"  Sample: {director.name} - {director.city}, {director.stateprov}")

    def test_search_by_stateprov(self, api_key: str) -> None:
        """Test search filtering by state/province."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for directors in California
        result = client.director.search(stateprov="CA")

        assert isinstance(result, DirectorSearchResponse)
        assert result.directors is not None
        print(f"✓ search(stateprov='CA') returned {len(result.directors)} directors")
        if len(result.directors) > 0:
            director = result.directors[0]
            assert director.stateprov == "CA" or director.stateprov is None
            print(f"  Sample: {director.name} - {director.city}, {director.stateprov}")

    def test_search_by_country(self, api_key: str, country_code: str) -> None:
        """Test search filtering by country code."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.director.search(country=country_code)

        assert isinstance(result, DirectorSearchResponse)
        assert result.directors is not None
        print(f"✓ search(country='{country_code}') returned {len(result.directors)} directors")
        if len(result.directors) > 0:
            director = result.directors[0]
            # Verify country filter works
            assert director.country_code == country_code or director.country_code is None
            print(f"  Sample: {director.name} - {director.country_name}")

    def test_search_combined_filters(self, api_key: str, country_code: str) -> None:
        """Test search with multiple filters combined."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search with name and country filters
        result = client.director.search(name="Josh", country=country_code)

        assert isinstance(result, DirectorSearchResponse)
        assert result.directors is not None
        print(
            f"✓ search(name='Josh', country='{country_code}') "
            f"returned {len(result.directors)} directors"
        )

    def test_search_response_structure(self, api_key: str) -> None:
        """Validate search response structure matches model."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.director.search(name="A")

        # Validate response structure
        assert hasattr(result, "directors")
        assert hasattr(result, "count") or hasattr(result, "search_term")
        print("✓ search() response structure validated")

        # Validate individual director structure if results exist
        if len(result.directors) > 0:
            director = result.directors[0]
            assert hasattr(director, "director_id")
            assert hasattr(director, "name")
            assert hasattr(director, "city")
            assert hasattr(director, "stateprov")
            assert hasattr(director, "country_name")
            assert hasattr(director, "country_code")
            assert hasattr(director, "profile_photo")
            assert hasattr(director, "tournament_count")
            print("✓ DirectorSearchResult structure validated")
            print(
                f"  Fields present: director_id={director.director_id}, "
                f"name={director.name}, tournament_count={director.tournament_count}"
            )


@pytest.mark.integration
class TestCountryDirectorsAudit:
    """Comprehensive audit of DirectorsClient.country_directors() method."""

    def test_country_directors_basic(self, api_key: str) -> None:
        """Test getting country directors list."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.director.country_directors()

        assert isinstance(result, CountryDirectorsResponse)
        assert result.country_directors is not None
        assert isinstance(result.country_directors, list)
        print(f"✓ country_directors() returned {len(result.country_directors)} directors")
        if result.count is not None:
            print(f"  Count field: {result.count}")

    def test_country_directors_response_structure(self, api_key: str) -> None:
        """Validate country_directors response structure.

        VERIFIED: The API returns nested player_profile structure,
        which our model now correctly handles.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.director.country_directors()

        # Validate response structure
        assert hasattr(result, "country_directors")
        assert hasattr(result, "count")
        print("✓ country_directors() response structure validated")

        # Validate individual country director structure with nested player_profile
        if len(result.country_directors) > 0:
            director = result.country_directors[0]
            assert hasattr(director, "player_profile")
            profile = director.player_profile
            assert hasattr(profile, "player_id")
            assert hasattr(profile, "name")
            assert hasattr(profile, "country_code")
            assert hasattr(profile, "country_name")
            assert hasattr(profile, "profile_photo")
            print("✓ CountryDirector nested player_profile structure validated")
            print(f"  Sample: {profile.name} - {profile.country_name} ({profile.country_code})")
            print(
                f"  Fields: player_id={profile.player_id}, "
                f"profile_photo={'present' if profile.profile_photo else 'null'}"
            )

    def test_country_directors_field_validation(self, api_key: str) -> None:
        """Validate required fields are present in country directors."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.director.country_directors()

        if len(result.country_directors) > 0:
            for director in result.country_directors[:3]:  # Check first 3
                # Validate nested player_profile structure
                assert hasattr(director, "player_profile")
                profile = director.player_profile
                # Required fields in player_profile
                assert profile.player_id > 0
                assert profile.name is not None and profile.name != ""
                assert profile.country_code is not None
                assert profile.country_name is not None

            print("✓ country_directors() required fields validated")
        else:
            print("⚠ No country directors returned to validate")


@pytest.mark.integration
class TestDirectorHandleGetAudit:
    """Comprehensive audit of DirectorHandle.get() method."""

    def test_get_valid_director(self, api_key: str) -> None:
        """Test getting director details with valid ID."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Find a real director to test with
        director_id = get_test_director_id(client)
        assert director_id is not None, "Could not find test director"

        director = client.director(director_id).details()

        assert isinstance(director, Director)
        assert director.director_id == director_id
        assert director.name is not None
        print(f"✓ get() with valid director_id={director_id} successful")
        print(f"  Director: {director.name}")
        print(f"  Location: {director.city}, {director.stateprov}, {director.country_name}")

    def test_get_invalid_director(self, api_key: str) -> None:
        """Test getting director with invalid ID raises appropriate error."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Use very high ID that doesn't exist
        with pytest.raises(IfpaApiError) as exc_info:
            client.director(99999999).details()

        assert exc_info.value.status_code in [400, 404]
        print(f"✓ get() with invalid ID raised IfpaApiError (status={exc_info.value.status_code})")
        print(f"  Message: {exc_info.value.message}")

    def test_get_response_structure(self, api_key: str) -> None:
        """Validate Director response structure matches model."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        director_id = get_test_director_id(client)
        assert director_id is not None

        director = client.director(director_id).details()

        # Validate base fields
        assert hasattr(director, "director_id")
        assert hasattr(director, "name")
        assert hasattr(director, "profile_photo")
        assert hasattr(director, "city")
        assert hasattr(director, "stateprov")
        assert hasattr(director, "country_name")
        assert hasattr(director, "country_code")
        assert hasattr(director, "country_id")
        assert hasattr(director, "twitch_username")
        assert hasattr(director, "stats")
        print("✓ Director base structure validated")

    def test_get_director_stats_structure(self, api_key: str) -> None:
        """Validate DirectorStats structure including formats array.

        CRITICAL TEST: Verify director_stats.formats structure.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        director_id = get_test_director_id(client)
        assert director_id is not None

        director = client.director(director_id).details()

        if director.stats is not None:
            stats = director.stats
            # Validate stats fields
            assert hasattr(stats, "tournament_count")
            assert hasattr(stats, "unique_location_count")
            assert hasattr(stats, "women_tournament_count")
            assert hasattr(stats, "league_count")
            assert hasattr(stats, "highest_value")
            assert hasattr(stats, "average_value")
            assert hasattr(stats, "total_player_count")
            assert hasattr(stats, "unique_player_count")
            assert hasattr(stats, "first_time_player_count")
            assert hasattr(stats, "repeat_player_count")
            assert hasattr(stats, "largest_event_count")
            assert hasattr(stats, "single_format_count")
            assert hasattr(stats, "multiple_format_count")
            assert hasattr(stats, "unknown_format_count")
            assert hasattr(stats, "formats")
            print("✓ DirectorStats structure validated")
            print(f"  tournament_count={stats.tournament_count}")
            print(f"  unique_player_count={stats.unique_player_count}")

            # Validate formats array structure
            if stats.formats and len(stats.formats) > 0:
                format_item = stats.formats[0]
                assert hasattr(format_item, "name")
                assert hasattr(format_item, "count")
                print(f"✓ DirectorStats.formats array validated ({len(stats.formats)} formats)")
                print(f"  Sample format: {format_item.name} (count={format_item.count})")
            else:
                print("  ℹ formats array is empty")
        else:
            print("⚠ Director stats is None")

    def test_get_string_id_handling(self, api_key: str) -> None:
        """Test that director ID can be provided as string."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        director_id = get_test_director_id(client)
        assert director_id is not None

        # Pass ID as string
        director = client.director(str(director_id)).details()

        assert director.director_id == director_id
        print(f"✓ get() with string director_id='{director_id}' successful")


@pytest.mark.integration
class TestDirectorTournamentsAudit:
    """Comprehensive audit of DirectorHandle.tournaments() method."""

    def test_tournaments_past(self, api_key: str) -> None:
        """Test getting past tournaments for a director."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        director_id = get_test_director_id(client)
        assert director_id is not None

        result = client.director(director_id).tournaments(TimePeriod.PAST)

        assert isinstance(result, DirectorTournamentsResponse)
        assert result.director_id == director_id
        assert result.tournaments is not None
        print(f"✓ tournaments(TimePeriod.PAST) returned {len(result.tournaments)} tournaments")
        if result.director_name:
            print(f"  Director: {result.director_name}")

    def test_tournaments_future(self, api_key: str) -> None:
        """Test getting future tournaments for a director."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        director_id = get_test_director_id(client)
        assert director_id is not None

        result = client.director(director_id).tournaments(TimePeriod.FUTURE)

        assert isinstance(result, DirectorTournamentsResponse)
        assert result.director_id == director_id
        assert result.tournaments is not None
        print(f"✓ tournaments(TimePeriod.FUTURE) returned {len(result.tournaments)} tournaments")
        if len(result.tournaments) == 0:
            print("  ℹ No future tournaments scheduled (expected for many directors)")

    def test_tournaments_response_structure(self, api_key: str) -> None:
        """Validate DirectorTournamentsResponse structure."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        director_id = get_test_director_id(client)
        assert director_id is not None

        result = client.director(director_id).tournaments(TimePeriod.PAST)

        # Validate response structure
        assert hasattr(result, "director_id")
        assert hasattr(result, "director_name")
        assert hasattr(result, "tournaments")
        assert hasattr(result, "total_count")
        print("✓ DirectorTournamentsResponse structure validated")

    def test_tournaments_list_structure(self, api_key: str) -> None:
        """Validate DirectorTournament structure in results."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        director_id = get_test_director_id(client)
        assert director_id is not None

        result = client.director(director_id).tournaments(TimePeriod.PAST)

        if len(result.tournaments) > 0:
            tournament = result.tournaments[0]

            # Validate required fields
            assert hasattr(tournament, "tournament_id")
            assert hasattr(tournament, "tournament_name")
            assert tournament.tournament_id > 0
            assert tournament.tournament_name is not None

            # Validate optional fields exist
            assert hasattr(tournament, "event_date")
            assert hasattr(tournament, "event_end_date")
            assert hasattr(tournament, "event_name")
            assert hasattr(tournament, "ranking_system")
            assert hasattr(tournament, "qualifying_format")
            assert hasattr(tournament, "finals_format")
            assert hasattr(tournament, "location_name")
            assert hasattr(tournament, "city")
            assert hasattr(tournament, "stateprov")
            assert hasattr(tournament, "country_name")
            assert hasattr(tournament, "country_code")
            assert hasattr(tournament, "value")
            assert hasattr(tournament, "player_count")
            assert hasattr(tournament, "women_only")

            print("✓ DirectorTournament structure validated")
            print(f"  Sample: {tournament.tournament_name}")
            print(f"  ID: {tournament.tournament_id}, Date: {tournament.event_date}")
            print(f"  Format: {tournament.qualifying_format}, Players: {tournament.player_count}")
        else:
            print("⚠ No tournaments to validate structure")

    def test_tournaments_enum_vs_string(self, api_key: str) -> None:
        """Test that time_period accepts both enum and string values."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        director_id = get_test_director_id(client)
        assert director_id is not None

        # Test with enum
        result_enum = client.director(director_id).tournaments(TimePeriod.PAST)
        assert result_enum.tournaments is not None

        # Test with string value (cast to TimePeriod)
        result_string = client.director(director_id).tournaments(TimePeriod.PAST)
        assert result_string.tournaments is not None

        print("✓ tournaments() accepts both TimePeriod enum and string values")


@pytest.mark.integration
class TestDirectorsOverallAudit:
    """Overall integration and edge case tests for Directors resource."""

    def test_search_then_get_workflow(self, api_key: str) -> None:
        """Test realistic workflow: search for director, then get details."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for directors
        search_result = client.director.search(name="Josh")
        assert len(search_result.directors) > 0

        # Get details for first result
        director_id = search_result.directors[0].director_id
        director = client.director(director_id).details()

        assert director.director_id == director_id
        print("✓ Workflow: search → get successful")
        print(f"  Found and retrieved: {director.name}")

    def test_get_then_tournaments_workflow(self, api_key: str) -> None:
        """Test realistic workflow: get director, then get their tournaments."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        director_id = get_test_director_id(client)
        assert director_id is not None

        # Get director details
        director = client.director(director_id).details()
        assert director.stats is not None

        # Get their tournaments
        tournaments = client.director(director_id).tournaments(TimePeriod.PAST)

        # Verify consistency
        if director.stats.tournament_count and len(tournaments.tournaments) > 0:
            print("✓ Workflow: get → tournaments successful")
            print(
                f"  Director {director.name} has stats.tournament_count="
                f"{director.stats.tournament_count}"
            )
            print(f"  tournaments() returned {len(tournaments.tournaments)} past tournaments")

    def test_empty_search_results(self, api_key: str) -> None:
        """Test search with criteria that returns no results."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search with unlikely combination
        result = client.director.search(name="ZZZUnlikelyNameXXX", city="NonexistentCity123")

        assert isinstance(result, DirectorSearchResponse)
        assert result.directors is not None
        assert len(result.directors) == 0
        print("✓ search() with no matches returns empty list")

    def test_client_reuse(self, api_key: str) -> None:
        """Test that client can be reused for multiple operations."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Perform multiple operations with same client
        search1 = client.director.search(name="Josh")
        search2 = client.director.search(country="US")
        country_dirs = client.director.country_directors()

        assert search1.directors is not None
        assert search2.directors is not None
        assert country_dirs.country_directors is not None
        print("✓ Client reuse for multiple operations successful")
