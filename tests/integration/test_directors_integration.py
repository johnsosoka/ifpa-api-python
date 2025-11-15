"""Integration tests for DirectorsClient and DirectorHandle.

These tests make real API calls to the IFPA API and require a valid API key.
Run with: pytest -m integration
"""

import pytest

from ifpa_sdk.client import IfpaClient
from ifpa_sdk.models.common import TimePeriod
from ifpa_sdk.models.director import Director, DirectorSearchResponse
from tests.integration.helpers import get_test_director_id, skip_if_no_api_key


@pytest.mark.integration
class TestDirectorsClientIntegration:
    """Integration tests for DirectorsClient."""

    def test_search_directors(self, api_key: str) -> None:
        """Test searching for directors with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.directors.search()

        assert isinstance(result, DirectorSearchResponse)
        # API should return some directors
        assert result.directors is not None

    def test_country_directors(self, api_key: str) -> None:
        """Test getting country directors list with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.directors.country_directors()

        assert result.country_directors is not None
        # There should be at least some country directors
        if len(result.country_directors) > 0:
            # Verify structure of first entry
            director = result.country_directors[0]
            assert director.player_id > 0
            assert director.name is not None
            assert director.country_code is not None


@pytest.mark.integration
class TestDirectorHandleIntegration:
    """Integration tests for DirectorHandle."""

    def test_get_director(self, api_key: str) -> None:
        """Test getting director details with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Find a director to test with
        director_id = get_test_director_id(client)
        if director_id is None:
            pytest.skip("Could not find test director")

        # Get director details
        director = client.director(director_id).get()

        assert isinstance(director, Director)
        assert director.director_id == director_id
        assert director.name is not None

    def test_director_tournaments_past(self, api_key: str) -> None:
        """Test getting past tournaments for a director with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Find a director to test with
        director_id = get_test_director_id(client)
        if director_id is None:
            pytest.skip("Could not find test director")

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
        if director_id is None:
            pytest.skip("Could not find test director")

        # Get future tournaments (may be empty)
        result = client.director(director_id).tournaments(TimePeriod.FUTURE)

        assert result.director_id == director_id
        assert result.tournaments is not None
