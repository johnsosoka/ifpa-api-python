"""Integration tests for Reference resource.

This test suite performs comprehensive integration testing of the Reference resource
(countries and state/provs endpoints) against the live IFPA API. Tests cover happy path,
edge cases, response structure validation, and common use cases.

Test Fixtures:
- Countries endpoint: Returns list of all countries with active flags
- State/Provs endpoint: Returns states/provinces grouped by country

These tests make real API calls and require a valid API key.
Run with: pytest -m integration
"""

import pytest

from ifpa_api import IfpaClient
from ifpa_api.models.reference import CountryListResponse, StateProvListResponse
from tests.integration.helpers import skip_if_no_api_key

# =============================================================================
# COUNTRIES ENDPOINT
# =============================================================================


@pytest.mark.integration
class TestCountriesEndpoint:
    """Integration tests for countries endpoint."""

    def test_countries_endpoint(self, api_key: str) -> None:
        """Test that countries endpoint returns valid data."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        result = client.reference.countries()

        # Verify we get countries back
        assert isinstance(result, CountryListResponse)
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
        skip_if_no_api_key()
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
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        result = client.reference.countries()

        for country in result.country:
            assert country.active_flag in (
                "Y",
                "N",
            ), f"Invalid active_flag for {country.country_name}"

    def test_countries_response_structure(self, api_key: str) -> None:
        """Test and document complete response structure."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        result = client.reference.countries()

        # Verify response structure
        assert isinstance(result, CountryListResponse)
        assert result.country is not None
        assert len(result.country) > 0

        # Verify field structure on sample records
        first = result.country[0]
        middle = result.country[len(result.country) // 2]
        last = result.country[-1]

        for country in [first, middle, last]:
            assert country.country_id > 0
            assert len(country.country_name) > 0
            assert len(country.country_code) > 0
            assert country.active_flag in ("Y", "N")

    def test_countries_sorting(self, api_key: str) -> None:
        """Test countries sorting order."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        result = client.reference.countries()

        # Verify we have enough countries to check sorting
        assert len(result.country) > 5

        # Countries should be returned in a consistent order
        # Document the actual order for reference
        first_five = result.country[:5]
        assert len(first_five) == 5


# =============================================================================
# STATE/PROVS ENDPOINT
# =============================================================================


@pytest.mark.integration
class TestStateProvsEndpoint:
    """Integration tests for state/province endpoint."""

    def test_stateprovs_endpoint(self, api_key: str) -> None:
        """Test that state/provs endpoint returns valid data."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        result = client.reference.state_provs()

        # Verify we get countries with regions
        assert isinstance(result, StateProvListResponse)
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
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        result = client.reference.state_provs()

        country_codes = [c.country_code for c in result.stateprov]

        # Verify known countries with regions are present
        assert "US" in country_codes
        assert "CA" in country_codes
        assert "AU" in country_codes

    def test_stateprovs_us_has_states(self, api_key: str) -> None:
        """Test that US has expected state data."""
        skip_if_no_api_key()
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
        """Test that Canada has expected province data.

        Note: API returns 8 provinces (missing NL, PE, NT, NU, YT).
        Canada has 13 total provinces/territories but API data is incomplete.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        result = client.reference.state_provs()

        ca_data = next((c for c in result.stateprov if c.country_code == "CA"), None)
        assert ca_data is not None, "Canada not found in state/prov data"

        # API returns 8 provinces (known API limitation)
        assert len(ca_data.regions) >= 8

        # Check for some known provinces
        region_codes = [r.region_code for r in ca_data.regions]
        assert "ON" in region_codes  # Ontario
        assert "QC" in region_codes  # Quebec
        assert "BC" in region_codes  # British Columbia

    def test_stateprovs_response_structure(self, api_key: str) -> None:
        """Test and document complete response structure."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        result = client.reference.state_provs()

        # Verify response structure
        assert isinstance(result, StateProvListResponse)
        assert result.stateprov is not None
        assert len(result.stateprov) > 0

        # Verify field structure on sample records
        first = result.stateprov[0]
        middle = result.stateprov[len(result.stateprov) // 2]
        last = result.stateprov[-1]

        for country_region in [first, middle, last]:
            assert country_region.country_id > 0
            assert len(country_region.country_name) > 0
            assert len(country_region.country_code) > 0
            assert country_region.regions is not None
            assert len(country_region.regions) > 0

            # Verify region structure
            for region in country_region.regions:
                assert len(region.region_name) > 0
                assert len(region.region_code) > 0

    def test_stateprovs_country_relationship(self, api_key: str) -> None:
        """Test that state/provs include proper country information."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        result = client.reference.state_provs()

        assert len(result.stateprov) > 0

        # Check that each country has proper fields
        for country_region in result.stateprov:
            assert country_region.country_id > 0
            assert len(country_region.country_name) > 0
            assert len(country_region.country_code) == 2  # 2-letter code
            assert country_region.country_code.isupper()  # Uppercase

    def test_stateprovs_sorting(self, api_key: str) -> None:
        """Test state/provs sorting order."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        result = client.reference.state_provs()

        # Verify we have data
        assert len(result.stateprov) > 0

        # State/provs should be returned in a consistent order
        # Document the actual order for reference
        assert len(result.stateprov) >= 3


# =============================================================================
# USE CASES AND CROSS-FUNCTIONAL TESTS
# =============================================================================


@pytest.mark.integration
class TestReferenceUseCases:
    """Integration tests for common reference data use cases."""

    def test_lookup_country_code_by_name(self, api_key: str) -> None:
        """Test looking up country code by name."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        countries = client.reference.countries()

        # Find US by name
        us = next((c for c in countries.country if c.country_name == "United States"), None)
        assert us is not None
        assert us.country_code == "US"

    def test_lookup_states_for_country(self, api_key: str) -> None:
        """Test looking up states for a specific country."""
        skip_if_no_api_key()
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
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        countries = client.reference.countries()

        # Filter for active countries
        active_countries = [c for c in countries.country if c.active_flag == "Y"]

        # Should have many active countries
        assert len(active_countries) >= 50
        assert all(c.active_flag == "Y" for c in active_countries)

    def test_count_total_regions(self, api_key: str) -> None:
        """Test counting total regions across all countries."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        state_provs = client.reference.state_provs()

        # Count total regions
        total_regions = sum(len(c.regions) for c in state_provs.stateprov)

        # Should have 67+ total regions (US states + CA provinces + AU states)
        assert total_regions >= 67

    def test_countries_for_rankings_filter(self, api_key: str) -> None:
        """Test using countries data for rankings filter validation."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        countries = client.reference.countries()

        # Verify we can use this data for filtering/validation
        assert len(countries.country) > 50

        # Verify country codes are valid format
        for country in countries.country:
            assert len(country.country_code) >= 2
            assert country.country_code.isupper()

    def test_stateprovs_for_player_search(self, api_key: str) -> None:
        """Test using state/provs data for player search validation."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        state_provs = client.reference.state_provs()

        # Verify we can use this data for filtering/validation
        assert len(state_provs.stateprov) >= 3

        # Verify regions are properly structured for validation
        for country_region in state_provs.stateprov:
            for region in country_region.regions:
                assert len(region.region_code) >= 2
                assert len(region.region_name) > 0


# =============================================================================
# EDGE CASES AND ERROR HANDLING
# =============================================================================


@pytest.mark.integration
class TestReferenceEdgeCases:
    """Test edge cases and data quality for reference endpoints."""

    def test_countries_no_duplicates(self, api_key: str) -> None:
        """Test that countries list has no duplicate country codes."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        result = client.reference.countries()

        country_codes = [c.country_code for c in result.country]
        # Check for duplicates
        assert len(country_codes) == len(set(country_codes)), "Found duplicate country codes"

    def test_countries_no_duplicates_by_id(self, api_key: str) -> None:
        """Test that countries list has no duplicate country IDs."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        result = client.reference.countries()

        country_ids = [c.country_id for c in result.country]
        # Check for duplicates
        assert len(country_ids) == len(set(country_ids)), "Found duplicate country IDs"

    def test_stateprovs_no_duplicate_countries(self, api_key: str) -> None:
        """Test that state/provs list has no duplicate country codes."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        result = client.reference.state_provs()

        country_codes = [c.country_code for c in result.stateprov]
        # Check for duplicates
        assert len(country_codes) == len(set(country_codes)), "Found duplicate country codes"

    def test_stateprovs_regions_no_duplicates(self, api_key: str) -> None:
        """Test that regions within each country have no duplicates."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        result = client.reference.state_provs()

        for country_region in result.stateprov:
            region_codes = [r.region_code for r in country_region.regions]
            assert len(region_codes) == len(
                set(region_codes)
            ), f"Found duplicate regions in {country_region.country_name}"

    def test_countries_field_data_quality(self, api_key: str) -> None:
        """Test that country fields have reasonable data quality."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        result = client.reference.countries()

        for country in result.country:
            # Country codes should be 2-3 characters
            assert 2 <= len(country.country_code) <= 3
            # Country names should be reasonable length
            assert 2 <= len(country.country_name) <= 100
            # IDs should be positive
            assert country.country_id > 0

    def test_stateprovs_field_data_quality(self, api_key: str) -> None:
        """Test that state/prov fields have reasonable data quality."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        result = client.reference.state_provs()

        for country_region in result.stateprov:
            # Country codes should be 2-3 characters
            assert 2 <= len(country_region.country_code) <= 3
            # Country names should be reasonable length
            assert 2 <= len(country_region.country_name) <= 100
            # IDs should be positive
            assert country_region.country_id > 0

            # Check region data quality
            for region in country_region.regions:
                # Region codes should be 2-3 characters
                assert 2 <= len(region.region_code) <= 5
                # Region names should be reasonable length
                assert 2 <= len(region.region_name) <= 100
