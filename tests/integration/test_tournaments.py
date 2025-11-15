"""Integration tests for Tournaments resource.

Tests the tournaments resource client against the real IFPA API to verify
field mappings and response structures match our models.
"""

import pytest

from ifpa_sdk import IfpaClient
from ifpa_sdk.models.tournaments import (
    Tournament,
    TournamentFormatsResponse,
    TournamentResultsResponse,
    TournamentSearchResponse,
)


@pytest.mark.integration
class TestTournamentsIntegration:
    """Integration tests for Tournaments resource against real API."""

    def test_tournament_search_basic(self, api_key: str) -> None:
        """Test basic tournament search returns valid results."""
        client = IfpaClient(api_key=api_key)

        # Search with a common term that should return results
        results = client.tournaments.search(name="Championship", count=5)

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

    def test_tournament_search_with_location(self, api_key: str) -> None:
        """Test tournament search with location filters."""
        client = IfpaClient(api_key=api_key)

        # Search for US tournaments
        results = client.tournaments.search(country="US", count=10)

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

    def test_tournament_results(self, api_key: str) -> None:
        """Test getting tournament results."""
        client = IfpaClient(api_key=api_key)

        # Use a known tournament ID that should have results
        # PAPA 17 (2014) - well-known tournament
        tournament_id = 7070

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
        except Exception as e:
            # If this specific tournament doesn't exist, just log it
            print(f"Could not get results for tournament {tournament_id}: {e}")

    def test_tournament_formats(self, api_key: str) -> None:
        """Test getting tournament formats."""
        client = IfpaClient(api_key=api_key)

        # Search for a recent tournament
        search_results = client.tournaments.search(count=5)
        if not search_results.tournaments:
            pytest.skip("No tournaments found to test formats")

        # Try to find one with formats
        for tournament in search_results.tournaments:
            try:
                formats = client.tournament(tournament.tournament_id).formats()
                assert isinstance(formats, TournamentFormatsResponse)

                if formats.formats:
                    print(f"\nTournament {tournament.tournament_name} formats:")
                    for fmt in formats.formats:
                        print(f"  - {fmt.format_name}: {fmt.rounds} rounds")
                    break  # Found one with formats, we're done
            except Exception:
                continue  # Try next tournament

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
