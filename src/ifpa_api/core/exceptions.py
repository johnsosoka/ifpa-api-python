"""Custom exceptions for the IFPA SDK.

This module defines the exception hierarchy for the SDK, providing clear error
messages and appropriate error information for different failure scenarios.
"""

from typing import Any


def format_validation_error(validation_error: Any) -> str:
    """Format Pydantic validation errors into user-friendly messages.

    Args:
        validation_error: Pydantic ValidationError or error details

    Returns:
        Formatted, human-readable error message with hints
    """
    # Handle Pydantic v2 ValidationError
    if hasattr(validation_error, "errors"):
        errors = validation_error.errors()

        messages = []
        for error in errors:
            field = error.get("loc", ["unknown"])[-1]  # Get last location part
            error_type = error.get("type", "unknown")
            msg = error.get("msg", "Validation failed")
            input_value = error.get("input", "N/A")

            # Create base message
            base_msg = f"Invalid parameter '{field}': {msg}"

            # Add type-specific hints
            hint = _get_validation_hint(field, error_type, input_value)
            if hint:
                base_msg += f"\nHint: {hint}"

            messages.append(base_msg)

        return "\n".join(messages)

    # Fallback for other formats
    return str(validation_error)


def _get_validation_hint(field: str, error_type: str, input_value: Any) -> str | None:
    """Get helpful hint for common validation errors.

    Args:
        field: Parameter name that failed validation
        error_type: Type of validation error
        input_value: The invalid input value

    Returns:
        Helpful hint string or None
    """
    # Type mismatch hints
    if error_type == "string_type":
        if field in ["country", "country_code"]:
            return "Country code should be a 2-letter string like 'US' or 'CA'"
        if field in ["state", "state_code"]:
            return "State code should be a 2-letter string like 'WA' or 'CA'"
        return f"Expected string, got {type(input_value).__name__}"

    if error_type == "int_type":
        return f"Expected integer, got {type(input_value).__name__}"

    # Value constraints
    if error_type in ["greater_than", "greater_than_equal"]:
        return "Value must be positive"

    # Missing required
    if error_type == "missing":
        return f"Parameter '{field}' is required"

    # Date format
    if error_type == "date_type" and field in ["start_date", "end_date"]:
        return "Date should be in YYYY-MM-DD format, e.g., '2024-01-15'"

    return None


class IfpaError(Exception):
    """Base exception for all IFPA SDK errors.

    All custom exceptions in the SDK inherit from this base class, making it
    easy to catch any SDK-related error.
    """


class MissingApiKeyError(IfpaError):
    """Raised when no API key is provided or available in environment.

    This error occurs during client initialization when:
    - No api_key is passed to the constructor
    - The IFPA_API_KEY environment variable is not set
    """


class IfpaApiError(IfpaError):
    """Raised when the IFPA API returns a non-2xx HTTP status code.

    This exception wraps HTTP errors from the API, providing access to the
    status code, error message, raw response body, and request context for debugging.

    Attributes:
        status_code: The HTTP status code returned by the API
        message: A human-readable error message
        response_body: The raw response body from the API (if available)
        request_url: The full URL that was requested
        request_params: The query parameters sent with the request
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: Any | None = None,
        request_url: str | None = None,
        request_params: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an API error.

        Args:
            message: A human-readable error message
            status_code: The HTTP status code from the API response
            response_body: The raw response body (typically dict or string)
            request_url: The full URL that was requested
            request_params: The query parameters sent with the request
        """
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.response_body = response_body
        self.request_url = request_url
        self.request_params = request_params

    def __str__(self) -> str:
        """Return a string representation of the error."""
        parts = []
        if self.status_code:
            parts.append(f"[{self.status_code}]")
        parts.append(self.message)
        if self.request_url:
            parts.append(f"(URL: {self.request_url})")
        return " ".join(parts)

    def __repr__(self) -> str:
        """Return a detailed representation of the error."""
        return (
            f"IfpaApiError(message={self.message!r}, "
            f"status_code={self.status_code!r}, "
            f"response_body={self.response_body!r}, "
            f"request_url={self.request_url!r}, "
            f"request_params={self.request_params!r})"
        )


class IfpaClientValidationError(IfpaError):
    """Raised when client-side request validation fails.

    This error occurs when validate_requests=True and Pydantic model validation
    fails for request parameters. It wraps the underlying Pydantic ValidationError
    to provide context about which SDK method call failed.

    Attributes:
        message: A human-readable error message describing the validation failure
        validation_errors: The underlying Pydantic validation error details
    """

    def __init__(self, message: str, validation_errors: Any | None = None) -> None:
        """Initialize a validation error.

        Args:
            message: A human-readable error message
            validation_errors: The underlying Pydantic ValidationError or error details
        """
        # Format the validation errors if provided
        if validation_errors:
            formatted = format_validation_error(validation_errors)
            message = f"{message}\n\n{formatted}"

        super().__init__(message)
        self.message = message
        self.validation_errors = validation_errors

    def __str__(self) -> str:
        """Return a string representation of the validation error."""
        return self.message  # Already formatted in __init__

    def __repr__(self) -> str:
        """Return a detailed representation of the validation error."""
        return (
            f"IfpaClientValidationError(message={self.message!r}, "
            f"validation_errors={self.validation_errors!r})"
        )


class PlayersNeverMetError(IfpaError):
    """Raised when requesting PVP data for players who have never competed together.

    This exception is raised by the client when the IFPA API returns a 404 error
    indicating that the two players have never faced each other in any tournament.
    This provides a clearer error message than a generic 404 response.

    Attributes:
        player_id: The first player's ID
        opponent_id: The second player's ID
        message: Error message explaining that the players have never met

    Example:
        ```python
        from ifpa_api import IfpaClient
        from ifpa_api.exceptions import PlayersNeverMetError

        client = IfpaClient(api_key="your-key")

        try:
            pvp = client.player(12345).pvp(67890)
        except PlayersNeverMetError as e:
            print(f"Players {e.player_id} and {e.opponent_id} have never competed together")
        ```
    """

    def __init__(
        self, player_id: int | str, opponent_id: int | str, message: str | None = None
    ) -> None:
        """Initialize the PlayersNeverMetError.

        Args:
            player_id: The first player's ID
            opponent_id: The second player's ID
            message: Optional custom message (default will be generated)
        """
        self.player_id = player_id
        self.opponent_id = opponent_id
        if message is None:
            message = (
                f"Players {player_id} and {opponent_id} have never competed in the "
                "same tournament. The IFPA API returns 404 when no head-to-head data exists."
            )
        super().__init__(message)


class SeriesPlayerNotFoundError(IfpaError):
    """Raised when requesting player card for a player not in the series.

    This exception is raised when the IFPA API returns a 404 error indicating
    that the specified player has no results in the given series/region.

    Attributes:
        series_code: The series code (e.g., "PAPA")
        player_id: The player's ID
        region_code: The region code (e.g., "OH")
        message: Error message explaining player not found in series

    Example:
        ```python
        from ifpa_api import IfpaClient
        from ifpa_api.exceptions import SeriesPlayerNotFoundError

        client = IfpaClient(api_key="your-key")

        try:
            card = client.series("PAPA").player_card(12345, "OH")
        except SeriesPlayerNotFoundError as e:
            print(f"Player {e.player_id} has no results in {e.series_code} series")
        ```
    """

    def __init__(
        self,
        series_code: str,
        player_id: int | str,
        region_code: str,
        message: str | None = None,
    ) -> None:
        """Initialize the SeriesPlayerNotFoundError.

        Args:
            series_code: The series code
            player_id: The player's ID
            region_code: The region code
            message: Optional custom message (default will be generated)
        """
        self.series_code = series_code
        self.player_id = player_id
        self.region_code = region_code
        if message is None:
            message = (
                f"Player {player_id} has no results in {series_code} series "
                f"for region {region_code}. The IFPA API returns 404 when no "
                f"player card data exists."
            )
        super().__init__(message)


class TournamentNotLeagueError(IfpaError):
    """Raised when requesting league data for a non-league tournament.

    This exception is raised when the IFPA API returns a 404 error indicating
    that the specified tournament is not in league format.

    Attributes:
        tournament_id: The tournament's ID
        message: Error message explaining tournament is not a league

    Example:
        ```python
        from ifpa_api import IfpaClient
        from ifpa_api.exceptions import TournamentNotLeagueError

        client = IfpaClient(api_key="your-key")

        try:
            league = client.tournament(12345).league()
        except TournamentNotLeagueError as e:
            print(f"Tournament {e.tournament_id} is not a league-format tournament")
        ```
    """

    def __init__(self, tournament_id: int | str, message: str | None = None) -> None:
        """Initialize the TournamentNotLeagueError.

        Args:
            tournament_id: The tournament's ID
            message: Optional custom message (default will be generated)
        """
        self.tournament_id = tournament_id
        if message is None:
            message = (
                f"Tournament {tournament_id} is not a league-format tournament. "
                f"The IFPA API returns 404 for non-league tournaments."
            )
        super().__init__(message)
