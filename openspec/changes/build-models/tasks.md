## 1. Implement src/models.py

- [x] 1.1 Create `src/models.py` with imports: `from pydantic import BaseModel, Field`, `from typing import Optional`, `from enum import Enum`
- [x] 1.2 Implement `HTTPMethod(str, Enum)` with members GET, POST, PUT, PATCH, DELETE
- [x] 1.3 Implement `Parameter` model with fields: `name`, `location`, `required` (default `False`), `schema_type` (default `"string"`), `description` (Optional, default `None`)
- [x] 1.4 Implement `RequestBody` model with fields: `content_type` (default `"application/json"`), `schema_summary`, `required` (default `True`)
- [x] 1.5 Implement `ResponseInfo` model with fields: `status_code`, `description`, `schema_summary` (Optional, default `None`)
- [x] 1.6 Implement `APIEndpoint` model with fields: `method`, `path`, `operation_id`, `summary`, `description` (all Optional where specified), `tags`, `parameters`, `request_body`, `responses` (lists use `Field(default_factory=list)`)
- [x] 1.7 Implement `APISpec` model with fields: `title`, `version`, `description` (Optional), `base_url` (Optional), `endpoints`
- [x] 1.8 Implement `GeneratedDoc` model with fields: `endpoint_ref`, `markdown`, `tokens_used`, `model`
- [x] 1.9 Implement `GenerationResult` model with fields: `api_title`, `api_version`, `docs`, `total_tokens`, `total_cost_usd`, `model`

## 2. Implement tests/test_models.py

- [x] 2.1 Create `tests/test_models.py` with import of all models from `src.models`
- [x] 2.2 Write tests for `HTTPMethod`: members exist, `HTTPMethod.GET == "GET"` is `True`, `HTTPMethod.OPTIONS` raises `AttributeError`
- [x] 2.3 Write tests for `Parameter`: valid full construction, defaults applied when only required fields given, `ValidationError` on missing `name`
- [x] 2.4 Write tests for `RequestBody`: valid construction with defaults, `ValidationError` on missing `schema_summary`
- [x] 2.5 Write tests for `ResponseInfo`: valid with and without `schema_summary`, `ValidationError` on missing required fields
- [x] 2.6 Write tests for `APIEndpoint`: minimal valid construction with defaults, full construction, invalid method raises `ValidationError`, list fields are not shared across instances
- [x] 2.7 Write tests for `APISpec`: valid with non-empty and empty endpoint lists, `ValidationError` on missing `title`
- [x] 2.8 Write tests for `GeneratedDoc`: valid construction, `model_dump()` returns correct keys
- [x] 2.9 Write tests for `GenerationResult`: valid construction, `model_dump()` returns nested docs as dicts, invalid `total_cost_usd` type raises `ValidationError`

## 3. Verify

- [x] 3.1 Run `pytest tests/test_models.py -v` and confirm all tests pass
- [x] 3.2 Confirm `from src.models import *` works with no import errors from a clean Python session
