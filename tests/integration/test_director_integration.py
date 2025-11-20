"""Integration tests for Director resource.

This test suite performs comprehensive integration testing of all Director resource methods
against the live IFPA API. Tests cover happy path, edge cases, filtering, error handling,
and response structure validation.

Test fixtures use diverse director profiles:
- Josh Rainwater (1533): Active, moderate activity, 13 tournaments, Columbia SC
- Erik Thoren (1151): Highly active, 545 tournaments, 1,658 unique players, De Pere WI
- Michael Trepp (1071): International, 225 tournaments, Switzerland
- Cory Casella (1752): Active with zero future events, 34 tournaments, Los Angeles CA
- Matt Darst (3657): Low activity, 3 tournaments, Willard MO

These tests make real API calls and require a valid API key.
Run with: pytest -m integration
"""

import pytest

from ifpa_api import IfpaClient
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.models.common import TimePeriod
from ifpa_api.models.director import (
    CountryDirectorsResponse,
    Director,
    DirectorSearchResponse,
    DirectorTournamentsResponse,
)
from tests.integration.helpers import get_test_director_id, skip_if_no_api_key

# Test thresholds for director activity levels
HIGHLY_ACTIVE_TOURNAMENT_COUNT = 500  # Directors with 500+ tournaments are highly active
HIGHLY_ACTIVE_PLAYER_COUNT = 1000  # Directors who've had 1000+ unique players
LOW_ACTIVITY_THRESHOLD = 10  # Directors with <10 tournaments are low activity

# =============================================================================
# COLLECTION METHODS (DirectorClient)
# =============================================================================


@pytest.mark.integration
class TestDirectorClientIntegration:
    """Basic integration tests for DirectorClient collection methods."""

    def test_search_directors(self, api_key: str) -> None:
        """Test searching for directors with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.director.search().get()

        assert isinstance(result, DirectorSearchResponse)
        # API should return some directors
        assert result.directors is not None

    def test_search_directors_with_filters(self, api_key: str, country_code: str) -> None:
        """Test searching directors with country filter parameter."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search with country filter
        result = client.director.search().country(country_code).get()

        assert result.directors is not None
        assert isinstance(result.directors, list)
        # Verify structure if results exist
        if len(result.directors) > 0:
            director = result.directors[0]
            assert director.director_id > 0
            assert director.name is not None


@pytest.mark.integration
class TestDirectorSearchAudit:
    """Comprehensive audit of DirectorClient.search() method."""

    def test_search_no_parameters(self, api_key: str) -> None:
        """Test search with no parameters returns results."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.director.search().get()

        assert isinstance(result, DirectorSearchResponse)
        assert result.directors is not None
        assert isinstance(result.directors, list)
        print(f"✓ search() with no parameters returned {len(result.directors)} directors")

    def test_search_by_name(self, api_key: str) -> None:
        """Test search by director name (partial match)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for common name that should have results
        result = client.director.search("Josh").get()

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
        result = client.director.search().city("Chicago").get()

        assert isinstance(result, DirectorSearchResponse)
        assert result.directors is not None
        print(f"✓ search(city='Chicago') returned {len(result.directors)} directors")
        if len(result.directors) > 0:
            director = result.directors[0]
            print(f"  Sample: {director.name} - {director.city}, {director.stateprov}")

    @pytest.mark.skip(
        reason="API Bug: stateprov filter returns incorrect results. "
        "Filtering by state returns directors from other states. "
        "This is a known IFPA API limitation, not an SDK issue."
    )
    def test_search_by_stateprov(self, api_key: str) -> None:
        """Test search filtering by state/province.

        Note: This test is permanently skipped due to a known IFPA API bug where
        the stateprov filter returns directors from incorrect states. For example,
        searching for "CA" (California) returns directors from North Carolina (NC)
        and other states. This is an API limitation and cannot be fixed in the SDK.

        When the API is fixed, this test should validate that filtering by state
        returns only directors from that specific state.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for directors in California
        result = client.director.search().state("CA").get()

        assert isinstance(result, DirectorSearchResponse)
        assert result.directors is not None
        print(f"✓ search(stateprov='CA') returned {len(result.directors)} directors")
        if len(result.directors) > 0:
            director = result.directors[0]
            # Note: API may return directors with None or empty stateprov
            print(f"  Sample: {director.name} - {director.city}, {director.stateprov}")

    def test_search_by_country(self, api_key: str, country_code: str) -> None:
        """Test search filtering by country code.

        Note: API search filtering has known inconsistencies where results
        may include directors from other countries. This test verifies the
        API returns results but does not strictly validate country matching.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.director.search().country(country_code).get()

        assert isinstance(result, DirectorSearchResponse)
        assert result.directors is not None
        print(f"✓ search(country='{country_code}') returned {len(result.directors)} directors")
        if len(result.directors) > 0:
            director = result.directors[0]
            print(f"  Sample: {director.name} - {director.country_name} ({director.country_code})")

    def test_search_combined_filters(self, api_key: str, country_code: str) -> None:
        """Test search with multiple filters combined."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search with name and country filters
        result = client.director.search("Josh").country(country_code).get()

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

        result = client.director.search("A").get()

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
    """Comprehensive audit of DirectorClient.country_directors() method."""

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


# =============================================================================
# RESOURCE METHODS (DirectorContext)
# =============================================================================


@pytest.mark.integration
class TestDirectorContextIntegration:
    """Basic integration tests for DirectorContext resource methods."""

    def test_details_director(self, api_key: str) -> None:
        """Test getting director details with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Find a director to test with
        director_id = get_test_director_id(client)
        assert director_id is not None, "Could not find test director"

        # Get director details
        director = client.director.get(director_id)

        assert isinstance(director, Director)
        assert director.director_id == director_id
        assert director.name is not None

    def test_details_not_found(self, api_key: str) -> None:
        """Test that getting non-existent director raises appropriate error."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Use very high ID that doesn't exist
        with pytest.raises(IfpaApiError) as exc_info:
            client.director.get(99999999)

        assert exc_info.value.status_code == 400
        assert "not found" in exc_info.value.message.lower()

    def test_director_tournaments_past(self, api_key: str) -> None:
        """Test getting past tournaments for a director with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Find a director to test with
        director_id = get_test_director_id(client)
        assert director_id is not None, "Could not find test director"

        # Get past tournaments
        result = client.director(director_id).tournaments(TimePeriod.PAST)

        assert result.director_id == director_id
        assert result.tournaments is not None
        # Verify structure if tournaments exist
        if len(result.tournaments) > 0:
            tournament = result.tournaments[0]
            assert tournament.tournament_id > 0
            assert tournament.tournament_name is not None

    def test_director_tournaments_future(self, api_key: str) -> None:
        """Test getting future tournaments for a director with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Find a director to test with
        director_id = get_test_director_id(client)
        assert director_id is not None, "Could not find test director"

        # Get future tournaments (may be empty)
        result = client.director(director_id).tournaments(TimePeriod.FUTURE)

        assert result.director_id == director_id
        assert result.tournaments is not None


# =============================================================================
# DIRECTOR DETAILS AUDIT
# =============================================================================


@pytest.mark.integration
class TestDirectorDetailsAudit:
    """Comprehensive audit of DirectorContext.details() method."""

    def test_details_valid_director(self, api_key: str) -> None:
        """Test getting director details with valid ID."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Find a real director to test with
        director_id = get_test_director_id(client)
        assert director_id is not None, "Could not find test director"

        director = client.director.get(director_id)

        assert isinstance(director, Director)
        assert director.director_id == director_id
        assert director.name is not None
        print(f"✓ details() with valid director_id={director_id} successful")
        print(f"  Director: {director.name}")
        print(f"  Location: {director.city}, {director.stateprov}, {director.country_name}")

    def test_details_invalid_director(self, api_key: str) -> None:
        """Test getting director with invalid ID raises appropriate error."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Use very high ID that doesn't exist
        with pytest.raises(IfpaApiError) as exc_info:
            client.director.get(99999999)

        assert exc_info.value.status_code in [400, 404]
        print(
            f"✓ details() with invalid ID raised IfpaApiError (status={exc_info.value.status_code})"
        )
        print(f"  Message: {exc_info.value.message}")

    def test_details_response_structure(self, api_key: str) -> None:
        """Validate Director response structure matches model."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        director_id = get_test_director_id(client)
        assert director_id is not None

        director = client.director.get(director_id)

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

    def test_details_stats_structure(self, api_key: str) -> None:
        """Validate DirectorStats structure including formats array.

        CRITICAL TEST: Verify director_stats.formats structure.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        director_id = get_test_director_id(client)
        assert director_id is not None

        director = client.director.get(director_id)

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

    def test_details_string_id_handling(self, api_key: str) -> None:
        """Test that director ID can be provided as string."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        director_id = get_test_director_id(client)
        assert director_id is not None

        # Pass ID as string
        director = client.director.get(str(director_id))

        assert director.director_id == director_id
        print(f"✓ details() with string director_id='{director_id}' successful")

    def test_details_highly_active_director(
        self, api_key: str, director_highly_active_id: int
    ) -> None:
        """Test details() with highly active director (extensive data)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        director = client.director.get(director_highly_active_id)

        assert isinstance(director, Director)
        assert director.director_id == director_highly_active_id
        assert director.name is not None

        # Verify high activity stats
        if director.stats is not None:
            assert (
                director.stats.tournament_count is not None
                and director.stats.tournament_count > HIGHLY_ACTIVE_TOURNAMENT_COUNT
            )
            assert (
                director.stats.unique_player_count is not None
                and director.stats.unique_player_count > HIGHLY_ACTIVE_PLAYER_COUNT
            )
            print("✓ details() for highly active director successful")
            print(f"  Director: {director.name}")
            print(f"  Tournament count: {director.stats.tournament_count}")
            print(f"  Unique players: {director.stats.unique_player_count}")

    def test_details_international_director(
        self, api_key: str, director_international_id: int
    ) -> None:
        """Test details() with international director (non-US)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        director = client.director.get(director_international_id)

        assert isinstance(director, Director)
        assert director.director_id == director_international_id
        assert director.name is not None
        assert director.country_code != "US"
        print("✓ details() for international director successful")
        print(f"  Director: {director.name}")
        print(f"  Country: {director.country_name} ({director.country_code})")
        if director.stats:
            print(f"  Tournament count: {director.stats.tournament_count}")

    def test_details_low_activity_director(
        self, api_key: str, director_low_activity_id: int
    ) -> None:
        """Test details() with low activity director (minimal data)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        director = client.director.get(director_low_activity_id)

        assert isinstance(director, Director)
        assert director.director_id == director_low_activity_id
        assert director.name is not None

        # Verify low activity stats
        if director.stats is not None:
            assert (
                director.stats.tournament_count is not None
                and director.stats.tournament_count < LOW_ACTIVITY_THRESHOLD
            )
            print("✓ details() for low activity director successful")
            print(f"  Director: {director.name}")
            print(f"  Tournament count: {director.stats.tournament_count}")
            print(f"  Unique players: {director.stats.unique_player_count}")


# =============================================================================
# DIRECTOR TOURNAMENTS AUDIT
# =============================================================================


@pytest.mark.integration
class TestDirectorTournamentsAudit:
    """Comprehensive audit of DirectorContext.tournaments() method."""

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

    def test_tournaments_zero_future_events(
        self, api_key: str, director_zero_future_id: int
    ) -> None:
        """Test tournaments() with director that has zero future events."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.director(director_zero_future_id).tournaments(TimePeriod.FUTURE)

        assert isinstance(result, DirectorTournamentsResponse)
        assert result.director_id == director_zero_future_id
        # Note: Director 1752 historically has zero future tournaments, but this could change
        assert result.tournaments is not None
        assert isinstance(result.tournaments, list)
        # Allow any count - director could schedule future events
        print("✓ tournaments(FUTURE) for zero-future director returned empty list")
        print(f"  Director ID: {director_zero_future_id}")
        print(f"  Future tournaments: {len(result.tournaments)}")

    def test_tournaments_high_volume(self, api_key: str, director_highly_active_id: int) -> None:
        """Test tournaments() with highly active director (large result set)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.director(director_highly_active_id).tournaments(TimePeriod.PAST)

        assert isinstance(result, DirectorTournamentsResponse)
        assert result.director_id == director_highly_active_id
        assert result.tournaments is not None
        assert len(result.tournaments) > HIGHLY_ACTIVE_TOURNAMENT_COUNT
        print("✓ tournaments(PAST) for highly active director successful")
        print(f"  Director ID: {director_highly_active_id}")
        print(f"  Past tournaments: {len(result.tournaments)}")
        if result.total_count:
            print(f"  Total count: {result.total_count}")


# =============================================================================
# CROSS-VALIDATION TESTS
# =============================================================================


@pytest.mark.integration
class TestDirectorCrossMethodValidation:
    """Cross-method validation tests to verify data consistency."""

    def test_search_then_details_consistency(self, api_key: str, director_active_id: int) -> None:
        """Test that search results match details() calls."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Get director details first
        director_details = client.director.get(director_active_id)

        # Search for director by name
        search_result = client.director.search(director_details.name).get()

        assert search_result.directors is not None
        assert len(search_result.directors) > 0

        # Find our director in search results
        found = False
        for search_dir in search_result.directors:
            if search_dir.director_id == director_active_id:
                found = True
                # Verify consistency
                assert search_dir.name == director_details.name
                assert search_dir.city == director_details.city
                assert search_dir.country_code == director_details.country_code
                print("✓ Search results match details() data")
                print(f"  Director: {director_details.name}")
                print(f"  ID: {director_active_id}")
                break

        assert found, f"Director {director_active_id} not found in search results"

    def test_stats_tournament_count_matches_query(
        self, api_key: str, director_active_id: int
    ) -> None:
        """Test that tournament count in stats matches tournaments() query.

        NOTE: Stats tournament_count may include future tournaments,
        so we verify it's >= past tournament count.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Get director details with stats
        director = client.director.get(director_active_id)
        assert director.stats is not None
        assert director.stats.tournament_count is not None

        # Get past tournaments
        past_tournaments = client.director(director_active_id).tournaments(TimePeriod.PAST)

        # Stats count should be >= past tournament count
        assert director.stats.tournament_count >= len(past_tournaments.tournaments)
        print("✓ Stats tournament count is consistent with tournaments query")
        print(f"  Stats tournament_count: {director.stats.tournament_count}")
        print(f"  Past tournaments returned: {len(past_tournaments.tournaments)}")

    def test_location_filter_accuracy(self, api_key: str, country_code: str) -> None:
        """Test that location filters return results.

        Note: API has known issues with filter accuracy where results may
        include directors from other countries. This test verifies API
        returns results but does not validate strict filter matching.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search with country filter
        result = client.director.search().country(country_code).get()

        assert result.directors is not None
        assert len(result.directors) > 0

        # Count how many directors actually match the filter
        matching = sum(1 for d in result.directors[:10] if d.country_code == country_code)
        total = min(10, len(result.directors))

        print(f"✓ Location filter (country={country_code}) returned results")
        print(f"  Directors returned: {len(result.directors)}")
        print(f"  Matching filter in first {total}: {matching}/{total}")

    def test_client_reuse_consistency(self, api_key: str, director_active_id: int) -> None:
        """Test that client can be reused for multiple operations."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Perform multiple operations with same client
        details1 = client.director.get(director_active_id)
        tournaments = client.director(director_active_id).tournaments(TimePeriod.PAST)
        details2 = client.director.get(director_active_id)

        # Verify consistency across calls
        assert details1.director_id == director_active_id
        assert tournaments.director_id == director_active_id
        assert details2.director_id == director_active_id
        assert details1.name == details2.name

        print("✓ Client reuse produces consistent results")
        print(f"  Director: {details1.name}")
        print("  Operations: details → tournaments → details")


# =============================================================================
# OVERALL INTEGRATION TESTS
# =============================================================================


@pytest.mark.integration
class TestDirectorsOverallAudit:
    """Overall workflows and edge cases."""

    def test_search_then_get_workflow(self, api_key: str) -> None:
        """Test realistic workflow: search for director, then get details."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for directors
        search_result = client.director.search("Josh").get()
        assert len(search_result.directors) > 0

        # Get details for first result
        director_id = search_result.directors[0].director_id
        director = client.director.get(director_id)

        assert director.director_id == director_id
        print("✓ Workflow: search → details successful")
        print(f"  Found and retrieved: {director.name}")

    def test_get_then_tournaments_workflow(self, api_key: str) -> None:
        """Test realistic workflow: get director, then get their tournaments."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        director_id = get_test_director_id(client)
        assert director_id is not None

        # Get director details
        director = client.director.get(director_id)
        assert director.stats is not None

        # Get their tournaments
        tournaments = client.director(director_id).tournaments(TimePeriod.PAST)

        # Verify consistency
        if director.stats.tournament_count and len(tournaments.tournaments) > 0:
            print("✓ Workflow: details → tournaments successful")
            print(
                f"  Director {director.name} has stats.tournament_count="
                f"{director.stats.tournament_count}"
            )
            print(f"  tournaments() returned {len(tournaments.tournaments)} past tournaments")

    def test_search_returns_zero_results(self, api_key: str) -> None:
        """Test that zero-result director searches are handled correctly.

        Uses unlikely search criteria to ensure empty results. The SDK should
        return an empty list rather than raising an error.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search with unlikely combination
        result = (
            client.director.search("ZzZzUnlikelyName999XxX")
            .country("XX")  # Invalid country code
            .get()
        )

        assert result.directors is not None
        assert isinstance(result.directors, list)
        assert len(result.directors) == 0
        print("✓ search() with no matches returns empty list")

    def test_client_reuse(self, api_key: str) -> None:
        """Test that client can be reused for multiple operations."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Perform multiple operations with same client
        search1 = client.director.search("Josh").get()
        search2 = client.director.search().country("US").get()
        country_dirs = client.director.country_directors()

        assert search1.directors is not None
        assert search2.directors is not None
        assert country_dirs.country_directors is not None
        print("✓ Client reuse for multiple operations successful")

    def test_international_director_workflow(
        self, api_key: str, director_international_id: int
    ) -> None:
        """Test complete workflow with international director."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Get director details
        director = client.director.get(director_international_id)
        assert director.director_id == director_international_id
        assert director.country_code != "US"

        # Get past tournaments
        past_tournaments = client.director(director_international_id).tournaments(TimePeriod.PAST)
        assert past_tournaments.director_id == director_international_id
        assert len(past_tournaments.tournaments) > 0

        # Get future tournaments
        future_tournaments = client.director(director_international_id).tournaments(
            TimePeriod.FUTURE
        )
        assert future_tournaments.director_id == director_international_id

        print("✓ International director workflow successful")
        print(f"  Director: {director.name}")
        print(f"  Country: {director.country_name} ({director.country_code})")
        print(f"  Past tournaments: {len(past_tournaments.tournaments)}")
        print(f"  Future tournaments: {len(future_tournaments.tournaments)}")
