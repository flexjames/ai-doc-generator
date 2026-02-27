import pytest

from src.models import APIEndpoint, APISpec, HTTPMethod, Parameter, RequestBody, ResponseInfo
from src.prompts import SYSTEM_PROMPT, build_endpoint_prompt, build_overview_prompt


# ---------------------------------------------------------------------------
# SYSTEM_PROMPT
# ---------------------------------------------------------------------------

class TestSystemPrompt:
    def test_is_non_empty_string(self):
        assert isinstance(SYSTEM_PROMPT, str)
        assert len(SYSTEM_PROMPT) > 0

    def test_contains_markdown(self):
        assert "markdown" in SYSTEM_PROMPT.lower()

    def test_instructs_realistic_sample_data(self):
        lower = SYSTEM_PROMPT.lower()
        assert "realistic" in lower or "domain-appropriate" in lower

    def test_references_technical_writer(self):
        assert "technical writer" in SYSTEM_PROMPT.lower()


# ---------------------------------------------------------------------------
# build_endpoint_prompt
# ---------------------------------------------------------------------------

class TestBuildEndpointPrompt:
    def _make_endpoint(self) -> APIEndpoint:
        return APIEndpoint(
            method=HTTPMethod.POST,
            path="/api/v1/members",
            operation_id="enrollMember",
            summary="Enroll a new member",
            description="Enroll a new member in the rewards program",
            tags=["members"],
            parameters=[
                Parameter(
                    name="X-Request-ID",
                    location="header",
                    required=False,
                    schema_type="string",
                    description="Optional request identifier",
                )
            ],
            request_body=RequestBody(
                content_type="application/json",
                schema_summary="{ firstName: string, lastName: string, email: string }",
                required=True,
            ),
            responses=[
                ResponseInfo(status_code="201", description="Member enrolled"),
                ResponseInfo(status_code="400", description="Invalid request"),
            ],
        )

    def test_includes_method_and_path(self):
        ep = self._make_endpoint()
        prompt = build_endpoint_prompt(ep)
        assert "POST" in prompt
        assert "/api/v1/members" in prompt

    def test_includes_parameter_details(self):
        ep = self._make_endpoint()
        prompt = build_endpoint_prompt(ep)
        assert "X-Request-ID" in prompt
        assert "header" in prompt
        assert "string" in prompt

    def test_includes_request_body(self):
        ep = self._make_endpoint()
        prompt = build_endpoint_prompt(ep)
        assert "application/json" in prompt
        assert "firstName" in prompt

    def test_no_request_body_does_not_raise(self):
        ep = APIEndpoint(method=HTTPMethod.GET, path="/health")
        prompt = build_endpoint_prompt(ep)
        assert isinstance(prompt, str)

    def test_no_request_body_omits_content_type(self):
        ep = APIEndpoint(method=HTTPMethod.GET, path="/health")
        prompt = build_endpoint_prompt(ep)
        assert "application/json" not in prompt

    def test_includes_all_response_status_codes(self):
        ep = self._make_endpoint()
        prompt = build_endpoint_prompt(ep)
        assert "201" in prompt
        assert "400" in prompt
        assert "Member enrolled" in prompt
        assert "Invalid request" in prompt

    def test_requests_examples(self):
        ep = self._make_endpoint()
        prompt = build_endpoint_prompt(ep)
        lower = prompt.lower()
        assert "example" in lower or "sample" in lower


# ---------------------------------------------------------------------------
# build_overview_prompt
# ---------------------------------------------------------------------------

class TestBuildOverviewPrompt:
    def _make_spec(self) -> APISpec:
        return APISpec(
            title="Rewards API",
            version="1.0.0",
            description="A loyalty rewards platform API",
            base_url="https://api.rewards.example.com",
            endpoints=[
                APIEndpoint(method=HTTPMethod.GET, path="/api/v1/members/{memberId}", summary="Get member"),
                APIEndpoint(method=HTTPMethod.POST, path="/api/v1/members", summary="Enroll member"),
            ],
        )

    def test_includes_title_and_version(self):
        spec = self._make_spec()
        prompt = build_overview_prompt(spec)
        assert "Rewards API" in prompt
        assert "1.0.0" in prompt

    def test_includes_endpoint_count_or_list(self):
        spec = self._make_spec()
        prompt = build_overview_prompt(spec)
        assert "/api/v1/members" in prompt or "2" in prompt

    def test_no_description_does_not_raise(self):
        spec = APISpec(
            title="Minimal API",
            version="0.1.0",
            endpoints=[],
        )
        prompt = build_overview_prompt(spec)
        assert isinstance(prompt, str)

    def test_no_description_omits_none_literal(self):
        spec = APISpec(
            title="Minimal API",
            version="0.1.0",
            endpoints=[],
        )
        prompt = build_overview_prompt(spec)
        assert "None" not in prompt

    def test_requests_overview_or_introduction(self):
        spec = self._make_spec()
        prompt = build_overview_prompt(spec)
        lower = prompt.lower()
        assert "overview" in lower or "introduction" in lower
