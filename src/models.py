from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class Parameter(BaseModel):
    name: str
    location: str
    required: bool = False
    schema_type: str = "string"
    description: Optional[str] = None


class RequestBody(BaseModel):
    content_type: str = "application/json"
    schema_summary: str
    required: bool = True


class ResponseInfo(BaseModel):
    status_code: str
    description: str
    schema_summary: Optional[str] = None


class APIEndpoint(BaseModel):
    method: HTTPMethod
    path: str
    operation_id: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    parameters: list[Parameter] = Field(default_factory=list)
    request_body: Optional[RequestBody] = None
    responses: list[ResponseInfo] = Field(default_factory=list)


class APISpec(BaseModel):
    title: str
    version: str
    description: Optional[str] = None
    base_url: Optional[str] = None
    endpoints: list[APIEndpoint]


class GeneratedDoc(BaseModel):
    endpoint_ref: str
    markdown: str
    tokens_used: int
    model: str


class GenerationResult(BaseModel):
    api_title: str
    api_version: str
    docs: list[GeneratedDoc]
    total_tokens: int
    total_cost_usd: float
    model: str
