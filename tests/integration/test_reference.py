"""Integration tests for ReferenceClient.

These tests make real API calls to verify the ReferenceClient works correctly
with the live IFPA API.
"""

import pytest

from ifpa_api import IfpaClient


@pytest.mark.integration
class TestCountries:
    """Integration tests for countries endpoint."""

    def test_countries_endpoint(self, api_key: str) -> None:
        """Test that countries endpoint returns valid data."""
        client = IfpaClient(api_key=api_key)
        result = client.reference.countries()

        # Verify we get countries back
        assert len(result.country) > 0
        assert len(result.country) >= 62  # Known to return 62 countries

        # Verify structure of first country
        country = result.country[0]
        assert country.country_id > 0
        assert len(country.country_name) > 0
        assert len(country.country_code) > 0
        assert country.active_flag in ("Y", "N")

    def test_countries_includes_major_countries(self, api_key: str) -> None:
        """Test that response includes major pinball countries."""
        client = IfpaClient(api_key=api_key)
        result = client.reference.countries()

        country_codes = [c.country_code for c in result.country]
        country_names = [c.country_name for c in result.country]

        # Verify major pinball countries are present
        assert "US" in country_codes
        assert "CA" in country_codes
        assert "United States" in country_names
        assert "Canada" in country_names

    def test_countries_all_active_flags_valid(self, api_key: str) -> None:
        """Test that all countries have valid active flags."""
        client = IfpaClient(api_key=api_key)
        result = client.reference.countries()

        for country in result.country:
            assert country.active_flag in (
                "Y",
                "N",
            ), f"Invalid active_flag for {country.country_name}"


@pytest.mark.integration
class TestStateProvs:
    """Integration tests for state/province endpoint."""

    def test_stateprovs_endpoint(self, api_key: str) -> None:
        """Test that state/provs endpoint returns valid data."""
        client = IfpaClient(api_key=api_key)
        result = client.reference.state_provs()

        # Verify we get countries with regions
        assert len(result.stateprov) > 0
        assert len(result.stateprov) >= 3  # Known to return AU, CA, US

        # Verify structure of first country
        country_region = result.stateprov[0]
        assert country_region.country_id > 0
        assert len(country_region.country_name) > 0
        assert len(country_region.country_code) > 0
        assert len(country_region.regions) > 0

        # Verify region structure
        region = country_region.regions[0]
        assert len(region.region_name) > 0
        assert len(region.region_code) > 0

    def test_stateprovs_includes_expected_countries(self, api_key: str) -> None:
        """Test that response includes known countries with regions."""
        client = IfpaClient(api_key=api_key)
        result = client.reference.state_provs()

        country_codes = [c.country_code for c in result.stateprov]

        # Verify known countries with regions are present
        assert "US" in country_codes
        assert "CA" in country_codes
        assert "AU" in country_codes

    def test_stateprovs_us_has_states(self, api_key: str) -> None:
        """Test that US has expected state data."""
        client = IfpaClient(api_key=api_key)
        result = client.reference.state_provs()

        us_data = next((c for c in result.stateprov if c.country_code == "US"), None)
        assert us_data is not None, "US not found in state/prov data"

        # US should have 50+ states/territories
        assert len(us_data.regions) >= 50

        # Check for some known states
        region_codes = [r.region_code for r in us_data.regions]
        assert "CA" in region_codes  # California
        assert "NY" in region_codes  # New York
        assert "TX" in region_codes  # Texas

    def test_stateprovs_canada_has_provinces(self, api_key: str) -> None:
        """Test that Canada has expected province data."""
        client = IfpaClient(api_key=api_key)
        result = client.reference.state_provs()

        ca_data = next((c for c in result.stateprov if c.country_code == "CA"), None)
        assert ca_data is not None, "Canada not found in state/prov data"

        # Canada should have 10+ provinces/territories
        assert len(ca_data.regions) >= 10

        # Check for some known provinces
        region_codes = [r.region_code for r in ca_data.regions]
        assert "ON" in region_codes  # Ontario
        assert "QC" in region_codes  # Quebec
        assert "BC" in region_codes  # British Columbia


@pytest.mark.integration
class TestReferenceUseCases:
    """Integration tests for common reference data use cases."""

    def test_lookup_country_code_by_name(self, api_key: str) -> None:
        """Test looking up country code by name."""
        client = IfpaClient(api_key=api_key)
        countries = client.reference.countries()

        # Find US by name
        us = next((c for c in countries.country if c.country_name == "United States"), None)
        assert us is not None
        assert us.country_code == "US"

    def test_lookup_states_for_country(self, api_key: str) -> None:
        """Test looking up states for a specific country."""
        client = IfpaClient(api_key=api_key)
        state_provs = client.reference.state_provs()

        # Find US states
        us_regions = next((c for c in state_provs.stateprov if c.country_code == "US"), None)
        assert us_regions is not None

        # Get all state codes
        state_codes = [r.region_code for r in us_regions.regions]
        assert len(state_codes) >= 50

        # Verify codes are uppercase 2-letter codes
        for code in state_codes:
            assert len(code) == 2
            assert code.isupper()

    def test_get_all_active_countries(self, api_key: str) -> None:
        """Test filtering for active countries."""
        client = IfpaClient(api_key=api_key)
        countries = client.reference.countries()

        # Filter for active countries
        active_countries = [c for c in countries.country if c.active_flag == "Y"]

        # Should have many active countries
        assert len(active_countries) >= 50
        assert all(c.active_flag == "Y" for c in active_countries)

    def test_count_total_regions(self, api_key: str) -> None:
        """Test counting total regions across all countries."""
        client = IfpaClient(api_key=api_key)
        state_provs = client.reference.state_provs()

        # Count total regions
        total_regions = sum(len(c.regions) for c in state_provs.stateprov)

        # Should have 67+ total regions (US states + CA provinces + AU states)
        assert total_regions >= 67
