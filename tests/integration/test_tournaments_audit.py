"""Comprehensive audit tests for Tournaments resource.

This module contains detailed integration tests for all Tournaments resource methods,
validating parameters, response structures, and edge cases against the live IFPA API.

Test Coverage:
- TournamentsClient.search() - All 9 parameters
- TournamentHandle.get() - Valid/invalid IDs, response structure
- TournamentHandle.results() - Tournament results structure
- TournamentHandle.formats() - Format structure
- TournamentHandle.league() - League data structure
- TournamentHandle.submissions() - Submission structure
- Investigation of unclear endpoints (formats/leagues collection-level)
- Investigation of missing related() endpoint

Run with: pytest tests/integration/test_tournaments_audit.py -v
"""

import os

import pytest
import requests

from ifpa_api import IfpaClient
from ifpa_api.exceptions import IfpaApiError
from ifpa_api.models.tournaments import (
    Tournament,
    TournamentFormatsResponse,
    TournamentLeagueResponse,
    TournamentResultsResponse,
    TournamentSearchResponse,
    TournamentSubmissionsResponse,
)
from tests.integration.helpers import skip_if_no_api_key


@pytest.mark.integration
class TestTournamentsSearchAudit:
    """Comprehensive audit of TournamentsClient.search() method."""

    def test_search_no_parameters(self, api_key: str) -> None:
        """Test search with no parameters returns results."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.tournaments.search()

        assert isinstance(result, TournamentSearchResponse)
        assert result.tournaments is not None
        assert isinstance(result.tournaments, list)
        print(f"✓ search() with no parameters returned {len(result.tournaments)} tournaments")
        if len(result.tournaments) > 0:
            tournament = result.tournaments[0]
            print(f"  Sample: {tournament.tournament_name} (ID: {tournament.tournament_id})")

    def test_search_by_name(self, api_key: str) -> None:
        """Test search by tournament name (partial match)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for common tournament name
        result = client.tournaments.search(name="Pinball")

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
        result = client.tournaments.search(city="Portland")

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
        result = client.tournaments.search(stateprov="OR")

        assert isinstance(result, TournamentSearchResponse)
        assert result.tournaments is not None
        print(f"✓ search(stateprov='OR') returned {len(result.tournaments)} tournaments")
        if len(result.tournaments) > 0:
            tournament = result.tournaments[0]
            print(f"  Sample: {tournament.tournament_name} - {tournament.stateprov}")

    def test_search_by_country(self, api_key: str, country_code: str) -> None:
        """Test search filtering by country code."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.tournaments.search(country=country_code, count=5)

        assert isinstance(result, TournamentSearchResponse)
        assert result.tournaments is not None
        print(f"✓ search(country='{country_code}') returned {len(result.tournaments)} tournaments")
        if len(result.tournaments) > 0:
            tournament = result.tournaments[0]
            print(f"  Sample: {tournament.tournament_name} - {tournament.country_code}")

    def test_search_by_start_date(self, api_key: str) -> None:
        """Test that search rejects start_date without end_date."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Should raise ValueError - both dates required together
        with pytest.raises(ValueError, match="start_date and end_date must be provided together"):
            client.tournaments.search(start_date="2024-01-01", count=10)

        print("✓ search(start_date='2024-01-01') correctly raised ValueError")

    def test_search_by_end_date(self, api_key: str) -> None:
        """Test that search rejects end_date without start_date."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Should raise ValueError - both dates required together
        with pytest.raises(ValueError, match="start_date and end_date must be provided together"):
            client.tournaments.search(end_date="2024-12-31", count=10)

        print("✓ search(end_date='2024-12-31') correctly raised ValueError")

    def test_search_by_date_range(self, api_key: str) -> None:
        """Test search filtering by date range (start_date and end_date)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for tournaments in 2024
        result = client.tournaments.search(start_date="2024-01-01", end_date="2024-12-31", count=20)

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
        result = client.tournaments.search(tournament_type="women", count=10)

        assert isinstance(result, TournamentSearchResponse)
        assert result.tournaments is not None
        print(f"✓ search(tournament_type='women') returned {len(result.tournaments)} tournaments")
        if len(result.tournaments) > 0:
            tournament = result.tournaments[0]
            print(f"  Sample: {tournament.tournament_name} (ID: {tournament.tournament_id})")

    def test_search_with_pagination(self, api_key: str, count_small: int) -> None:
        """Test search with pagination parameters (start_pos, count)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Get first page (API requires start_pos >= 1)
        page1 = client.tournaments.search(start_pos=1, count=count_small)
        assert isinstance(page1, TournamentSearchResponse)
        print(
            f"✓ search(start_pos=1, count={count_small}) "
            f"returned {len(page1.tournaments)} tournaments"
        )

        # Try to get second page - may timeout on API side
        try:
            page2 = client.tournaments.search(start_pos=count_small + 1, count=count_small)
            assert isinstance(page2, TournamentSearchResponse)
            print(
                f"✓ search(start_pos={count_small + 1}, count={count_small}) "
                f"returned {len(page2.tournaments)} tournaments"
            )

            # Verify different results (if both pages have data)
            if len(page1.tournaments) > 0 and len(page2.tournaments) > 0:
                # Note: API may return more results than requested count, but pagination should work
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
                pytest.skip("API timed out on pagination request (known API issue)")
            raise

    def test_search_combined_filters(self, api_key: str) -> None:
        """Test search with multiple filters combined."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Combine country, date range, and pagination
        result = client.tournaments.search(
            country="US", start_date="2024-01-01", end_date="2024-12-31", count=15
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


@pytest.mark.integration
class TestTournamentHandleGetAudit:
    """Comprehensive audit of TournamentHandle.get() method."""

    def test_get_valid_tournament(self, api_key: str, tournament_id: int) -> None:
        """Test get() with a valid tournament ID."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        tournament = client.tournament(tournament_id).get()

        assert isinstance(tournament, Tournament)
        assert tournament.tournament_id == tournament_id
        assert tournament.tournament_name is not None
        print(f"✓ get() returned tournament: {tournament.tournament_name}")
        print(f"  Tournament ID: {tournament.tournament_id}")
        print(f"  Event Date: {tournament.event_date}")
        print(f"  Location: {tournament.city}, {tournament.stateprov}, {tournament.country_code}")
        print(f"  Players: {tournament.player_count}")
        print(f"  Director: {tournament.director_name} (ID: {tournament.director_id})")

        # Verify event_date vs event_start_date handling
        print(f"  event_date: {tournament.event_date}")
        print(f"  event_start_date: {tournament.event_start_date}")
        print(f"  event_end_date: {tournament.event_end_date}")

    def test_get_invalid_tournament(self, api_key: str) -> None:
        """Test get() with an invalid tournament ID raises error."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Use a very high ID that shouldn't exist
        # API returns 200 with empty dict instead of 404, causing ValidationError
        from pydantic_core import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            client.tournament(99999999).get()

        print(
            f"✓ get() with invalid ID raised ValidationError "
            f"(API returned empty data): {exc_info.value}"
        )

    def test_get_tournament_structure_validation(self, api_key: str, tournament_id: int) -> None:
        """Test get() response structure and field types."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        tournament = client.tournament(tournament_id).get()

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

        print("✓ get() response structure validated successfully")


@pytest.mark.integration
class TestTournamentHandleResultsAudit:
    """Comprehensive audit of TournamentHandle.results() method."""

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
            print(f"  WPPR Points: {result.wppr_points}")

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
                if result.wppr_points is not None:
                    assert isinstance(result.wppr_points, int | float)
                print(f"  Pos {result.position}: {result.player_name} - {result.wppr_points} WPPR")

        print("✓ results() player rankings structure validated")


@pytest.mark.integration
class TestTournamentHandleFormatsAudit:
    """Comprehensive audit of TournamentHandle.formats() method."""

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
class TestTournamentHandleLeagueAudit:
    """Comprehensive audit of TournamentHandle.league() method."""

    def test_league_with_league_tournament(self, api_key: str) -> None:
        """Test league() with a league tournament."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Try to find a league tournament first
        search_result = client.tournaments.search(tournament_type="league", count=5)

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
        """Test league() with a non-league tournament (may return empty or error)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            league = client.tournament(tournament_id).league()
            print(f"✓ league() on non-league tournament returned: {type(league)}")
            print(f"  Sessions: {len(league.sessions)}")
        except IfpaApiError as e:
            print(f"✓ league() on non-league tournament raised error (expected): {e}")


@pytest.mark.integration
class TestTournamentHandleSubmissionsAudit:
    """Comprehensive audit of TournamentHandle.submissions() method."""

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


@pytest.mark.integration
class TestTournamentMissingEndpointInvestigation:
    """Investigation of potentially missing related() endpoint."""

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
        search_result = client.tournaments.search(count=10)

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
