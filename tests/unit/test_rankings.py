"""Unit tests for RankingsClient.

Tests the rankings resource client using mocked HTTP requests.
"""

import pytest
import requests_mock

from ifpa_api.client import IfpaClient
from ifpa_api.exceptions import IfpaApiError
from ifpa_api.models.rankings import (
    CountryRankingsResponse,
    CustomRankingsResponse,
    RankingsResponse,
)


class TestRankingsClientWPPR:
    """Test cases for WPPR rankings queries."""

    def test_wppr_basic(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting WPPR rankings without filters."""
        mock_requests.get(
            "https://api.ifpapinball.com/rankings/wppr",
            json={
                "rankings": [
                    {
                        "player_id": 1,
                        "current_rank": 1,
                        "name": "Top Player",
                        "rating_value": 1000.5,
                        "country_code": "US",
                    },
                    {
                        "player_id": 2,
                        "current_rank": 2,
                        "name": "Second Player",
                        "rating_value": 950.2,
                        "country_code": "CA",
                    },
                ],
                "total_results": 2,
                "ranking_system": "Main",
            },
        )

        client = IfpaClient(api_key="test-key")
        rankings = client.rankings.wppr()

        assert isinstance(rankings, RankingsResponse)
        assert len(rankings.rankings) == 2
        assert rankings.rankings[0].rank == 1
        assert rankings.rankings[0].player_name == "Top Player"
        assert rankings.rankings[0].rating == 1000.5

    def test_wppr_with_pagination(self, mock_requests: requests_mock.Mocker) -> None:
        """Test WPPR rankings with pagination parameters."""
        mock_requests.get(
            "https://api.ifpapinball.com/rankings/wppr",
            json={
                "rankings": [
                    {"player_id": i, "current_rank": i, "name": f"Player {i}"}
                    for i in range(1, 101)
                ],
                "total_results": 5000,
            },
        )

        client = IfpaClient(api_key="test-key")
        rankings = client.rankings.wppr(start_pos=0, count=100)

        assert len(rankings.rankings) == 100
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "start_pos=0" in query
        assert "count=100" in query

    def test_wppr_with_country_filter(self, mock_requests: requests_mock.Mocker) -> None:
        """Test WPPR rankings filtered by country."""
        mock_requests.get(
            "https://api.ifpapinball.com/rankings/wppr",
            json={
                "rankings": [
                    {
                        "player_id": 100,
                        "current_rank": 1,
                        "name": "US Player",
                        "country_code": "US",
                    }
                ],
                "total_results": 1,
            },
        )

        client = IfpaClient(api_key="test-key")
        rankings = client.rankings.wppr(country="US")

        assert len(rankings.rankings) == 1
        assert mock_requests.last_request is not None
        assert "country=us" in mock_requests.last_request.query

    def test_wppr_with_region_filter(self, mock_requests: requests_mock.Mocker) -> None:
        """Test WPPR rankings filtered by region."""
        mock_requests.get(
            "https://api.ifpapinball.com/rankings/wppr",
            json={
                "rankings": [
                    {
                        "player_id": 200,
                        "current_rank": 1,
                        "name": "Regional Player",
                    }
                ],
                "total_results": 1,
            },
        )

        client = IfpaClient(api_key="test-key")
        rankings = client.rankings.wppr(region="northwest")

        assert len(rankings.rankings) == 1
        assert mock_requests.last_request is not None
        assert "region=northwest" in mock_requests.last_request.query


class TestRankingsClientSpecialSystems:
    """Test cases for specialized ranking systems."""

    def test_women_rankings(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting women's rankings."""
        mock_requests.get(
            "https://api.ifpapinball.com/rankings/women/open",
            json={
                "rankings": [
                    {
                        "player_id": 1001,
                        "current_rank": 1,
                        "name": "Top Woman Player",
                        "rating_value": 800.5,
                        "country_code": "US",
                    }
                ],
                "total_results": 1,
                "ranking_system": "Women",
            },
        )

        client = IfpaClient(api_key="test-key")
        rankings = client.rankings.women()

        assert isinstance(rankings, RankingsResponse)
        assert len(rankings.rankings) == 1
        assert rankings.ranking_system == "Women"
        assert mock_requests.last_request is not None
        assert "women/open" in mock_requests.last_request.path

    def test_women_rankings_with_filters(self, mock_requests: requests_mock.Mocker) -> None:
        """Test women's rankings with pagination and country filter."""
        mock_requests.get(
            "https://api.ifpapinball.com/rankings/women/women",
            json={
                "rankings": [{"player_id": i, "current_rank": i} for i in range(1, 26)],
                "total_results": 500,
            },
        )

        client = IfpaClient(api_key="test-key")
        rankings = client.rankings.women(
            tournament_type="WOMEN", start_pos=0, count=25, country="US"
        )

        assert len(rankings.rankings) == 25
        assert mock_requests.last_request is not None
        assert "women/women" in mock_requests.last_request.path
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "start_pos=0" in query
        assert "count=25" in query
        assert "country=us" in query

    def test_youth_rankings(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting youth rankings."""
        mock_requests.get(
            "https://api.ifpapinball.com/rankings/youth",
            json={
                "rankings": [
                    {
                        "player_id": 2001,
                        "current_rank": 1,
                        "name": "Top Youth Player",
                        "age": 16,
                    }
                ],
                "total_results": 1,
                "ranking_system": "Youth",
            },
        )

        client = IfpaClient(api_key="test-key")
        rankings = client.rankings.youth()

        assert len(rankings.rankings) == 1
        assert rankings.ranking_system == "Youth"

    def test_virtual_rankings(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting virtual tournament rankings."""
        mock_requests.get(
            "https://api.ifpapinball.com/rankings/virtual",
            json={
                "rankings": [
                    {
                        "player_id": 3001,
                        "current_rank": 1,
                        "name": "Top Virtual Player",
                    }
                ],
                "total_results": 1,
                "ranking_system": "Virtual",
            },
        )

        client = IfpaClient(api_key="test-key")
        rankings = client.rankings.virtual()

        assert len(rankings.rankings) == 1

    def test_pro_rankings(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting professional circuit rankings."""
        mock_requests.get(
            "https://api.ifpapinball.com/rankings/pro/open",
            json={
                "rankings": [
                    {
                        "player_id": 4001,
                        "current_rank": 1,
                        "name": "Top Pro Player",
                        "rating_value": 1200.0,
                    }
                ],
                "total_results": 1,
                "ranking_system": "Pro",
            },
        )

        client = IfpaClient(api_key="test-key")
        rankings = client.rankings.pro(start_pos=0, count=50)

        assert len(rankings.rankings) == 1
        assert mock_requests.last_request is not None
        assert "pro/open" in mock_requests.last_request.path
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "start_pos=0" in query
        assert "count=50" in query

    def test_pro_rankings_women_division(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting professional circuit women's division rankings."""
        mock_requests.get(
            "https://api.ifpapinball.com/rankings/pro/women",
            json={
                "rankings": [
                    {
                        "player_id": 4002,
                        "current_rank": 1,
                        "name": "Top Women Pro Player",
                        "rating_value": 1100.0,
                    }
                ],
                "total_results": 1,
                "ranking_system": "Pro",
            },
        )

        client = IfpaClient(api_key="test-key")
        rankings = client.rankings.pro(ranking_system="WOMEN")

        assert len(rankings.rankings) == 1
        assert mock_requests.last_request is not None
        assert "pro/women" in mock_requests.last_request.path


class TestRankingsClientCountryAndCustom:
    """Test cases for country and custom rankings."""

    def test_by_country(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting country rankings."""
        mock_requests.get(
            "https://api.ifpapinball.com/rankings/country",
            json={
                "rankings": [
                    {
                        "current_rank": 1,
                        "player_id": 1,
                        "name": "Top US Player",
                        "country_code": "US",
                        "country_name": "United States",
                        "rating_value": 1000.0,
                    },
                    {
                        "current_rank": 2,
                        "player_id": 2,
                        "name": "Second US Player",
                        "country_code": "US",
                        "country_name": "United States",
                        "rating_value": 950.0,
                    },
                ],
                "total_count": 10000,
            },
        )

        client = IfpaClient(api_key="test-key")
        rankings = client.rankings.by_country(country="US")

        assert isinstance(rankings, CountryRankingsResponse)
        assert len(rankings.rankings) == 2
        assert rankings.rankings[0].rank == 1
        assert rankings.rankings[0].player_name == "Top US Player"
        assert rankings.rankings[0].country_code == "US"
        assert rankings.total_count == 10000
        # Verify country parameter was passed
        assert mock_requests.last_request is not None
        assert "country=" in mock_requests.last_request.query

    def test_by_country_with_pagination(self, mock_requests: requests_mock.Mocker) -> None:
        """Test country rankings with pagination."""
        mock_requests.get(
            "https://api.ifpapinball.com/rankings/country",
            json={
                "rankings": [
                    {
                        "current_rank": i,
                        "player_id": i,
                        "name": f"Player {i}",
                        "country_code": "US",
                        "country_name": "United States",
                        "rating_value": 1000.0 - i,
                    }
                    for i in range(1, 26)
                ],
                "total_count": 10000,
            },
        )

        client = IfpaClient(api_key="test-key")
        rankings = client.rankings.by_country(country="US", start_pos=0, count=25)

        assert len(rankings.rankings) == 25
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "country=" in query
        assert "start_pos=0" in query
        assert "count=25" in query

    def test_custom_rankings(self, mock_requests: requests_mock.Mocker) -> None:
        """Test custom ranking system."""
        mock_requests.get(
            "https://api.ifpapinball.com/rankings/custom/regional-2024",
            json={
                "custom_view": [
                    {
                        "rank": 1,
                        "player_id": 6001,
                        "player_name": "Regional Champion",
                        "value": 500.0,
                        "details": {"region": "Northwest", "tournaments": 10},
                    }
                ],
                "title": "Regional Rankings 2024",
                "description": "Rankings for regional circuit 2024",
            },
        )

        client = IfpaClient(api_key="test-key")
        rankings = client.rankings.custom("regional-2024")

        assert isinstance(rankings, CustomRankingsResponse)
        assert len(rankings.rankings) == 1
        assert rankings.ranking_name == "Regional Rankings 2024"
        assert rankings.rankings[0].rank == 1
        assert rankings.rankings[0].value == 500.0

    def test_custom_rankings_with_numeric_id(self, mock_requests: requests_mock.Mocker) -> None:
        """Test custom rankings with numeric ID."""
        mock_requests.get(
            "https://api.ifpapinball.com/rankings/custom/123",
            json={
                "custom_view": [],
                "title": "Custom Ranking 123",
            },
        )

        client = IfpaClient(api_key="test-key")
        rankings = client.rankings.custom(123)

        assert isinstance(rankings, CustomRankingsResponse)
        assert mock_requests.last_request is not None
        assert "custom/123" in mock_requests.last_request.path


class TestRankingsClientErrors:
    """Test error handling for rankings client."""

    def test_wppr_handles_api_error(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that rankings properly handles API errors."""
        mock_requests.get(
            "https://api.ifpapinball.com/rankings/wppr",
            status_code=503,
            json={"error": "Service temporarily unavailable"},
        )

        client = IfpaClient(api_key="test-key")
        with pytest.raises(IfpaApiError) as exc_info:
            client.rankings.wppr()

        assert exc_info.value.status_code == 503

    def test_custom_rankings_handles_404(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that custom rankings handles not found."""
        mock_requests.get(
            "https://api.ifpapinball.com/rankings/custom/nonexistent",
            status_code=404,
            json={"error": "Custom ranking not found"},
        )

        client = IfpaClient(api_key="test-key")
        with pytest.raises(IfpaApiError) as exc_info:
            client.rankings.custom("nonexistent")

        assert exc_info.value.status_code == 404


class TestRankingsClientFieldMappings:
    """Test that field aliases and mappings work correctly."""

    def test_ranking_entry_field_aliases(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that RankingEntry properly maps aliased fields."""
        mock_requests.get(
            "https://api.ifpapinball.com/rankings/wppr",
            json={
                "rankings": [
                    {
                        "player_id": 1,
                        "current_rank": 5,  # Should map to 'rank'
                        "name": "Test Player",  # Should map to 'player_name'
                        "rating_value": 750.5,  # Should map to 'rating'
                        "event_count": 12,  # Should map to 'active_events'
                        "efficiency_percent": 85.5,  # Should map to 'efficiency_value'
                    }
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        rankings = client.rankings.wppr()

        entry = rankings.rankings[0]
        assert entry.rank == 5
        assert entry.player_name == "Test Player"
        assert entry.rating == 750.5
        assert entry.active_events == 12
        assert entry.efficiency_value == 85.5

    def test_country_rankings_field_alias(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that CountryRankingsResponse maps 'rankings' to 'country_rankings'."""
        mock_requests.get(
            "https://api.ifpapinball.com/rankings/country",
            json={
                "rankings": [  # API returns 'rankings'
                    {
                        "current_rank": 1,
                        "player_id": 1,
                        "name": "Top US Player",
                        "country_code": "US",
                        "country_name": "United States",
                        "rating_value": 1000.0,
                    }
                ]
            },
        )

        client = IfpaClient(api_key="test-key")
        rankings = client.rankings.by_country(country="US")

        # Should be accessible via 'rankings'
        assert len(rankings.rankings) == 1
        assert rankings.rankings[0].country_code == "US"
