import pytest
from pydantic import ValidationError

from src.models import (
    APIEndpoint,
    APISpec,
    GeneratedDoc,
    GenerationResult,
    HTTPMethod,
    Parameter,
    RequestBody,
    ResponseInfo,
)


# ---------------------------------------------------------------------------
# HTTPMethod
# ---------------------------------------------------------------------------

class TestHTTPMethod:
    def test_members_exist(self):
        assert HTTPMethod.GET
        assert HTTPMethod.POST
        assert HTTPMethod.PUT
        assert HTTPMethod.PATCH
        assert HTTPMethod.DELETE

    def test_compares_equal_to_string(self):
        assert HTTPMethod.GET == "GET"
        assert HTTPMethod.POST == "POST"
        assert HTTPMethod.DELETE == "DELETE"

    def test_unsupported_verb_raises(self):
        with pytest.raises(AttributeError):
            _ = HTTPMethod.OPTIONS

        with pytest.raises(AttributeError):
            _ = HTTPMethod.HEAD


# ---------------------------------------------------------------------------
# Parameter
# ---------------------------------------------------------------------------

class TestParameter:
    def test_valid_full_construction(self):
        p = Parameter(
            name="page",
            location="query",
            required=False,
            schema_type="integer",
            description="Page number",
        )
        assert p.name == "page"
        assert p.location == "query"
        assert p.required is False
        assert p.schema_type == "integer"
        assert p.description == "Page number"

    def test_defaults_when_only_required_fields(self):
        p = Parameter(name="id", location="path")
        assert p.required is False
        assert p.schema_type == "string"
        assert p.description is None

    def test_missing_name_raises_validation_error(self):
        with pytest.raises(ValidationError):
            Parameter(location="query")

    def test_missing_location_raises_validation_error(self):
        with pytest.raises(ValidationError):
            Parameter(name="id")


# ---------------------------------------------------------------------------
# RequestBody
# ---------------------------------------------------------------------------

class TestRequestBody:
    def test_valid_construction_with_defaults(self):
        rb = RequestBody(schema_summary="{ id: string, name: string }")
        assert rb.content_type == "application/json"
        assert rb.schema_summary == "{ id: string, name: string }"
        assert rb.required is True

    def test_custom_content_type(self):
        rb = RequestBody(schema_summary="binary", content_type="multipart/form-data")
        assert rb.content_type == "multipart/form-data"

    def test_missing_schema_summary_raises_validation_error(self):
        with pytest.raises(ValidationError):
            RequestBody()


# ---------------------------------------------------------------------------
# ResponseInfo
# ---------------------------------------------------------------------------

class TestResponseInfo:
    def test_valid_with_schema(self):
        r = ResponseInfo(status_code="200", description="OK", schema_summary="{ id: string }")
        assert r.status_code == "200"
        assert r.description == "OK"
        assert r.schema_summary == "{ id: string }"

    def test_valid_without_schema(self):
        r = ResponseInfo(status_code="204", description="No Content")
        assert r.schema_summary is None

    def test_missing_status_code_raises_validation_error(self):
        with pytest.raises(ValidationError):
            ResponseInfo(description="OK")

    def test_missing_description_raises_validation_error(self):
        with pytest.raises(ValidationError):
            ResponseInfo(status_code="200")


# ---------------------------------------------------------------------------
# APIEndpoint
# ---------------------------------------------------------------------------

class TestAPIEndpoint:
    def test_minimal_valid_construction(self):
        ep = APIEndpoint(method=HTTPMethod.GET, path="/users")
        assert ep.method == HTTPMethod.GET
        assert ep.path == "/users"
        assert ep.operation_id is None
        assert ep.summary is None
        assert ep.description is None
        assert ep.tags == []
        assert ep.parameters == []
        assert ep.request_body is None
        assert ep.responses == []

    def test_full_construction(self):
        param = Parameter(name="id", location="path", required=True)
        body = RequestBody(schema_summary="{ name: string }")
        resp = ResponseInfo(status_code="200", description="OK")
        ep = APIEndpoint(
            method=HTTPMethod.POST,
            path="/users/{id}",
            operation_id="updateUser",
            summary="Update user",
            description="Updates an existing user record.",
            tags=["users"],
            parameters=[param],
            request_body=body,
            responses=[resp],
        )
        assert ep.method == HTTPMethod.POST
        assert ep.operation_id == "updateUser"
        assert len(ep.parameters) == 1
        assert ep.request_body is not None
        assert len(ep.responses) == 1

    def test_invalid_method_raises_validation_error(self):
        with pytest.raises(ValidationError):
            APIEndpoint(method="OPTIONS", path="/ping")

    def test_list_fields_not_shared_across_instances(self):
        ep1 = APIEndpoint(method=HTTPMethod.GET, path="/a")
        ep2 = APIEndpoint(method=HTTPMethod.GET, path="/b")
        ep1.tags.append("admin")
        assert ep2.tags == []

        ep1.parameters.append(Parameter(name="x", location="query"))
        assert ep2.parameters == []


# ---------------------------------------------------------------------------
# APISpec
# ---------------------------------------------------------------------------

class TestAPISpec:
    def test_valid_with_endpoints(self):
        ep = APIEndpoint(method=HTTPMethod.GET, path="/health")
        spec = APISpec(title="My API", version="1.0.0", endpoints=[ep])
        assert spec.title == "My API"
        assert spec.version == "1.0.0"
        assert len(spec.endpoints) == 1
        assert spec.description is None
        assert spec.base_url is None

    def test_valid_with_empty_endpoints(self):
        spec = APISpec(title="Empty API", version="0.1.0", endpoints=[])
        assert spec.endpoints == []

    def test_missing_title_raises_validation_error(self):
        with pytest.raises(ValidationError):
            APISpec(version="1.0.0", endpoints=[])

    def test_missing_version_raises_validation_error(self):
        with pytest.raises(ValidationError):
            APISpec(title="My API", endpoints=[])


# ---------------------------------------------------------------------------
# GeneratedDoc
# ---------------------------------------------------------------------------

class TestGeneratedDoc:
    def test_valid_construction(self):
        doc = GeneratedDoc(
            endpoint_ref="GET /users/{id}",
            markdown="# GET /users/{id}\nReturns a user.",
            tokens_used=450,
            model="claude-sonnet-4-20250514",
        )
        assert doc.endpoint_ref == "GET /users/{id}"
        assert doc.tokens_used == 450

    def test_model_dump_returns_correct_keys(self):
        doc = GeneratedDoc(
            endpoint_ref="POST /users",
            markdown="# POST /users",
            tokens_used=300,
            model="claude-sonnet-4-20250514",
        )
        d = doc.model_dump()
        assert set(d.keys()) == {"endpoint_ref", "markdown", "tokens_used", "model"}


# ---------------------------------------------------------------------------
# GenerationResult
# ---------------------------------------------------------------------------

class TestGenerationResult:
    def _make_doc(self):
        return GeneratedDoc(
            endpoint_ref="GET /items",
            markdown="# GET /items",
            tokens_used=200,
            model="claude-sonnet-4-20250514",
        )

    def test_valid_construction(self):
        doc = self._make_doc()
        result = GenerationResult(
            api_title="Items API",
            api_version="2.0.0",
            docs=[doc],
            total_tokens=200,
            total_cost_usd=0.0012,
            model="claude-sonnet-4-20250514",
        )
        assert result.api_title == "Items API"
        assert len(result.docs) == 1
        assert result.total_cost_usd == pytest.approx(0.0012)

    def test_model_dump_returns_nested_docs_as_dicts(self):
        doc = self._make_doc()
        result = GenerationResult(
            api_title="Items API",
            api_version="2.0.0",
            docs=[doc],
            total_tokens=200,
            total_cost_usd=0.0012,
            model="claude-sonnet-4-20250514",
        )
        d = result.model_dump()
        assert isinstance(d["docs"], list)
        assert isinstance(d["docs"][0], dict)
        assert "endpoint_ref" in d["docs"][0]

    def test_invalid_total_cost_usd_type_raises_validation_error(self):
        with pytest.raises(ValidationError):
            GenerationResult(
                api_title="Items API",
                api_version="2.0.0",
                docs=[],
                total_tokens=0,
                total_cost_usd="not-a-float",
                model="claude-sonnet-4-20250514",
            )
