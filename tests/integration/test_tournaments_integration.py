"""Integration tests for TournamentsClient and TournamentHandle.

These tests make real API calls to the IFPA API and require a valid API key.
Run with: pytest -m integration
"""

import pytest

from ifpa_api.client import IfpaClient
from ifpa_api.models.tournaments import (
    RelatedTournamentsResponse,
    Tournament,
    TournamentFormatsListResponse,
    TournamentSearchResponse,
)
from tests.integration.helpers import get_test_tournament_id, skip_if_no_api_key


@pytest.mark.integration
class TestTournamentsClientIntegration:
    """Integration tests for TournamentsClient."""

    def test_search_tournaments(self, api_key: str) -> None:
        """Test searching for tournaments with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.tournaments.search(count=10)

        assert isinstance(result, TournamentSearchResponse)
        assert result.tournaments is not None

    def test_search_tournaments_with_country_filter(self, api_key: str) -> None:
        """Test searching tournaments with country filter."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.tournaments.search(country="US", count=5)

        assert isinstance(result, TournamentSearchResponse)
        assert result.tournaments is not None
        # If results exist, verify they match filter
        if len(result.tournaments) > 0:
            for tournament in result.tournaments:
                if tournament.country_code:
                    assert tournament.country_code == "US"

    def test_list_formats(self, api_key: str) -> None:
        """Test getting tournament format list with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        formats = client.tournaments.list_formats()

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


@pytest.mark.integration
class TestTournamentHandleIntegration:
    """Integration tests for TournamentHandle."""

    def test_get_tournament(self, api_key: str) -> None:
        """Test getting tournament details with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        tournament_id = get_test_tournament_id(client)
        assert tournament_id is not None, "Could not find test tournament"

        tournament = client.tournament(tournament_id).get()

        assert isinstance(tournament, Tournament)
        assert tournament.tournament_id == tournament_id
        assert tournament.tournament_name is not None

    def test_tournament_results(self, api_key: str) -> None:
        """Test getting tournament results with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        tournament_id = get_test_tournament_id(client)
        assert tournament_id is not None, "Could not find test tournament"

        results = client.tournament(tournament_id).results()

        assert results.tournament_id == tournament_id
        assert results.results is not None

    def test_tournament_related(self, api_key: str) -> None:
        """Test getting related tournaments with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        tournament_id = get_test_tournament_id(client)
        assert tournament_id is not None, "Could not find test tournament"

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
