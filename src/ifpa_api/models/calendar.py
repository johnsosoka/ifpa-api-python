"""Calendar-related Pydantic models.

Models for calendar events and schedules (if supported by API).
"""

from pydantic import Field

from ifpa_api.models.common import IfpaBaseModel


class CalendarEvent(IfpaBaseModel):
    """Calendar event information.

    Attributes:
        event_id: Unique event identifier
        event_name: Event name
        event_date: Date of the event
        event_start_date: Start date (for multi-day events)
        event_end_date: End date (for multi-day events)
        location_name: Venue name
        city: City location
        stateprov: State or province
        country_code: ISO country code
        country_name: Full country name
        website: Event website URL
        contact_info: Contact information
        description: Event description
        status: Event status (scheduled, completed, cancelled)
    """

    event_id: int | None = None
    event_name: str
    event_date: str | None = None
    event_start_date: str | None = None
    event_end_date: str | None = None
    location_name: str | None = None
    city: str | None = None
    stateprov: str | None = None
    country_code: str | None = None
    country_name: str | None = None
    website: str | None = None
    contact_info: str | None = None
    description: str | None = None
    status: str | None = None


class CalendarResponse(IfpaBaseModel):
    """Response for calendar queries.

    Attributes:
        events: List of calendar events
        total_events: Total number of events
        period_start: Start of the period covered
        period_end: End of the period covered
    """

    events: list[CalendarEvent] = Field(default_factory=list)
    total_events: int | None = None
    period_start: str | None = None
    period_end: str | None = None
