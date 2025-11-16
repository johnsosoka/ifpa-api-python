"""Unit tests for ReferenceClient."""

import requests_mock

from ifpa_api import IfpaClient


def test_countries() -> None:
    """Test countries() method returns country list."""
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.ifpapinball.com/countries",
            json={
                "country": [
                    {
                        "country_id": 1,
                        "country_name": "United States",
                        "country_code": "US",
                        "active_flag": "Y",
                    },
                    {
                        "country_id": 2,
                        "country_name": "Canada",
                        "country_code": "CA",
                        "active_flag": "Y",
                    },
                ]
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.reference.countries()

        assert len(result.country) == 2
        assert result.country[0].country_name == "United States"
        assert result.country[0].country_code == "US"
        assert result.country[1].country_name == "Canada"


def test_state_provs() -> None:
    """Test state_provs() method returns regions by country."""
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.ifpapinball.com/stateprovs",
            json={
                "stateprov": [
                    {
                        "country_id": 1,
                        "country_name": "United States",
                        "country_code": "US",
                        "regions": [
                            {"region_name": "California", "region_code": "CA"},
                            {"region_name": "New York", "region_code": "NY"},
                        ],
                    },
                    {
                        "country_id": 2,
                        "country_name": "Canada",
                        "country_code": "CA",
                        "regions": [
                            {"region_name": "Ontario", "region_code": "ON"},
                            {"region_name": "Quebec", "region_code": "QC"},
                        ],
                    },
                ]
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.reference.state_provs()

        assert len(result.stateprov) == 2
        assert result.stateprov[0].country_code == "US"
        assert len(result.stateprov[0].regions) == 2
        assert result.stateprov[0].regions[0].region_name == "California"
        assert result.stateprov[1].country_code == "CA"
        assert len(result.stateprov[1].regions) == 2
