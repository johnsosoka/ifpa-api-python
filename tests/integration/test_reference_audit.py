"""Integration tests for Reference/Other resource audit.

This module tests the /other/countries and /other/stateprovs endpoints
to document their complete API response structures for implementing
a ReferenceClient.
"""

import os
from typing import Any, cast

import pytest
import requests


@pytest.fixture
def api_key() -> str:
    """Get API key from environment or credentials file."""
    # Try environment variable first
    api_key = os.environ.get("IFPA_API_KEY")
    if api_key:
        return api_key

    # Try credentials file
    credentials_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "credentials"
    )
    if os.path.exists(credentials_path):
        with open(credentials_path) as f:
            for line in f:
                if line.startswith("IFPA_API_KEY="):
                    return line.strip().split("=", 1)[1]

    pytest.skip("No API key available for testing")
    return ""  # Never reached, but satisfies mypy


@pytest.fixture
def base_url() -> str:
    """Get base URL for IFPA API."""
    return "https://api.ifpapinball.com"


@pytest.mark.integration
class TestCountriesEndpoint:
    """Test suite for /other/countries endpoint."""

    def test_countries_endpoint_exists(self, api_key: str, base_url: str) -> None:
        """Test that /countries endpoint exists and responds."""
        response = requests.get(
            f"{base_url}/countries",
            headers={"X-API-Key": api_key},
            timeout=10.0,
        )

        # Document HTTP status
        print(f"\n✓ Status Code: {response.status_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_countries_without_api_key(self, base_url: str) -> None:
        """Test that endpoint returns 401 without API key."""
        response = requests.get(
            f"{base_url}/countries",
            timeout=10.0,
        )

        print(f"\n✓ Status Code (no key): {response.status_code}")
        assert response.status_code == 401, "Expected 401 without API key"

    def test_countries_response_structure(self, api_key: str, base_url: str) -> None:
        """Test and document complete response structure."""
        response = requests.get(
            f"{base_url}/countries",
            headers={"X-API-Key": api_key},
            timeout=10.0,
        )

        assert response.status_code == 200
        data = response.json()

        # Document top-level structure
        print(f"\n✓ Response type: {type(data)}")
        print(f"✓ Top-level keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")

        # If it's a list, examine first few items
        if isinstance(data, list):
            print(f"✓ Total countries: {len(data)}")
            if len(data) > 0:
                print("\n✓ Sample record (first):")
                self._print_record(data[0])
                print("\n✓ Sample record (middle):")
                self._print_record(data[len(data) // 2])
                print("\n✓ Sample record (last):")
                self._print_record(data[-1])

        # If it's a dict with nested data, examine structure
        if isinstance(data, dict):
            # Check for common wrapper keys
            for key in ["countries", "data", "results", "search"]:
                if key in data:
                    print(f"\n✓ Found wrapper key: '{key}'")
                    nested_data = data[key]
                    if isinstance(nested_data, list) and len(nested_data) > 0:
                        print(f"✓ Records in '{key}': {len(nested_data)}")
                        print(f"\n✓ Sample record from '{key}':")
                        self._print_record(nested_data[0])

    def test_countries_query_parameters(self, api_key: str, base_url: str) -> None:
        """Test if endpoint accepts any query parameters."""
        # Test common parameter names
        test_params = [
            {"active": "true"},
            {"country": "US"},
            {"start_pos": 0},
            {"count": 10},
        ]

        for params_dict in test_params:
            response = requests.get(
                f"{base_url}/countries",
                headers={"X-API-Key": api_key},
                params=cast(dict[str, Any], params_dict) if params_dict else None,
                timeout=10.0,
            )
            print(f"\n✓ Params {params_dict}: Status {response.status_code}")

    def test_countries_sorting(self, api_key: str, base_url: str) -> None:
        """Test if countries are sorted and by what field."""
        response = requests.get(
            f"{base_url}/countries",
            headers={"X-API-Key": api_key},
            timeout=10.0,
        )

        assert response.status_code == 200
        data = response.json()

        # Determine if it's a list or dict wrapper
        countries = data if isinstance(data, list) else data.get("countries", data.get("data", []))

        if isinstance(countries, list) and len(countries) > 3:
            # Check first few records for sorting
            print("\n✓ First 5 countries (checking sort order):")
            for i, country in enumerate(countries[:5]):
                print(f"  {i+1}. {country}")

    @staticmethod
    def _print_record(record: Any) -> None:
        """Helper to print a record's structure."""
        if isinstance(record, dict):
            for key, value in record.items():
                value_type = type(value).__name__
                # Truncate long strings
                display_value = str(value)[:50] if isinstance(value, str) else value
                print(f"    {key}: {display_value} (type: {value_type})")
        else:
            print(f"    {record} (type: {type(record).__name__})")


@pytest.mark.integration
class TestStateProvsEndpoint:
    """Test suite for /other/stateprovs endpoint."""

    def test_stateprovs_endpoint_exists(self, api_key: str, base_url: str) -> None:
        """Test that /stateprovs endpoint exists and responds."""
        response = requests.get(
            f"{base_url}/stateprovs",
            headers={"X-API-Key": api_key},
            timeout=10.0,
        )

        # Document HTTP status
        print(f"\n✓ Status Code: {response.status_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_stateprovs_without_api_key(self, base_url: str) -> None:
        """Test that endpoint returns 401 without API key."""
        response = requests.get(
            f"{base_url}/stateprovs",
            timeout=10.0,
        )

        print(f"\n✓ Status Code (no key): {response.status_code}")
        assert response.status_code == 401, "Expected 401 without API key"

    def test_stateprovs_response_structure(self, api_key: str, base_url: str) -> None:
        """Test and document complete response structure."""
        response = requests.get(
            f"{base_url}/stateprovs",
            headers={"X-API-Key": api_key},
            timeout=10.0,
        )

        assert response.status_code == 200
        data = response.json()

        # Document top-level structure
        print(f"\n✓ Response type: {type(data)}")
        print(f"✓ Top-level keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")

        # If it's a list, examine first few items
        if isinstance(data, list):
            print(f"✓ Total state/provs: {len(data)}")
            if len(data) > 0:
                print("\n✓ Sample record (first):")
                self._print_record(data[0])
                print("\n✓ Sample record (middle):")
                self._print_record(data[len(data) // 2])
                print("\n✓ Sample record (last):")
                self._print_record(data[-1])

        # If it's a dict with nested data, examine structure
        if isinstance(data, dict):
            # Check for common wrapper keys
            for key in ["stateprovs", "states", "data", "results", "search"]:
                if key in data:
                    print(f"\n✓ Found wrapper key: '{key}'")
                    nested_data = data[key]
                    if isinstance(nested_data, list) and len(nested_data) > 0:
                        print(f"✓ Records in '{key}': {len(nested_data)}")
                        print(f"\n✓ Sample record from '{key}':")
                        self._print_record(nested_data[0])

    def test_stateprovs_query_parameters(self, api_key: str, base_url: str) -> None:
        """Test if endpoint accepts any query parameters."""
        # Test common parameter names
        test_params = [
            {"country": "US"},
            {"active": "true"},
            {"start_pos": 0},
            {"count": 10},
        ]

        for params_dict in test_params:
            response = requests.get(
                f"{base_url}/stateprovs",
                headers={"X-API-Key": api_key},
                params=cast(dict[str, Any], params_dict) if params_dict else None,
                timeout=10.0,
            )
            print(f"\n✓ Params {params_dict}: Status {response.status_code}")

    def test_stateprovs_country_relationship(self, api_key: str, base_url: str) -> None:
        """Test if state/provs include country information."""
        response = requests.get(
            f"{base_url}/stateprovs",
            headers={"X-API-Key": api_key},
            timeout=10.0,
        )

        assert response.status_code == 200
        data = response.json()

        # Determine if it's a list or dict wrapper
        stateprovs = (
            data if isinstance(data, list) else data.get("stateprovs", data.get("data", []))
        )

        if isinstance(stateprovs, list) and len(stateprovs) > 0:
            # Check if records include country field
            sample = stateprovs[0]
            print("\n✓ Sample state/prov record:")
            self._print_record(sample)

            # Check for country-related fields
            if isinstance(sample, dict):
                country_fields = [k for k in sample if "country" in k.lower()]
                if country_fields:
                    print(f"\n✓ Country-related fields found: {country_fields}")

    def test_stateprovs_sorting(self, api_key: str, base_url: str) -> None:
        """Test if state/provs are sorted and by what field."""
        response = requests.get(
            f"{base_url}/stateprovs",
            headers={"X-API-Key": api_key},
            timeout=10.0,
        )

        assert response.status_code == 200
        data = response.json()

        # Determine if it's a list or dict wrapper
        stateprovs = (
            data if isinstance(data, list) else data.get("stateprovs", data.get("data", []))
        )

        if isinstance(stateprovs, list) and len(stateprovs) > 3:
            # Check first few records for sorting
            print("\n✓ First 10 state/provs (checking sort order):")
            for i, stateprov in enumerate(stateprovs[:10]):
                print(f"  {i+1}. {stateprov}")

    @staticmethod
    def _print_record(record: Any) -> None:
        """Helper to print a record's structure."""
        if isinstance(record, dict):
            for key, value in record.items():
                value_type = type(value).__name__
                # Truncate long strings
                display_value = str(value)[:50] if isinstance(value, str) else value
                print(f"    {key}: {display_value} (type: {value_type})")
        else:
            print(f"    {record} (type: {type(record).__name__})")


@pytest.mark.integration
class TestReferenceDataUseCases:
    """Test use cases for reference data."""

    def test_countries_for_rankings_filter(self, api_key: str, base_url: str) -> None:
        """Test using countries data for rankings filter validation."""
        # Get countries
        countries_response = requests.get(
            f"{base_url}/countries",
            headers={"X-API-Key": api_key},
            timeout=10.0,
        )
        assert countries_response.status_code == 200
        countries_data = countries_response.json()

        # Test if we can use this for rankings
        print("\n✓ Use Case: Countries for rankings filter")
        print(
            f"  Total countries available: "
            f"{len(countries_data) if isinstance(countries_data, list) else 'unknown'}"
        )

    def test_stateprovs_for_player_search(self, api_key: str, base_url: str) -> None:
        """Test using state/provs data for player search validation."""
        # Get state/provs
        stateprovs_response = requests.get(
            f"{base_url}/stateprovs",
            headers={"X-API-Key": api_key},
            timeout=10.0,
        )
        assert stateprovs_response.status_code == 200
        stateprovs_data = stateprovs_response.json()

        # Test if we can use this for player search
        print("\n✓ Use Case: State/Provs for player search filter")
        print(
            f"  Total state/provs available: "
            f"{len(stateprovs_data) if isinstance(stateprovs_data, list) else 'unknown'}"
        )
