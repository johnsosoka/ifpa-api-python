"""Models for IFPA Reference data (countries, states/provinces)."""

from pydantic import Field

from ifpa_api.models.common import IfpaBaseModel


class Country(IfpaBaseModel):
    """A country in the IFPA system.

    Attributes:
        country_id: Unique country identifier
        country_name: Full country name (e.g., "United States")
        country_code: ISO country code (e.g., "US")
        active_flag: Whether country is active ("Y" or "N")
    """

    country_id: int
    country_name: str
    country_code: str
    active_flag: str


class CountryListResponse(IfpaBaseModel):
    """Response from GET /countries endpoint.

    Attributes:
        country: List of all countries in the IFPA system (typically 62)
    """

    country: list[Country] = Field(default_factory=list)


class Region(IfpaBaseModel):
    """A state or province within a country.

    Attributes:
        region_name: Full region name (e.g., "California", "Ontario")
        region_code: Region code abbreviation (e.g., "CA", "ON")
    """

    region_name: str
    region_code: str


class CountryRegions(IfpaBaseModel):
    """Country with its regions/states/provinces.

    Attributes:
        country_id: Unique country identifier
        country_name: Full country name
        country_code: ISO country code
        regions: List of regions/states/provinces in this country
    """

    country_id: int
    country_name: str
    country_code: str
    regions: list[Region] = Field(default_factory=list)


class StateProvListResponse(IfpaBaseModel):
    """Response from GET /stateprovs endpoint.

    Attributes:
        stateprov: List of countries with their regions (typically 3 countries: AU, CA, US
            with 67 total regions)
    """

    stateprov: list[CountryRegions] = Field(default_factory=list)
