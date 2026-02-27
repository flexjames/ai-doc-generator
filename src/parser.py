import json
import logging
from pathlib import Path
from typing import Any, cast

import yaml

from src.models import APIEndpoint, APISpec, HTTPMethod, Parameter, RequestBody, ResponseInfo

logger = logging.getLogger(__name__)

_SUPPORTED_METHODS = {m.value.lower() for m in HTTPMethod}


def _load_file(file_path: str) -> dict[str, Any]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Spec file not found: {file_path}")
    try:
        if path.suffix == ".json":
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        elif path.suffix in {".yaml", ".yml"}:
            with open(path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported file extension '{path.suffix}': {file_path}")
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise ValueError(f"Failed to parse spec file '{file_path}': {exc}") from exc


def _resolve_refs(spec: dict[str, Any]) -> dict[str, Any]:
    schemas: dict[str, Any] = (spec.get("components") or {}).get("schemas") or {}

    def _resolve(node: Any, visiting: frozenset[str]) -> Any:
        if isinstance(node, dict):
            if "$ref" in node and len(node) == 1:
                ref = node["$ref"]
                if not ref.startswith("#/components/schemas/"):
                    logger.warning("Skipping non-local $ref: %s", ref)
                    return node
                name = ref.split("/")[-1]
                if name in visiting:
                    logger.warning("Circular $ref detected for '%s'; breaking cycle", name)
                    return node
                if name not in schemas:
                    logger.warning("Unresolvable $ref '%s'; leaving as-is", ref)
                    return node
                return _resolve(schemas[name], visiting | {name})
            return {k: _resolve(v, visiting) for k, v in node.items()}
        if isinstance(node, list):
            return [_resolve(item, visiting) for item in node]
        return node

    return _resolve(spec, frozenset())


def _summarize_schema(schema: dict[str, Any] | None, depth: int = 0) -> str:
    if not schema:
        return ""
    if not isinstance(schema, dict):
        return str(schema)
    schema_type = schema.get("type")
    if schema_type == "array":
        items: dict[str, Any] | None = schema.get("items")
        if items:
            return f"array of {_summarize_schema(items, depth)}"
        return "array"
    if schema_type == "object" or "properties" in schema:
        if depth >= 3:
            return "..."
        props = cast(dict[str, dict[str, Any]], schema.get("properties") or {})
        if not props:
            return "object"
        parts = []
        for field, field_schema in props.items():
            field_type = field_schema.get("type", "object")
            if field_type == "object" or "properties" in field_schema:
                nested = _summarize_schema(field_schema, depth + 1)
                parts.append(f"{field}: {nested}")
            else:
                parts.append(f"{field}: {field_type}")
        return "{ " + ", ".join(parts) + " }"
    if schema_type:
        return schema_type
    return ""


def _extract_parameters(params: list[dict[str, Any]]) -> list[Parameter]:
    result = []
    for p in params or []:
        schema: dict[str, Any] = p.get("schema") or {}
        result.append(Parameter(
            name=p.get("name", ""),
            location=p.get("in", ""),
            required=p.get("required", False),
            schema_type=schema.get("type", "string"),
            description=p.get("description"),
        ))
    return result


def _extract_request_body(body: dict[str, Any] | None) -> RequestBody | None:
    if not body:
        return None
    content: dict[str, Any] = body.get("content") or {}
    if not content:
        return None
    content_type = next(iter(content))
    schema: dict[str, Any] = (content[content_type] or {}).get("schema") or {}
    return RequestBody(
        content_type=content_type,
        schema_summary=_summarize_schema(schema),
        required=body.get("required", True),
    )


def _extract_responses(responses: dict[str, Any]) -> list[ResponseInfo]:
    result = []
    for status_code, response in (responses or {}).items():
        description = (response or {}).get("description", "")
        schema_summary = None
        content: dict[str, Any] = (response or {}).get("content") or {}
        if content:
            first_content: dict[str, Any] = next(iter(content.values()))
            schema: dict[str, Any] = (first_content or {}).get("schema") or {}
            summary = _summarize_schema(schema)
            schema_summary = summary if summary else None
        result.append(ResponseInfo(
            status_code=str(status_code),
            description=description,
            schema_summary=schema_summary,
        ))
    return result


def _extract_endpoints(spec: dict[str, Any]) -> list[APIEndpoint]:
    paths = cast(dict[str, Any], spec.get("paths") or {})
    if not paths:
        logger.warning("Spec has no paths defined; returning empty endpoint list")
    endpoints = []
    for path, path_item in paths.items():
        path_item = cast(dict[str, Any], path_item)
        path_params = cast(list[dict[str, Any]], path_item.get("parameters") or [])
        for method_key, operation in path_item.items():
            if method_key == "parameters" or not isinstance(operation, dict):
                continue
            if method_key not in _SUPPORTED_METHODS:
                continue
            op_params = cast(list[dict[str, Any]], operation.get("parameters") or [])
            merged_params = _merge_parameters(path_params, op_params)
            endpoints.append(APIEndpoint(
                method=HTTPMethod(method_key.upper()),
                path=path,
                operation_id=operation.get("operationId"),
                summary=operation.get("summary"),
                description=operation.get("description"),
                tags=operation.get("tags") or [],
                parameters=_extract_parameters(merged_params),
                request_body=_extract_request_body(operation.get("requestBody")),
                responses=_extract_responses(operation.get("responses") or {}),
            ))
    return endpoints


def _merge_parameters(path_params: list[dict[str, Any]], op_params: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged = {(p["name"], p["in"]): p for p in path_params if "name" in p and "in" in p}
    for p in op_params:
        if "name" in p and "in" in p:
            merged[(p["name"], p["in"])] = p
    return list(merged.values())


def parse_spec(file_path: str) -> APISpec:
    raw = _load_file(file_path)
    resolved = _resolve_refs(raw)
    info: dict[str, Any] = resolved.get("info") or {}
    title = info.get("title")
    version = info.get("version")
    if not title:
        logger.warning("Spec is missing info.title; using 'Unknown'")
        title = "Unknown"
    if not version:
        logger.warning("Spec is missing info.version; using 'Unknown'")
        version = "Unknown"
    servers: list[dict[str, Any]] = resolved.get("servers") or []
    base_url = servers[0].get("url") if servers else None
    endpoints = _extract_endpoints(resolved)
    return APISpec(
        title=title,
        version=version,
        description=info.get("description"),
        base_url=base_url,
        endpoints=endpoints,
    )
