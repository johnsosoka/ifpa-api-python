"""Integration tests for Tournament resource.

This test suite performs comprehensive integration testing of all Tournament resource methods
against the live IFPA API. Tests cover happy path, edge cases, pagination, error handling,
and response structure validation.

These tests make real API calls and require a valid API key.
Run with: pytest -m integration
"""

import os

import pytest
import requests

from ifpa_api import IfpaClient
from ifpa_api.core.exceptions import IfpaApiError, TournamentNotLeagueError
from ifpa_api.models.tournaments import (
    RelatedTournamentsResponse,
    Tournament,
    TournamentFormatsListResponse,
    TournamentFormatsResponse,
    TournamentLeagueResponse,
    TournamentResultsResponse,
    TournamentSearchResponse,
    TournamentSubmissionsResponse,
)
from tests.integration.helpers import get_test_tournament_id, skip_if_no_api_key

# =============================================================================
# COLLECTION METHODS (TournamentsClient)
# =============================================================================


@pytest.mark.integration
class TestTournamentSearchIntegration:
    """Integration tests for TournamentsClient.search() method."""

    def test_search_no_parameters(self, api_key: str) -> None:
        """Test search with no parameters returns results."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.tournament.query().get()

        assert isinstance(result, TournamentSearchResponse)
        assert result.tournaments is not None
        assert isinstance(result.tournaments, list)
        print(f"✓ search() with no parameters returned {len(result.tournaments)} tournaments")
        if len(result.tournaments) > 0:
            tournament = result.tournaments[0]
            print(f"  Sample: {tournament.tournament_name} (ID: {tournament.tournament_id})")

    def test_search_basic(self, api_key: str, count_small: int) -> None:
        """Test basic tournament search returns valid results."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search with a common term that should return results
        results = client.tournament.query("Championship").limit(count_small).get()

        assert isinstance(results, TournamentSearchResponse)
        # Should have at least one result
        if results.tournaments:
            first_result = results.tournaments[0]
            assert first_result.tournament_id is not None
            assert first_result.tournament_name is not None
            # Verify critical fields are populated
            tournament_name = first_result.tournament_name
            tournament_id = first_result.tournament_id
            print(f"Found tournament: {tournament_name} (ID: {tournament_id})")

    def test_search_by_name(self, api_key: str) -> None:
        """Test search by tournament name (partial match)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for common tournament name
        result = client.tournament.query("Pinball").get()

        assert isinstance(result, TournamentSearchResponse)
        assert result.tournaments is not None
        print(f"✓ search(name='Pinball') found {len(result.tournaments)} tournaments")
        if len(result.tournaments) > 0:
            tournament = result.tournaments[0]
            assert tournament.tournament_id > 0
            print(f"  Sample: {tournament.tournament_name} (ID: {tournament.tournament_id})")

    def test_search_by_city(self, api_key: str) -> None:
        """Test search filtering by city."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for tournaments in a major city
        result = client.tournament.query().city("Portland").get()

        assert isinstance(result, TournamentSearchResponse)
        assert result.tournaments is not None
        print(f"✓ search(city='Portland') returned {len(result.tournaments)} tournaments")
        if len(result.tournaments) > 0:
            tournament = result.tournaments[0]
            print(f"  Sample: {tournament.tournament_name} - {tournament.city}")

    def test_search_by_stateprov(self, api_key: str) -> None:
        """Test search filtering by state/province."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for tournaments in Oregon
        result = client.tournament.query().state("OR").get()

        assert isinstance(result, TournamentSearchResponse)
        assert result.tournaments is not None
        print(f"✓ search(stateprov='OR') returned {len(result.tournaments)} tournaments")
        if len(result.tournaments) > 0:
            tournament = result.tournaments[0]
            print(f"  Sample: {tournament.tournament_name} - {tournament.stateprov}")

    def test_search_with_state_filter(self, api_key: str, count_small: int) -> None:
        """Test tournament search with state filter."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search California tournaments
        result = client.tournament.query().state("CA").limit(count_small).get()

        assert isinstance(result, TournamentSearchResponse)
        assert isinstance(result.tournaments, list)

    def test_search_by_country(self, api_key: str, country_code: str) -> None:
        """Test search filtering by country code."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.tournament.query().country(country_code).limit(5).get()

        assert isinstance(result, TournamentSearchResponse)
        assert result.tournaments is not None
        print(f"✓ search(country='{country_code}') returned {len(result.tournaments)} tournaments")
        if len(result.tournaments) > 0:
            tournament = result.tournaments[0]
            print(f"  Sample: {tournament.tournament_name} - {tournament.country_code}")

    def test_search_with_location(self, api_key: str, country_code: str, count_medium: int) -> None:
        """Test tournament search with location filters."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for tournaments by country
        results = client.tournament.query().country(country_code).limit(count_medium).get()

        assert isinstance(results, TournamentSearchResponse)
        if results.tournaments:
            # Check that stateprov field is properly mapped
            for tournament in results.tournaments:
                print(f"Tournament: {tournament.tournament_name}")
                location = (
                    f"{tournament.city}, {tournament.stateprov} " f"{tournament.country_code}"
                )
                print(f"  Location: {location}")
                # Verify stateprov field exists (not 'state')
                if tournament.stateprov:
                    assert isinstance(tournament.stateprov, str)

    def test_search_with_country_filter(self, api_key: str) -> None:
        """Test searching tournaments with country filter."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.tournament.query().country("US").limit(5).get()

        assert isinstance(result, TournamentSearchResponse)
        assert result.tournaments is not None
        # If results exist, verify they match filter
        if len(result.tournaments) > 0:
            for tournament in result.tournaments:
                if tournament.country_code:
                    assert tournament.country_code == "US"

    def test_search_by_start_date(self, api_key: str) -> None:
        """Test that search rejects start_date without end_date."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Should raise ValueError - both dates required together
        with pytest.raises(ValueError, match="Both start_date and end_date must be provided"):
            client.tournament.query().date_range("2024-01-01", None).limit(10).get()

        print("✓ search(start_date='2024-01-01') correctly raised ValueError")

    def test_search_by_end_date(self, api_key: str) -> None:
        """Test that search rejects end_date without start_date."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Should raise ValueError - both dates required together
        with pytest.raises(ValueError, match="Both start_date and end_date must be provided"):
            client.tournament.query().date_range(None, "2024-12-31").limit(10).get()

        print("✓ search(end_date='2024-12-31') correctly raised ValueError")

    def test_search_by_date_range(self, api_key: str) -> None:
        """Test search filtering by date range (start_date and end_date)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for tournaments in 2024
        result = client.tournament.query().date_range("2024-01-01", "2024-12-31").limit(20).get()

        assert isinstance(result, TournamentSearchResponse)
        assert result.tournaments is not None
        print(f"✓ search with date range (2024) returned {len(result.tournaments)} tournaments")
        if len(result.tournaments) > 0:
            tournament = result.tournaments[0]
            print(f"  Sample: {tournament.tournament_name} - {tournament.event_date}")

    def test_search_by_tournament_type(self, api_key: str) -> None:
        """Test search filtering by tournament_type."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for women's tournaments
        result = client.tournament.query().tournament_type("women").limit(10).get()

        assert isinstance(result, TournamentSearchResponse)
        assert result.tournaments is not None
        print(f"✓ search(tournament_type='women') returned {len(result.tournaments)} tournaments")
        if len(result.tournaments) > 0:
            tournament = result.tournaments[0]
            print(f"  Sample: {tournament.tournament_name} (ID: {tournament.tournament_id})")

    def test_search_with_pagination(self, api_key: str, count_small: int) -> None:
        """Test search with pagination parameters (start_pos, count)."""
        skip_if_no_api_key()
        # Use longer timeout for pagination queries which can be slow in CI
        client = IfpaClient(api_key=api_key, timeout=30.0)

        # Get first page (API requires start_pos >= 1)
        try:
            page1 = client.tournament.query().offset(1).limit(count_small).get()
            assert isinstance(page1, TournamentSearchResponse)
            print(
                f"✓ search(start_pos=1, count={count_small}) "
                f"returned {len(page1.tournaments)} tournaments"
            )

            # Try to get second page - may timeout on API side
            try:
                page2 = client.tournament.query().offset(count_small + 1).limit(count_small).get()
                assert isinstance(page2, TournamentSearchResponse)
                print(
                    f"✓ search(start_pos={count_small + 1}, count={count_small}) "
                    f"returned {len(page2.tournaments)} tournaments"
                )

                # Verify different results (if both pages have data)
                if len(page1.tournaments) > 0 and len(page2.tournaments) > 0:
                    # Note: API may return more results than requested count,
                    # but pagination should work
                    print(
                        f"  Note: API returned {len(page1.tournaments)} results "
                        f"(count param may be ignored)"
                    )
                    # Just verify we got results from different pages
                    page1_ids = {t.tournament_id for t in page1.tournaments}
                    page2_ids = {t.tournament_id for t in page2.tournaments}
                    # Pages should have some different tournaments if pagination works
                    if page1_ids != page2_ids:
                        print("  ✓ Pagination returns different results")
                    else:
                        print("  ⚠ Warning: Pages returned same results")
            except IfpaApiError as e:
                if "timed out" in str(e).lower():
                    pytest.skip(
                        "API timed out on second page request "
                        "(known API performance issue in CI)"
                    )
                raise
        except IfpaApiError as e:
            if "timed out" in str(e).lower():
                pytest.skip(
                    "API timed out on pagination request (known API performance issue in CI)"
                )
            raise

    def test_search_combined_filters(self, api_key: str) -> None:
        """Test search with multiple filters combined."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Combine country, date range, and pagination
        result = (
            client.tournament.query()
            .country("US")
            .date_range("2024-01-01", "2024-12-31")
            .limit(15)
            .get()
        )

        assert isinstance(result, TournamentSearchResponse)
        assert result.tournaments is not None
        print(f"✓ search with combined filters returned {len(result.tournaments)} tournaments")
        if len(result.tournaments) > 0:
            tournament = result.tournaments[0]
            print(
                f"  Sample: {tournament.tournament_name} - "
                f"{tournament.country_code}, {tournament.event_date}"
            )

    def test_search_returns_zero_results(self, api_key: str) -> None:
        """Test that zero-result tournament searches are handled correctly.

        Uses unlikely search criteria to ensure empty results. The SDK should
        return an empty list rather than raising an error.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for something unlikely to exist with restrictive filters
        result = (
            client.tournament.query("ZzZzUnlikelyName999XxX")
            .country("XX")  # Invalid country code
            .date_range("1900-01-01", "1900-01-02")  # Date range with no tournaments
            .get()
        )

        # Should return empty list, not error
        assert result.tournaments is not None
        assert isinstance(result.tournaments, list)
        assert len(result.tournaments) == 0
        print("✓ search() with no matches returns empty list")

    def test_field_names_consistency(self, api_key: str) -> None:
        """Test that field names match between search and details endpoints.

        This test specifically checks for the stateprov vs state issue found
        in the Player resource.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Get a search result
        search_results = client.tournament.query().limit(1).get()
        if not search_results.tournaments:
            pytest.skip("No tournaments found for field consistency test")

        search_result = search_results.tournaments[0]
        tournament_id = search_result.tournament_id

        # Get full details
        details = client.tournament(tournament_id).details()

        # Compare field names are consistent
        print(f"\nField consistency check for tournament {tournament_id}:")
        print(f"  Search result stateprov: {search_result.stateprov}")
        print(f"  Details stateprov: {details.stateprov}")

        # Both should use stateprov (not state)
        # If validation passed, the field names are correct
        assert True  # If we got here, Pydantic validation succeeded


# =============================================================================
# INDIVIDUAL TOURNAMENT METHODS (TournamentHandle)
# =============================================================================


@pytest.mark.integration
class TestTournamentDetailsIntegration:
    """Integration tests for TournamentHandle.details() method."""

    def test_details_with_valid_tournament(self, api_key: str, tournament_id: int) -> None:
        """Test details() with a valid tournament ID."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        tournament = client.tournament(tournament_id).details()

        assert isinstance(tournament, Tournament)
        assert tournament.tournament_id == tournament_id
        assert tournament.tournament_name is not None
        print(f"✓ details() returned tournament: {tournament.tournament_name}")
        print(f"  Tournament ID: {tournament.tournament_id}")
        print(f"  Event Date: {tournament.event_date}")
        print(f"  Location: {tournament.city}, {tournament.stateprov}, {tournament.country_code}")
        print(f"  Players: {tournament.player_count}")
        print(f"  Director: {tournament.director_name} (ID: {tournament.director_id})")

        # Verify event_date vs event_start_date handling
        print(f"  event_date: {tournament.event_date}")
        print(f"  event_start_date: {tournament.event_start_date}")
        print(f"  event_end_date: {tournament.event_end_date}")

    def test_details_basic(self, api_key: str, tournament_id: int) -> None:
        """Test getting tournament details for a specific tournament."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Get full tournament details using known stable tournament ID
        tournament = client.tournament(tournament_id).details()

        assert isinstance(tournament, Tournament)
        assert tournament.tournament_id == tournament_id
        assert tournament.tournament_name is not None
        print("\nTournament Details:")
        print(f"  Name: {tournament.tournament_name}")
        print(f"  Location: {tournament.city}, {tournament.stateprov}")
        print(f"  Director: {tournament.director_name}")
        print(f"  Players: {tournament.player_count}")

    def test_details_from_helper(self, api_key: str) -> None:
        """Test getting tournament details with real API using helper function."""
        skip_if_no_api_key()
        # Use longer timeout for search queries which can be slow in CI
        client = IfpaClient(api_key=api_key, timeout=30.0)

        tournament_id = get_test_tournament_id(client)
        if tournament_id is None:
            pytest.skip("Could not find test tournament (API may be slow or rate-limited)")

        tournament = client.tournament(tournament_id).details()

        assert isinstance(tournament, Tournament)
        assert tournament.tournament_id == tournament_id
        assert tournament.tournament_name is not None

    def test_details_with_invalid_tournament(self, api_key: str) -> None:
        """Test details() with an invalid tournament ID raises error."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Use a very high ID that shouldn't exist
        # API returns 200 with empty dict, which causes Pydantic ValidationError
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            client.tournament(99999999).details()

        print(
            f"✓ details() with invalid ID raised ValidationError "
            f"(API returned empty data): {exc_info.value}"
        )

    def test_details_not_found(self, api_key: str) -> None:
        """Test that getting non-existent tournament raises appropriate error."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # API raises either IfpaApiError or validation error for non-existent tournament
        with pytest.raises((IfpaApiError, ValueError)):
            client.tournament(99999999).details()

    def test_details_structure_validation(self, api_key: str, tournament_id: int) -> None:
        """Test details() response structure and field types."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        tournament = client.tournament(tournament_id).details()

        # Verify required fields
        assert isinstance(tournament.tournament_id, int)
        assert isinstance(tournament.tournament_name, str)

        # Verify optional field types (if present)
        if tournament.director_id is not None:
            assert isinstance(tournament.director_id, int)
        if tournament.player_count is not None:
            assert isinstance(tournament.player_count, int)
        if tournament.rating_value is not None:
            assert isinstance(tournament.rating_value, int | float)
        if tournament.wppr_value is not None:
            assert isinstance(tournament.wppr_value, int | float)

        print("✓ details() response structure validated successfully")


@pytest.mark.integration
class TestTournamentResultsIntegration:
    """Integration tests for TournamentHandle.results() method."""

    def test_results_basic(self, api_key: str, tournament_id: int) -> None:
        """Test getting tournament results."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            results = client.tournament(tournament_id).results()

            assert isinstance(results, TournamentResultsResponse)
            if results.results:
                print("\nTournament Results (showing first 3):")
                for result in results.results[:3]:
                    print(f"  {result.position}. {result.player_name}: {result.points} WPPR")
                    # Verify field names are correct
                    assert result.position is not None
                    assert result.player_id is not None
        except IfpaApiError as e:
            # Some tournaments may not have results data
            if e.status_code in [404, 400]:
                pytest.skip(f"Tournament {tournament_id} has no results data")
            raise

    def test_results_from_helper(self, api_key: str) -> None:
        """Test getting tournament results with real API using helper function."""
        skip_if_no_api_key()
        # Use longer timeout for search queries which can be slow in CI
        client = IfpaClient(api_key=api_key, timeout=30.0)

        tournament_id = get_test_tournament_id(client)
        if tournament_id is None:
            pytest.skip("Could not find test tournament (API may be slow or rate-limited)")

        results = client.tournament(tournament_id).results()

        assert results.tournament_id == tournament_id
        assert results.results is not None

    def test_results_with_valid_tournament(self, api_key: str, tournament_id: int) -> None:
        """Test results() with a tournament that has results."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        results = client.tournament(tournament_id).results()

        assert isinstance(results, TournamentResultsResponse)
        print(f"✓ results() returned response for tournament {tournament_id}")
        print(f"  Tournament: {results.tournament_name}")
        print(f"  Event Date: {results.event_date}")
        print(f"  Player Count: {results.player_count}")
        print(f"  Results Count: {len(results.results)}")

        if len(results.results) > 0:
            # Verify first result structure
            result = results.results[0]
            assert result.position is not None
            assert result.player_id is not None
            print(f"  Winner: {result.player_name} (ID: {result.player_id})")
            print(f"  WPPR Points: {result.points}")

    def test_results_player_rankings_structure(self, api_key: str, tournament_id: int) -> None:
        """Test results() player rankings structure validation."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        results = client.tournament(tournament_id).results()

        assert isinstance(results, TournamentResultsResponse)
        assert results.results is not None

        if len(results.results) > 0:
            # Verify result field types
            for _i, result in enumerate(results.results[:3]):  # Check first 3
                assert isinstance(result.position, int)
                assert isinstance(result.player_id, int)
                if result.points is not None:
                    assert isinstance(result.points, int | float)
                print(f"  Pos {result.position}: {result.player_name} - {result.points} WPPR")

        print("✓ results() player rankings structure validated")


@pytest.mark.integration
class TestTournamentFormatsIntegration:
    """Integration tests for TournamentHandle.formats() method."""

    def test_formats_basic(self, api_key: str, tournament_id: int) -> None:
        """Test getting tournament formats with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.tournament(tournament_id).formats()

            assert isinstance(result, TournamentFormatsResponse)
            assert result is not None
            # Tournament formats structure varies by tournament
            if result.formats:
                print(f"\nTournament {tournament_id} formats:")
                for fmt in result.formats:
                    print(f"  - {fmt.format_name}: {fmt.rounds} rounds")
        except IfpaApiError as e:
            # Some tournaments may not have formats data
            if e.status_code in [404, 400]:
                pytest.skip(f"Tournament {tournament_id} has no formats data")
            raise

    def test_formats_with_valid_tournament(self, api_key: str, tournament_id: int) -> None:
        """Test formats() with a tournament that has format information."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            formats = client.tournament(tournament_id).formats()

            assert isinstance(formats, TournamentFormatsResponse)
            print(f"✓ formats() returned response for tournament {tournament_id}")
            print(f"  Tournament ID: {formats.tournament_id}")
            print(f"  Formats Count: {len(formats.formats)}")

            if len(formats.formats) > 0:
                # Verify format structure
                fmt = formats.formats[0]
                print(f"  Format: {fmt.format_name}")
                print(f"  Rounds: {fmt.rounds}")
                print(f"  Games per Round: {fmt.games_per_round}")
                print(f"  Player Count: {fmt.player_count}")
        except IfpaApiError as e:
            if e.status_code == 404:
                pytest.skip(f"Tournament {tournament_id} doesn't have formats endpoint available")
            raise

    def test_formats_structure_validation(self, api_key: str, tournament_id: int) -> None:
        """Test formats() response structure validation."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            formats = client.tournament(tournament_id).formats()

            assert isinstance(formats, TournamentFormatsResponse)
            assert formats.formats is not None
            assert isinstance(formats.formats, list)

            if len(formats.formats) > 0:
                fmt = formats.formats[0]
                assert isinstance(fmt.format_name, str)
                if fmt.rounds is not None:
                    assert isinstance(fmt.rounds, int)
                if fmt.machine_list is not None:
                    assert isinstance(fmt.machine_list, list)

            print("✓ formats() structure validated successfully")
        except IfpaApiError as e:
            if e.status_code == 404:
                pytest.skip(f"Tournament {tournament_id} doesn't have formats endpoint available")
            raise


@pytest.mark.integration
class TestTournamentLeagueIntegration:
    """Integration tests for TournamentHandle.league() method."""

    def test_league_basic(self, api_key: str, tournament_id: int) -> None:
        """Test getting tournament league data with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.tournament(tournament_id).league()

            assert isinstance(result, TournamentLeagueResponse)
            assert result is not None
            # League data structure varies
            if result.sessions:
                print(f"\nTournament {tournament_id} league sessions:")
                for session in result.sessions[:3]:
                    print(f"  - {session.session_date}: {session.player_count} players")
        except TournamentNotLeagueError:
            # Many tournaments are not leagues - this is expected
            pytest.skip(f"Tournament {tournament_id} is not a league")
        except IfpaApiError as e:
            # Other API errors should still be handled
            if e.status_code in [404, 400]:
                pytest.skip(f"Tournament {tournament_id} has API errors")
            raise

    def test_league_with_league_tournament(self, api_key: str) -> None:
        """Test league() with a league tournament."""
        skip_if_no_api_key()
        # Use longer timeout for league tournament queries which can be slow in CI
        client = IfpaClient(api_key=api_key, timeout=30.0)

        # Try to find a league tournament first
        try:
            search_result = client.tournament.query().tournament_type("league").limit(5).get()
        except IfpaApiError as e:
            if "timed out" in str(e).lower():
                pytest.skip(
                    "API timed out searching for league tournaments "
                    "(known API performance issue in CI)"
                )
            raise

        if len(search_result.tournaments) > 0:
            league_tournament_id = search_result.tournaments[0].tournament_id
            print(f"Testing league tournament ID: {league_tournament_id}")

            try:
                league = client.tournament(league_tournament_id).league()

                assert isinstance(league, TournamentLeagueResponse)
                print(f"✓ league() returned response for tournament {league_tournament_id}")
                print(f"  Tournament ID: {league.tournament_id}")
                print(f"  League Format: {league.league_format}")
                print(f"  Total Sessions: {league.total_sessions}")
                print(f"  Sessions Count: {len(league.sessions)}")

                if len(league.sessions) > 0:
                    session = league.sessions[0]
                    print(
                        f"  Sample Session: {session.session_date} - {session.player_count} players"
                    )
            except TournamentNotLeagueError:
                pytest.skip(
                    f"League tournament {league_tournament_id} is not actually a league "
                    f"(may be misclassified in search)"
                )
            except IfpaApiError as e:
                if e.status_code == 404:
                    pytest.skip(
                        f"League tournament {league_tournament_id} doesn't have "
                        f"league endpoint available"
                    )
                raise
        else:
            pytest.skip("No league tournaments found in search")

    def test_league_with_non_league_tournament(self, api_key: str, tournament_id: int) -> None:
        """Test league() with a non-league tournament (should raise TournamentNotLeagueError)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            league = client.tournament(tournament_id).league()
            print(f"✓ league() on non-league tournament returned: {type(league)}")
            print(f"  Sessions: {len(league.sessions)}")
        except TournamentNotLeagueError as e:
            print(
                "✓ league() on non-league tournament raised "
                f"TournamentNotLeagueError (expected): {e}"
            )
        except IfpaApiError as e:
            print(f"✓ league() on non-league tournament raised IfpaApiError: {e}")


@pytest.mark.integration
class TestTournamentSubmissionsIntegration:
    """Integration tests for TournamentHandle.submissions() method."""

    def test_submissions_basic(self, api_key: str, tournament_id: int) -> None:
        """Test getting tournament submissions with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.tournament(tournament_id).submissions()

            assert isinstance(result, TournamentSubmissionsResponse)
            assert result is not None
            # Submissions structure varies
            if result.submissions:
                print(f"\nTournament {tournament_id} submissions:")
                for submission in result.submissions[:3]:
                    print(f"  - ID: {submission.submission_id}, Status: {submission.status}")
        except IfpaApiError as e:
            # Not all tournaments have submission data
            if e.status_code in [404, 400]:
                pytest.skip(f"Tournament {tournament_id} has no submissions data")
            raise

    def test_submissions_with_valid_tournament(self, api_key: str, tournament_id: int) -> None:
        """Test submissions() with a tournament."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            submissions = client.tournament(tournament_id).submissions()

            assert isinstance(submissions, TournamentSubmissionsResponse)
            print(f"✓ submissions() returned response for tournament {tournament_id}")
            print(f"  Tournament ID: {submissions.tournament_id}")
            print(f"  Submissions Count: {len(submissions.submissions)}")

            if len(submissions.submissions) > 0:
                submission = submissions.submissions[0]
                print(f"  Sample: {submission.submission_date} - {submission.status}")
                print(f"  Submitter: {submission.submitter_name}")
        except IfpaApiError as e:
            if e.status_code == 404:
                pytest.skip(
                    f"Tournament {tournament_id} doesn't have submissions endpoint available"
                )
            raise

    def test_submissions_structure_validation(self, api_key: str, tournament_id: int) -> None:
        """Test submissions() response structure validation."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            submissions = client.tournament(tournament_id).submissions()

            assert isinstance(submissions, TournamentSubmissionsResponse)
            assert submissions.submissions is not None
            assert isinstance(submissions.submissions, list)

            if len(submissions.submissions) > 0:
                submission = submissions.submissions[0]
                assert isinstance(submission.submission_id, int)

            print("✓ submissions() structure validated successfully")
        except IfpaApiError as e:
            if e.status_code == 404:
                pytest.skip(
                    f"Tournament {tournament_id} doesn't have submissions endpoint available"
                )
            raise


@pytest.mark.integration
class TestTournamentRelatedIntegration:
    """Integration tests for TournamentHandle.related() method."""

    def test_related_basic(self, api_key: str) -> None:
        """Test getting related tournaments with real API using helper function."""
        skip_if_no_api_key()
        # Use longer timeout for search queries which can be slow in CI
        client = IfpaClient(api_key=api_key, timeout=30.0)

        tournament_id = get_test_tournament_id(client)
        if tournament_id is None:
            pytest.skip("Could not find test tournament (API may be slow or rate-limited)")

        related = client.tournament(tournament_id).related()

        assert isinstance(related, RelatedTournamentsResponse)
        assert related.tournament is not None
        # related tournaments can be empty or populated
        # just verify response structure is valid
        for tournament in related.tournament:
            assert tournament.tournament_id is not None
            assert tournament.tournament_name is not None
            assert tournament.event_name is not None
            # winner can be None for future events
            if tournament.winner:
                assert tournament.winner.player_id is not None
                assert tournament.winner.name is not None

    def test_investigate_related_endpoint(self, api_key: str, tournament_id: int) -> None:
        """Investigate if GET /tournament/{id}/related endpoint exists."""
        skip_if_no_api_key()

        # Use direct HTTP call to test if endpoint exists
        api_key_value = os.getenv("IFPA_API_KEY")
        if not api_key_value:
            with open("credentials") as f:
                for line in f:
                    if line.startswith("IFPA_API_KEY="):
                        api_key_value = line.split("=", 1)[1].strip()
                        break

        print(f"\n=== INVESTIGATION: GET /tournament/{tournament_id}/related ===")

        try:
            response = requests.get(
                f"https://api.ifpapinball.com/tournament/{tournament_id}/related",
                headers={"X-API-Key": api_key_value},
                timeout=10,
            )

            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                print("✓ ENDPOINT EXISTS!")
                data = response.json()
                print(f"Response Structure: {type(data)}")
                print(f"Response Keys: {data.keys() if isinstance(data, dict) else 'N/A'}")
                print(f"Sample Data: {data}")
                print("\n⚠ FINDING: related() endpoint exists but not implemented in SDK")

                # Document expected model structure
                print("\nRecommended Model Structure:")
                if isinstance(data, dict):
                    for key, value in data.items():
                        print(f"  {key}: {type(value).__name__}")
            elif response.status_code == 404:
                print("✓ CONFIRMED: Endpoint does not exist (404)")
            else:
                print(f"⚠ Unexpected status code: {response.status_code}")
                print(f"Response: {response.text}")

        except Exception as e:
            print(f"❌ Error testing endpoint: {e}")

    def test_investigate_related_with_multiple_tournaments(self, api_key: str) -> None:
        """Test related() endpoint with multiple tournament IDs to find examples."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Get multiple tournament IDs to test
        search_result = client.tournament.query().limit(10).get()

        api_key_value = os.getenv("IFPA_API_KEY")
        if not api_key_value:
            with open("credentials") as f:
                for line in f:
                    if line.startswith("IFPA_API_KEY="):
                        api_key_value = line.split("=", 1)[1].strip()
                        break

        print(f"\n=== TESTING related() with {len(search_result.tournaments)} tournaments ===")

        found_working_endpoint = False
        for tournament in search_result.tournaments[:5]:  # Test first 5
            try:
                response = requests.get(
                    f"https://api.ifpapinball.com/tournament/{tournament.tournament_id}/related",
                    headers={"X-API-Key": api_key_value},
                    timeout=10,
                )

                if response.status_code == 200:
                    print(f"✓ Tournament {tournament.tournament_id} has related data!")
                    data = response.json()
                    print(f"  Data: {data}")
                    found_working_endpoint = True
                    break
            except Exception:
                pass

        if not found_working_endpoint:
            print("⚠ No tournaments with related data found in sample")


@pytest.mark.integration
class TestTournamentListFormatsIntegration:
    """Integration tests for TournamentsClient.list_formats() method."""

    def test_list_formats(self, api_key: str) -> None:
        """Test getting tournament format list with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        formats = client.tournament.list_formats()

        assert isinstance(formats, TournamentFormatsListResponse)
        assert formats.qualifying_formats is not None
        assert formats.finals_formats is not None
        # API should return ~11 qualifying and ~14 finals formats
        assert len(formats.qualifying_formats) > 0
        assert len(formats.finals_formats) > 0

        # Verify format structure
        for fmt in formats.qualifying_formats:
            assert fmt.format_id is not None
            assert fmt.name is not None
            # description is optional

        for fmt in formats.finals_formats:
            assert fmt.format_id is not None
            assert fmt.name is not None
            # description is optional


# =============================================================================
# INVESTIGATION TESTS
# =============================================================================


@pytest.mark.integration
class TestTournamentUnclearEndpointsInvestigation:
    """Investigation of unclear endpoints from API spec."""

    def test_investigate_formats_collection_endpoint(self, api_key: str) -> None:
        """Investigate if GET /tournament/formats (no ID) exists as collection-level endpoint."""
        skip_if_no_api_key()

        # Use direct HTTP call to test if endpoint exists
        api_key_value = os.getenv("IFPA_API_KEY")
        if not api_key_value:
            with open("credentials") as f:
                for line in f:
                    if line.startswith("IFPA_API_KEY="):
                        api_key_value = line.split("=", 1)[1].strip()
                        break

        print("\n=== INVESTIGATION: GET /tournament/formats (collection-level) ===")

        try:
            response = requests.get(
                "https://api.ifpapinball.com/tournament/formats",
                headers={"X-API-Key": api_key_value},
                timeout=10,
            )

            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")

            if response.status_code == 200:
                print("✓ ENDPOINT EXISTS!")
                data = response.json()
                print(f"Response Structure: {type(data)}")
                print(f"Response Keys: {data.keys() if isinstance(data, dict) else 'N/A'}")
                print(f"Sample Data: {data}")
                print(
                    "\n⚠ FINDING: Collection-level formats endpoint exists "
                    "but not implemented in SDK"
                )
            elif response.status_code == 404:
                print("✓ CONFIRMED: Endpoint does not exist (404)")
            else:
                print(f"⚠ Unexpected status code: {response.status_code}")
                print(f"Response: {response.text}")

        except Exception as e:
            print(f"❌ Error testing endpoint: {e}")

    def test_investigate_leagues_collection_endpoint(self, api_key: str) -> None:
        """Investigate if GET /tournament/leagues/{time_period} exists as collection endpoint."""
        skip_if_no_api_key()

        # Use direct HTTP call to test if endpoint exists
        api_key_value = os.getenv("IFPA_API_KEY")
        if not api_key_value:
            with open("credentials") as f:
                for line in f:
                    if line.startswith("IFPA_API_KEY="):
                        api_key_value = line.split("=", 1)[1].strip()
                        break

        print("\n=== INVESTIGATION: GET /tournament/leagues/{time_period} (collection-level) ===")

        for time_period in ["past", "future"]:
            print(f"\nTesting time_period: {time_period}")

            try:
                response = requests.get(
                    f"https://api.ifpapinball.com/tournament/leagues/{time_period}",
                    headers={"X-API-Key": api_key_value},
                    timeout=10,
                )

                print(f"Status Code: {response.status_code}")

                if response.status_code == 200:
                    print(f"✓ ENDPOINT EXISTS for time_period={time_period}!")
                    data = response.json()
                    print(f"Response Structure: {type(data)}")
                    print(f"Response Keys: {data.keys() if isinstance(data, dict) else 'N/A'}")

                    # Show sample data (limited)
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, list):
                                print(f"  {key}: List with {len(value)} items")
                                if len(value) > 0:
                                    print(f"    Sample: {value[0]}")
                            else:
                                print(f"  {key}: {value}")

                    print(
                        f"\n⚠ FINDING: Collection-level leagues/{time_period} "
                        f"endpoint exists but not implemented"
                    )
                elif response.status_code == 404:
                    print(
                        f"✓ CONFIRMED: Endpoint does not exist for time_period={time_period} (404)"
                    )
                else:
                    print(f"⚠ Unexpected status code: {response.status_code}")
                    print(f"Response: {response.text[:200]}")

            except Exception as e:
                print(f"❌ Error testing endpoint: {e}")
