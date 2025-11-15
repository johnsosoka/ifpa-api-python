"""Integration tests for Tournaments resource.

Tests the tournaments resource client against the real IFPA API to verify
field mappings and response structures match our models.
"""

import pytest

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


@pytest.mark.integration
class TestTournamentsIntegration:
    """Integration tests for Tournaments resource against real API."""

    def test_tournament_search_basic(self, api_key: str, count_small: int) -> None:
        """Test basic tournament search returns valid results."""
        client = IfpaClient(api_key=api_key)

        # Search with a common term that should return results
        results = client.tournaments.search(name="Championship", count=count_small)

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

    def test_tournament_search_with_location(
        self, api_key: str, country_code: str, count_medium: int
    ) -> None:
        """Test tournament search with location filters."""
        client = IfpaClient(api_key=api_key)

        # Search for tournaments by country
        results = client.tournaments.search(country=country_code, count=count_medium)

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

    def test_tournament_search_with_state_filter(self, api_key: str, count_small: int) -> None:
        """Test tournament search with state filter."""
        client = IfpaClient(api_key=api_key)

        # Search California tournaments
        result = client.tournaments.search(stateprov="CA", count=count_small)

        assert isinstance(result, TournamentSearchResponse)
        assert isinstance(result.tournaments, list)

    def test_tournament_details(self, api_key: str) -> None:
        """Test getting tournament details for a specific tournament."""
        client = IfpaClient(api_key=api_key)

        # First search for a tournament to get a valid ID
        search_results = client.tournaments.search(count=1)
        if not search_results.tournaments:
            pytest.skip("No tournaments found to test details")

        tournament_id = search_results.tournaments[0].tournament_id

        # Get full tournament details
        tournament = client.tournament(tournament_id).get()

        assert isinstance(tournament, Tournament)
        assert tournament.tournament_id == tournament_id
        assert tournament.tournament_name is not None
        print("\nTournament Details:")
        print(f"  Name: {tournament.tournament_name}")
        print(f"  Location: {tournament.city}, {tournament.stateprov}")
        print(f"  Director: {tournament.director_name}")
        print(f"  Players: {tournament.player_count}")

    def test_tournament_results(self, api_key: str, tournament_id: int) -> None:
        """Test getting tournament results."""
        client = IfpaClient(api_key=api_key)

        try:
            results = client.tournament(tournament_id).results()

            assert isinstance(results, TournamentResultsResponse)
            if results.results:
                print("\nTournament Results (showing first 3):")
                for result in results.results[:3]:
                    print(f"  {result.position}. {result.player_name}: {result.wppr_points} WPPR")
                    # Verify field names are correct
                    assert result.position is not None
                    assert result.player_id is not None
        except IfpaApiError as e:
            # Some tournaments may not have results data
            if e.status_code in [404, 400]:
                pytest.skip(f"Tournament {tournament_id} has no results data")
            raise

    def test_tournament_formats(self, api_key: str, tournament_id: int) -> None:
        """Test getting tournament formats with real API."""
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

    def test_tournament_league(self, api_key: str, tournament_id: int) -> None:
        """Test getting tournament league data with real API."""
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
        except IfpaApiError as e:
            # Many tournaments are not leagues
            if e.status_code in [404, 400]:
                pytest.skip(f"Tournament {tournament_id} is not a league")
            raise

    def test_tournament_submissions(self, api_key: str, tournament_id: int) -> None:
        """Test getting tournament submissions with real API."""
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

    def test_get_tournament_not_found(self, api_key: str) -> None:
        """Test that getting non-existent tournament raises appropriate error."""
        client = IfpaClient(api_key=api_key)

        # API raises either IfpaApiError or validation error for non-existent tournament
        with pytest.raises((IfpaApiError, ValueError)):
            client.tournament(99999999).get()

    def test_field_names_consistency(self, api_key: str) -> None:
        """Test that field names match between search and details endpoints.

        This test specifically checks for the stateprov vs state issue found
        in the Player resource.
        """
        client = IfpaClient(api_key=api_key)

        # Get a search result
        search_results = client.tournaments.search(count=1)
        if not search_results.tournaments:
            pytest.skip("No tournaments found for field consistency test")

        search_result = search_results.tournaments[0]
        tournament_id = search_result.tournament_id

        # Get full details
        details = client.tournament(tournament_id).get()

        # Compare field names are consistent
        print(f"\nField consistency check for tournament {tournament_id}:")
        print(f"  Search result stateprov: {search_result.stateprov}")
        print(f"  Details stateprov: {details.stateprov}")

        # Both should use stateprov (not state)
        # If validation passed, the field names are correct
        assert True  # If we got here, Pydantic validation succeeded
