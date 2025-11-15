"""Integration tests for SeriesClient and SeriesHandle.

These tests make real API calls to the IFPA API and require a valid API key.
Run with: pytest -m integration
"""

import pytest

from ifpa_api.client import IfpaClient
from ifpa_api.exceptions import IfpaApiError
from ifpa_api.models.series import SeriesListResponse
from tests.integration.helpers import get_test_series_code, skip_if_no_api_key


@pytest.mark.integration
class TestSeriesClientIntegration:
    """Integration tests for SeriesClient."""

    def test_list_series(self, api_key: str) -> None:
        """Test listing series with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.series.list()

        assert isinstance(result, SeriesListResponse)
        assert result.series is not None

    def test_list_active_series(self, api_key: str) -> None:
        """Test listing only active series with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.series.list(active_only=True)

        assert isinstance(result, SeriesListResponse)
        assert result.series is not None
        # If series exist, verify structure
        if len(result.series) > 0:
            first_series = result.series[0]
            assert first_series.series_code is not None
            assert first_series.series_name is not None


@pytest.mark.integration
class TestSeriesHandleIntegration:
    """Integration tests for SeriesHandle."""

    def test_series_standings(self, api_key: str, count_small: int) -> None:
        """Test getting series standings with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_code = get_test_series_code(client)
        assert series_code is not None, "Could not find test series"

        try:
            # Some series may require region_code parameter
            standings = client.series_handle(series_code).standings(count=count_small)

            assert standings.series_code == series_code
            assert standings.standings is not None
        except IfpaApiError as e:
            if e.status_code == 400 and "Region Code" in str(e):
                pytest.skip(f"Series {series_code} requires region_code parameter")
            raise

    def test_series_overview(self, api_key: str) -> None:
        """Test getting series overview with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_code = get_test_series_code(client)
        assert series_code is not None, "Could not find test series"

        try:
            overview = client.series_handle(series_code).overview()

            assert overview.series_code == series_code
            assert overview.series_name is not None
        except IfpaApiError as e:
            # Not all series have overview endpoints available
            if e.status_code == 404:
                pytest.skip(f"Series {series_code} overview not available")
            raise

    def test_series_player_card(self, api_key: str, player_active_id: int) -> None:
        """Test getting player series card with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_code = get_test_series_code(client)
        assert series_code is not None, "Could not find test series"

        try:
            card = client.series_handle(series_code).player_card(player_active_id, "OH")
            assert card is not None
            # Player card structure varies by series
        except IfpaApiError as e:
            # Player may not have participated in this series
            if e.status_code == 404:
                pytest.skip(f"Player {player_active_id} not in series {series_code}")
            raise

    def test_series_regions(self, api_key: str) -> None:
        """Test getting series regions with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_code = get_test_series_code(client)
        assert series_code is not None, "Could not find test series"

        try:
            regions = client.series_handle(series_code).regions()
            assert regions is not None
            # Regions structure varies by series
        except IfpaApiError as e:
            # Some series endpoints require additional parameters
            if e.status_code == 400:
                pytest.skip(f"Series {series_code} regions endpoint requires parameters")
            if e.status_code == 404:
                pytest.skip(f"Series {series_code} regions not available")
            raise

    def test_series_rules(self, api_key: str) -> None:
        """Test getting series rules with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_code = get_test_series_code(client)
        assert series_code is not None, "Could not find test series"

        try:
            rules = client.series_handle(series_code).rules()
            assert rules is not None
            # Rules structure varies by series
        except IfpaApiError as e:
            # Not all series have rules endpoints available
            if e.status_code == 404:
                pytest.skip(f"Series {series_code} rules not available")
            raise

    def test_series_stats(self, api_key: str) -> None:
        """Test getting series statistics with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_code = get_test_series_code(client)
        assert series_code is not None, "Could not find test series"

        try:
            stats = client.series_handle(series_code).stats()
            assert stats is not None
            # Stats structure varies by series
        except IfpaApiError as e:
            # Not all series have stats endpoints available, or may require additional parameters
            if e.status_code in [400, 404]:
                pytest.skip(f"Series {series_code} stats not available or requires region code")
            raise

    def test_series_schedule(self, api_key: str) -> None:
        """Test getting series schedule with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_code = get_test_series_code(client)
        assert series_code is not None, "Could not find test series"

        try:
            schedule = client.series_handle(series_code).schedule()
            assert schedule is not None
            # Schedule structure varies by series
        except IfpaApiError as e:
            # Not all series have schedule endpoints available
            if e.status_code == 404:
                pytest.skip(f"Series {series_code} schedule not available")
            raise

    def test_series_region_reps(self, api_key: str) -> None:
        """Test getting series region representatives with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_code = get_test_series_code(client)
        assert series_code is not None, "Could not find test series"

        try:
            reps = client.series_handle(series_code).region_reps()
            assert reps is not None
            # Region reps structure varies by series
        except IfpaApiError as e:
            # Not all series have region reps
            if e.status_code == 404:
                pytest.skip(f"Series {series_code} has no region reps")
            raise

    def test_series_invalid_code(self, api_key: str) -> None:
        """Test that invalid series code returns appropriate error."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        with pytest.raises(IfpaApiError) as exc_info:
            # Try to get overview which should fail for non-existent series
            client.series_handle("INVALID_CODE_XYZ").overview()

        # Should be either 404 (not found) or 400 (bad request)
        assert exc_info.value.status_code in [400, 404]
