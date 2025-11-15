Here’s a detailed spec you can hand to the team for building a professional IFPA Python client SDK.

⸻

1. Project overview

Working name: ifpa-sdk (PyPI package: ifpa-sdk, top-level module ifpa_sdk)

Goal:
Provide a typed, well-structured, Pydantic-powered Python client for the IFPA (International Flipper Pinball Association) API, using their OpenAPI JSON at https://api.ifpapinball.com/docs/api.json as the contract. The SDK should expose resource-oriented clients (players, directors, rankings, tournaments, calendar, etc.), plus “handle” objects for fluent access to individual entities.

IFPA API is read-only (GET-only) and exposes players, tournaments, rankings, calendar/events, etc.

⸻

2. High-level architecture

2.1 Layers
	1.	HTTP Core Layer
	•	Responsible for:
	•	Base URL & path construction
	•	Auth (API key)
	•	Timeouts, retries (basic)
	•	Error mapping (HTTP → custom exceptions)
	•	Implemented as _HttpClient or BaseClient using requests.
	2.	Domain SDK Layer (typed SDK)
	•	Pydantic models for requests/responses/enums.
	•	Resource subclients:
	•	DirectorsClient, PlayersClient, RankingsClient, TournamentsClient, CalendarClient, etc.
	•	Handle objects:
	•	DirectorHandle, PlayerHandle, etc. with .get() as default accessor and additional sub-resource methods.
	•	Request validation optional via validate_requests flag.
	3.	Public Facade
	•	IfpaClient as the main entry point.
	•	Properties for top-level resources (client.directors, client.players, client.rankings, …).
	•	Methods returning handles (client.director(id) -> DirectorHandle).

⸻

3. Technology & tooling
	•	Python: 3.11+ (specify officially supported minor versions).
	•	Dependency management: Poetry.
	•	HTTP: requests.
	•	Models & validation: pydantic>=2 (request/response models, enums, validation)
	•	Testing: pytest, requests-mock or responses for unit tests; real API for integration.
	•	Linting/formatting: ruff + black (or ruff formatting if you want a single tool).
	•	Type checking: mypy (optional but recommended).
	•	Pre-commit: pre-commit with hooks configured.

⸻

4. Package structure

Use a src/ layout with one top-level distribution (ifpa-sdk) but internal subpackages for organization.

ifpa-sdk/
  pyproject.toml
  README.md
  LICENSE
  src/
    ifpa_sdk/
      __init__.py
      config.py           # settings, env handling
      exceptions.py       # APIError, ValidationError, etc.
      http.py             # low-level HTTP client
      client.py           # IfpaClient, Async client (future)
      models/             # Pydantic models & enums
        __init__.py
        common.py         # shared base models/enums (TimePeriod, CountryCode, etc.)
        director.py
        player.py
        rankings.py
        tournaments.py
        calendar.py
        # others as needed
      resources/          # resource clients & handles
        __init__.py
        directors.py
        players.py
        rankings.py
        tournaments.py
        calendar.py
        # handle classes live here too
  tests/
    unit/
      test_client_config.py
      test_http_error_handling.py
      test_directors_client.py
      ...
    integration/
      test_players_integration.py
      test_rankings_integration.py
      ...
  .pre-commit-config.yaml


⸻

5. Configuration & initialization

5.1 Base URL
	•	Use the documented IFPA API base URL (from their API docs / Swagger UI, e.g. https://api.ifpapinball.com/v1 – confirm from api.json).
	•	Expose as an optional constructor argument in case it changes or for testing.

5.2 API key
	•	Constructor signature (conceptual):

class IfpaClient:
    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 10.0,
        validate_requests: bool = True,
    )


	•	API key resolution logic:
	1.	If api_key argument is provided, use it.
	2.	Else, read from IFPA_API_KEY environment variable.
	3.	If neither available, raise a clear error (MissingApiKeyError).

5.3 Validation flag
	•	validate_requests: bool = True stored on client and passed into resource clients/handles.
	•	When True, request Pydantic models must be instantiated and validated before hitting HTTP.
	•	When False, models may be skipped or only minimally used, avoiding extra overhead.

⸻

6. HTTP client design

6.1 Implementation
	•	http.py exposes a small internal class, e.g. _HttpClient:
Responsibilities:
	•	Store shared requests.Session.
	•	Manage base URL, headers, timeout.
	•	Provide _request(method, path, params=None, json=None, ...) abstraction.
	•	Normalize and raise errors:
	•	On non-2xx: raise IfpaApiError(status_code, message, error_body=...).
	•	Attach headers:
	•	Authorization: Bearer <API_KEY> if that’s how IFPA requires it (verify from docs; some APIs use ?api_key= or custom header).
	•	Accept: application/json

6.2 Error handling

Define exceptions in exceptions.py:
	•	IfpaError (base)
	•	MissingApiKeyError
	•	IfpaApiError (wraps status code + body)
	•	IfpaClientValidationError (wraps Pydantic validation errors when validate_requests=True)

⸻

7. Pydantic model strategy

Follow Pydantic best practices (clear separation of models, shared config, enums, etc.).

7.1 Source of truth
	•	Use https://api.ifpapinball.com/docs/api.json as the contract.
	•	Generate initial Pydantic models using a compatible generator (e.g. datamodel-code-generator or openapi-python-client in “models only” mode), then refine manually as needed.
	•	Keep models/ package as the single source of truth for request/response shapes.

7.2 Organization
	•	models/common.py
	•	Shared base model class: BaseModel subclass with common config (e.g. model_config = ConfigDict(extra="ignore")).
	•	Shared enums: TimePeriod, CountryCode, RankingType, etc. (derive from OpenAPI enum definitions).
	•	Shared pagination models, if any.
	•	Resource-specific model modules:
	•	models/director.py – Director, DirectorTournamentsRequest, DirectorTournamentsResponse, etc.
	•	models/player.py
	•	models/rankings.py
	•	models/tournaments.py
	•	models/calendar.py

7.3 Request vs response models
	•	Request models should:
	•	Enforce required vs optional fields per OpenAPI.
	•	Encode query/path params (e.g. DirectorTournamentsRequest(director_id, time_period)).
	•	Provide simple .to_params() and .to_path() helpers where useful.
	•	Response models should:
	•	Mirror IFPA JSON responses.
	•	Use model_validate to parse raw JSON.

7.4 Client-side validation behavior
	•	When validate_requests=True:
	•	Each public SDK method should instantiate a Pydantic request model using provided arguments.
	•	If ValidationError is raised, wrap and raise IfpaClientValidationError.
	•	When False:
	•	Skip model construction or use a fast path (e.g. rely only on simple type assumptions).

⸻

8. Resource clients & handle pattern

8.1 Main IfpaClient facade
	•	Properties:

class IfpaClient:
    @property
    def directors(self) -> DirectorsClient: ...
    @property
    def players(self) -> PlayersClient: ...
    @property
    def rankings(self) -> RankingsClient: ...
    @property
    def tournaments(self) -> TournamentsClient: ...
    @property
    def calendar(self) -> CalendarClient: ...


	•	Handle factories:

def director(self, director_id: int | str) -> DirectorHandle: ...
def player(self, player_id: int | str) -> PlayerHandle: ...
# Add handles for others if useful.



8.2 Directors example (pattern template)
	•	resources/directors.py:
	•	DirectorsClient for collection-level operations (search, list, etc.).
	•	DirectorHandle for instance-level operations.
Spec-level interface (not implementation):

class DirectorsClient:
    def __init__(self, http: _HttpClient, validate_requests: bool): ...

    def list(...): ...
    def search(...): ...
    # any collection operations defined by IFPA

class DirectorHandle:
    def __init__(self, http: _HttpClient, director_id: int | str, validate_requests: bool): ...

    def get(self) -> Director: ...
    def tournaments(self, time_period: TimePeriod) -> DirectorTournamentsResponse: ...
    # Potential other sub-resources targeting /director/{id}/...


	•	IfpaClient.director(id) returns a DirectorHandle wired with shared _HttpClient and validate_requests flag.

8.3 Other resources

Follow the same structure:
	•	PlayersClient, PlayerHandle
	•	e.g. /player/{id} details, rankings, history.
	•	RankingsClient
	•	Overall rankings, country rankings, etc.
	•	TournamentsClient, possibly TournamentHandle
	•	Info about a single tournament, results, etc.
	•	CalendarClient
	•	Calendar endpoints (active events, upcoming, etc.).

Use IFPA’s endpoints from the OpenAPI JSON to fill in exact operations and models.

⸻

9. Client method naming conventions
	•	Use Pythonic names and resource-oriented semantics, not raw HTTP paths.

Examples:
	•	/director/{id} → DirectorHandle.get()
	•	/director/{id}/tournaments/{time_period} → DirectorHandle.tournaments(time_period=TimePeriod.PAST)
	•	/player/{id} → PlayerHandle.get()
	•	Rankings endpoints:
	•	/rankings/wppr → RankingsClient.wppr(...)
	•	/rankings/country → RankingsClient.by_country(...)
	•	Calendar endpoints:
	•	/calendar/active → CalendarClient.active_events(...)
	•	/calendar/past → CalendarClient.past_events(...)

Align naming with what IFPA docs call these concepts (Players, Rankings, Calendar, etc.).

⸻

10. Testing strategy

10.1 Unit tests

Location: tests/unit/

Goals:
	•	Verify:
	•	Request construction logic (paths, query params).
	•	Client-side validation (raises on invalid input when validate_requests=True).
	•	Error mapping from HTTP responses to IfpaApiError, etc.
	•	Use responses or requests-mock to intercept HTTP calls and return canned responses.

Examples:
	•	test_client_config.py
	•	Tests API key resolution (constructor vs env var).
	•	test_directors_client.py
	•	Validates the path /director/{id}/tournaments/{time_period} is called correctly for DirectorHandle.tournaments.

10.2 Integration tests

Location: tests/integration/
	•	Mark tests with @pytest.mark.integration.
	•	Require IFPA_API_KEY from environment:
	•	If missing, skip integration tests with pytest.skip.
	•	Call real endpoints with a small, safe subset of operations (e.g. retrieving known players, sample rankings).
	•	Validate:
	•	Deserialization into Pydantic models.
	•	Basic behavior of handles and resource methods.

⸻

11. Pre-commit & code quality

11.1 .pre-commit-config.yaml

Include hooks such as:
	•	black (or ruff formatter) – formatting.
	•	ruff – linting (E, F, I, N, UP, etc.).
	•	mypy – optional type checking.
	•	check-yaml, check-toml.
	•	end-of-file-fixer, trailing-whitespace.

Install and wire into Poetry dev dependencies.

11.2 Poetry configuration

In pyproject.toml:
	•	[tool.poetry.dependencies]
	•	python = "^3.11"
	•	requests
	•	pydantic
	•	[tool.poetry.group.dev.dependencies]
	•	pytest, responses or requests-mock, pre-commit, ruff, black, mypy etc.

⸻

12. README & documentation

12.1 README content outline
	1.	Project name & badges
	•	PyPI version, build status (if CI), license.
	2.	Overview
	•	One paragraph: Typed Python client for the IFPA API.
	3.	Installation
	•	pip install ifpa-sdk
	4.	Quickstart

from ifpa_sdk import IfpaClient, TimePeriod

client = IfpaClient()  # uses IFPA_API_KEY from env
director = client.director(1234).get()
tournaments = client.director(1234).tournaments(TimePeriod.PAST)


	5.	Configuration
	•	API key sources (constructor vs env).
	•	Base URL override.
	•	validate_requests flag.
	6.	Usage Guide
	•	Players (examples for client.player(id).get(), client.players.search(...)).
	•	Directors & tournaments.
	•	Rankings.
	•	Calendar.
	7.	Error Handling
	•	Explain IfpaApiError, validation errors, etc.
	8.	Testing
	•	How to run unit tests.
	•	How to run integration tests (requires API key).
	9.	Contributing
	•	Code style (black/ruff).
	•	Pre-commit usage.
	•	How to add new endpoints (update OpenAPI, model, resource client).
	10.	License

12.2 Future docs

If this grows, consider a docs/ folder with MkDocs for richer docs, but not required for v1.

⸻

13. Release & versioning
	•	Use semantic versioning:
	•	MAJOR.MINOR.PATCH
	•	v0.x while the API & SDK shape are still stabilizing.
	•	Release steps:
	1.	Bump version via Poetry.
	2.	Run tests (unit + integration locally, or via CI).
	3.	Build: poetry build.
	4.	Publish: poetry publish (with configured PyPI credentials).
	•	Maintain a CHANGELOG.md describing added endpoints, breaking changes, bug fixes.

⸻

14. Non-goals (for initial version)
	•	Async client (httpx.AsyncClient) – can be added later as AsyncIfpaClient following same resource/handle pattern.
	•	LangChain/MCP integrations – interesting future work, but out of scope for this initial SDK spec.
	•	Any write/update endpoints (IFPA API is read-only today).

⸻

If you want, a follow-up spec can focus only on one resource (e.g. Players) in full detail (models + methods + example tests) as the “reference implementation” for the rest of the team to copy.

Confidence: 8.5/10
