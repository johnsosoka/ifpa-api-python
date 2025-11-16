"""Integration tests for DirectorsClient and DirectorHandle.

These tests make real API calls to the IFPA API and require a valid API key.
Run with: pytest -m integration
"""

import pytest

from ifpa_api.client import IfpaClient
from ifpa_api.exceptions import IfpaApiError
from ifpa_api.models.common import TimePeriod
from ifpa_api.models.director import Director, DirectorSearchResponse
from tests.integration.helpers import get_test_director_id, skip_if_no_api_key


@pytest.mark.integration
class TestDirectorsClientIntegration:
    """Integration tests for DirectorsClient."""

    def test_search_directors(self, api_key: str) -> None:
        """Test searching for directors with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.director.search()

        assert isinstance(result, DirectorSearchResponse)
        # API should return some directors
        assert result.directors is not None

    def test_search_directors_with_filters(self, api_key: str, country_code: str) -> None:
        """Test searching directors with country filter parameter."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search with country filter
        result = client.director.search(country=country_code)

        assert result.directors is not None
        assert isinstance(result.directors, list)
        # Verify structure if results exist
        if len(result.directors) > 0:
            director = result.directors[0]
            assert director.director_id > 0
            assert director.name is not None


@pytest.mark.integration
class TestDirectorHandleIntegration:
    """Integration tests for DirectorHandle."""

    def test_get_director(self, api_key: str) -> None:
        """Test getting director details with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Find a director to test with
        director_id = get_test_director_id(client)
        assert director_id is not None, "Could not find test director"

        # Get director details
        director = client.director(director_id).details()

        assert isinstance(director, Director)
        assert director.director_id == director_id
        assert director.name is not None

    def test_get_director_not_found(self, api_key: str) -> None:
        """Test that getting non-existent director raises appropriate error."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Use very high ID that doesn't exist
        with pytest.raises(IfpaApiError) as exc_info:
            client.director(99999999).details()

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
