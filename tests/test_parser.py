import json
from pathlib import Path

import pytest

from src.models import APISpec, HTTPMethod
from src.parser import (
    _extract_endpoints,
    _resolve_refs,
    _summarize_schema,
    parse_spec,
)

FIXTURES = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# parse_spec — file loading
# ---------------------------------------------------------------------------

class TestParseSpecJSON:
    def test_minimal_spec(self):
        spec = parse_spec(str(FIXTURES / "minimal-spec.json"))
        assert isinstance(spec, APISpec)
        assert spec.title == "Minimal API"
        assert spec.version == "1.0.0"
        assert len(spec.endpoints) == 1
        assert spec.endpoints[0].method == HTTPMethod.GET
        assert spec.endpoints[0].path == "/health"

    def test_rewards_spec_six_endpoints(self):
        spec = parse_spec(str(FIXTURES / "rewards-api-spec.json"))
        assert isinstance(spec, APISpec)
        assert len(spec.endpoints) == 6
        methods = {ep.method for ep in spec.endpoints}
        assert HTTPMethod.GET in methods
        assert HTTPMethod.POST in methods

    def test_rewards_spec_has_parameters_and_request_body(self):
        spec = parse_spec(str(FIXTURES / "rewards-api-spec.json"))
        endpoints_with_params = [ep for ep in spec.endpoints if ep.parameters]
        assert len(endpoints_with_params) > 0
        endpoints_with_body = [ep for ep in spec.endpoints if ep.request_body is not None]
        assert len(endpoints_with_body) > 0

    def test_rewards_spec_base_url(self):
        spec = parse_spec(str(FIXTURES / "rewards-api-spec.json"))
        assert spec.base_url == "https://api.rewards.example.com"

    def test_rewards_spec_description(self):
        spec = parse_spec(str(FIXTURES / "rewards-api-spec.json"))
        assert spec.description == "A loyalty rewards platform API"


class TestParseSpecYAML:
    def test_yaml_file(self, tmp_path):
        yaml_content = (
            "openapi: '3.0.0'\n"
            "info:\n"
            "  title: YAML API\n"
            "  version: '2.0.0'\n"
            "paths:\n"
            "  /ping:\n"
            "    get:\n"
            "      responses:\n"
            "        '200':\n"
            "          description: pong\n"
        )
        spec_file = tmp_path / "test.yaml"
        spec_file.write_text(yaml_content)
        spec = parse_spec(str(spec_file))
        assert spec.title == "YAML API"
        assert spec.version == "2.0.0"
        assert len(spec.endpoints) == 1

    def test_yaml_with_anchors(self, tmp_path):
        yaml_content = (
            "openapi: '3.0.0'\n"
            "info:\n"
            "  title: Anchor API\n"
            "  version: &ver '3.0.0'\n"
            "paths:\n"
            "  /a:\n"
            "    get:\n"
            "      responses:\n"
            "        '200':\n"
            "          description: ok\n"
        )
        spec_file = tmp_path / "anchors.yaml"
        spec_file.write_text(yaml_content)
        spec = parse_spec(str(spec_file))
        assert spec.version == "3.0.0"


class TestParseSpecErrors:
    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError) as exc_info:
            parse_spec("/nonexistent/path/spec.json")
        assert "/nonexistent/path/spec.json" in str(exc_info.value)

    def test_malformed_json_raises(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{ not valid json }")
        with pytest.raises(ValueError) as exc_info:
            parse_spec(str(bad_file))
        assert str(bad_file) in str(exc_info.value)

    def test_no_paths_returns_empty_endpoints(self):
        spec_dict = {"openapi": "3.0.0", "info": {"title": "No Paths", "version": "1.0.0"}}
        endpoints = _extract_endpoints(spec_dict)
        assert endpoints == []

    def test_parse_spec_no_paths_key(self, tmp_path):
        data = {"openapi": "3.0.0", "info": {"title": "Empty", "version": "1.0.0"}}
        spec_file = tmp_path / "empty.json"
        spec_file.write_text(json.dumps(data))
        spec = parse_spec(str(spec_file))
        assert isinstance(spec, APISpec)
        assert spec.endpoints == []


# ---------------------------------------------------------------------------
# _resolve_refs
# ---------------------------------------------------------------------------

class TestResolveRefs:
    def test_ref_is_inlined(self):
        spec = {
            "components": {
                "schemas": {
                    "User": {"type": "object", "properties": {"id": {"type": "string"}}}
                }
            },
            "paths": {
                "/users": {
                    "get": {
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/User"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        resolved = _resolve_refs(spec)
        schema = (
            resolved["paths"]["/users"]["get"]["responses"]["200"]
            ["content"]["application/json"]["schema"]
        )
        assert schema == {"type": "object", "properties": {"id": {"type": "string"}}}

    def test_circular_ref_does_not_infinite_loop(self):
        spec = {
            "components": {
                "schemas": {
                    "A": {"type": "object", "properties": {"b": {"$ref": "#/components/schemas/B"}}},
                    "B": {"type": "object", "properties": {"a": {"$ref": "#/components/schemas/A"}}},
                }
            }
        }
        result = _resolve_refs(spec)
        assert result is not None

    def test_unresolvable_ref_left_as_is(self):
        spec = {
            "components": {"schemas": {}},
            "data": {"$ref": "#/components/schemas/Missing"}
        }
        result = _resolve_refs(spec)
        assert result["data"] == {"$ref": "#/components/schemas/Missing"}


# ---------------------------------------------------------------------------
# _extract_endpoints
# ---------------------------------------------------------------------------

class TestExtractEndpoints:
    def test_skips_unsupported_methods(self):
        spec = {
            "paths": {
                "/ping": {
                    "get": {"responses": {"200": {"description": "ok"}}},
                    "options": {"responses": {"200": {"description": "ok"}}},
                    "head": {"responses": {"200": {"description": "ok"}}},
                }
            }
        }
        endpoints = _extract_endpoints(spec)
        assert len(endpoints) == 1
        assert endpoints[0].method == HTTPMethod.GET

    def test_path_level_params_appear_on_all_operations(self):
        spec = {
            "paths": {
                "/items/{itemId}": {
                    "parameters": [
                        {"name": "itemId", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "get": {"responses": {"200": {"description": "ok"}}},
                    "delete": {"responses": {"204": {"description": "deleted"}}},
                }
            }
        }
        endpoints = _extract_endpoints(spec)
        assert len(endpoints) == 2
        for ep in endpoints:
            assert any(p.name == "itemId" for p in ep.parameters)

    def test_operation_param_overrides_path_param(self):
        spec = {
            "paths": {
                "/items/{itemId}": {
                    "parameters": [
                        {"name": "itemId", "in": "path", "required": True,
                         "schema": {"type": "string"}, "description": "path-level"}
                    ],
                    "get": {
                        "parameters": [
                            {"name": "itemId", "in": "path", "required": True,
                             "schema": {"type": "string"}, "description": "op-level"}
                        ],
                        "responses": {"200": {"description": "ok"}}
                    }
                }
            }
        }
        endpoints = _extract_endpoints(spec)
        assert len(endpoints) == 1
        assert len(endpoints[0].parameters) == 1
        assert endpoints[0].parameters[0].description == "op-level"


# ---------------------------------------------------------------------------
# _summarize_schema
# ---------------------------------------------------------------------------

class TestSummarizeSchema:
    def test_flat_object(self):
        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
            }
        }
        result = _summarize_schema(schema)
        assert "id: string" in result
        assert "name: string" in result
        assert result.startswith("{")
        assert result.endswith("}")

    def test_array_schema(self):
        schema = {
            "type": "array",
            "items": {"type": "object", "properties": {"id": {"type": "string"}}}
        }
        result = _summarize_schema(schema)
        assert "array of" in result

    def test_none_returns_empty_string(self):
        assert _summarize_schema(None) == ""

    def test_empty_dict_returns_empty_string(self):
        assert _summarize_schema({}) == ""


# ---------------------------------------------------------------------------
# Edge cases on endpoints
# ---------------------------------------------------------------------------

class TestEndpointEdgeCases:
    def test_missing_summary_and_description_are_none(self):
        spec = {
            "paths": {
                "/x": {
                    "get": {"responses": {"200": {"description": "ok"}}}
                }
            }
        }
        endpoints = _extract_endpoints(spec)
        assert endpoints[0].summary is None
        assert endpoints[0].description is None

    def test_no_request_body_is_none(self):
        spec = {
            "paths": {
                "/x": {
                    "get": {"responses": {"200": {"description": "ok"}}}
                }
            }
        }
        endpoints = _extract_endpoints(spec)
        assert endpoints[0].request_body is None

    def test_response_without_content_has_none_schema_summary(self):
        spec = {
            "paths": {
                "/x": {
                    "delete": {
                        "responses": {"204": {"description": "No Content"}}
                    }
                }
            }
        }
        endpoints = _extract_endpoints(spec)
        assert len(endpoints[0].responses) == 1
        assert endpoints[0].responses[0].schema_summary is None
