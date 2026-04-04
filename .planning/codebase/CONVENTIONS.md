# Coding Conventions

_Last updated: 2026-04-04_

## Summary

The codebase uses Python 3.13 with strict type checking enforced by mypy and code formatting/linting via Ruff. All naming follows standard Python conventions (snake_case for functions/variables, PascalCase for classes). Docstrings are used minimally — primarily in test fixtures and nox sessions — but not required throughout application code.

## Details

### Formatting Tool

**Ruff** is the single tool for both formatting and linting, configured in `pyproject.toml` under `[tool.ruff]` and `[tool.ruff.format]`.

Key formatting settings:
- Line length: **88 characters** (same as Black)
- Indent width: **4 spaces**
- Quote style: **double quotes**
- Line endings: **auto-detected**
- Magic trailing commas: **respected** (`skip-magic-trailing-comma = false`)
- Target Python version: `py311` (though runtime is 3.13.5)

Running Ruff via nox (defined in `noxfile.py`):
```bash
nox -s ruff           # formats then checks
```

Ruff is run in two passes in `noxfile.py`:
1. `ruff format . --config ./pyproject.toml` (auto-formats)
2. `ruff check --fix . --config ./pyproject.toml` (auto-fixes lint issues)
3. Both are then re-run in check-only mode to confirm compliance.

### Linting Rules

Configured in `pyproject.toml` under `[tool.ruff.lint]`:

| Rule Set | Code | Description |
|----------|------|-------------|
| Pyflakes | `F` | Undefined names, unused imports |
| pycodestyle errors | `E4`, `E7`, `E9` | Syntax/import errors |
| isort | `I` | Import ordering |
| pyupgrade | `UP` | Modern Python idioms |
| Ruff-native | `RUF` | Ruff-specific rules |
| McCabe complexity | `C90` | Cyclomatic complexity |
| FastAPI | `FAST` | FastAPI-specific checks |
| Bugbear | `B904` | `raise X from Y` inside except blocks |

Per-file ignores:
- `__init__.py`: `F401` (unused imports) is ignored — barrel re-exports are permitted.

### Type Checking — mypy

mypy is configured in `pyproject.toml` under `[tool.mypy]` in **strict mode**:

```toml
[tool.mypy]
strict = true
disallow_untyped_calls = true
disallow_untyped_defs = true
warn_return_any = true
ignore_missing_imports = true
show_error_codes = true
disable_error_code = ["no-any-return"]
plugins = ["pydantic.mypy"]
packages = ["app"]
```

Pydantic mypy plugin is active with:
- `init_forbid_extra = true`
- `init_typed = true`
- `warn_required_dynamic_aliases = true`

All functions must have full type annotations. Return types are always declared. `Any` return types are suppressed from errors via `disable_error_code = ["no-any-return"]`.

### Naming Conventions

**Files:**
- snake_case for all Python module files: `dependencies.py`, `servicer.py`, `routes.py`, `schemas.py`, `models.py`, `repository.py`
- Directories mirror domain/layer structure: `app/brand/api/`, `app/brand/db/`

**Classes:**
- PascalCase: `BrandServicer`, `BrandPostRequest`, `BrandPostResponse`, `BrandGetResponse`, `BrandResponse`, `Brand`, `Settings`
- Request/response schemas use the pattern `{Resource}{Method}Request` / `{Resource}{Method}Response`
- Base response schemas use plain `{Resource}Response` and are extended via inheritance

**Functions and methods:**
- snake_case: `create_brand`, `get_brand`, `get_session`, `create_engine_with_retry`, `run_migrations`
- FastAPI route handlers are named after their HTTP action: `create_brand` for POST, `get_brand` for GET

**Variables:**
- snake_case: `brand_post_request`, `brand_id`, `alembic_config`
- Constants: UPPER_SNAKE_CASE: `POSTGRES_IMAGE`, `POSTGRES_USER`, `POSTGRES_CONTAINER_PORT`, `API_V1_STR`

**Config fields (pydantic-settings):**
- UPPER_SNAKE_CASE matching environment variable names: `POSTGRES_HOST`, `GEMINI_API_KEY`, `SQLALCHEMY_DATABASE_URI`

### Import Ordering

isort (`I` rule set in Ruff) enforces import ordering:
- Standard library imports first
- Third-party imports second
- Local `app.*` imports last

The `# noqa: I001` comment appears in `tests/conftest.py` to suppress an import ordering error where `from .init import POSTGRES_CONTAINER_PORT` must run before other imports to set environment variables before app modules load.

### Documentation and Comments

Docstrings are used selectively:
- **nox session functions** all have one-line docstrings (`"""Run the linter."""`, `"""Run the type checker."""`)
- **pytest fixtures** use one-line docstrings for clarity (`"""Setup postgres container"""`)
- **Application code** (routes, servicers, models, config) has no docstrings
- **Inline comments** are used for non-obvious logic (e.g., pool configuration rationale in `app/base/db/engine.py`)

No enforced docstring requirement is configured in Ruff or mypy.

### Error Handling

FastAPI's `HTTPException` is used for API-layer errors. Pattern in `app/brand/api/servicer.py`:

```python
from fastapi import HTTPException

brand = session.get(Brand, brand_id)
if brand is None:
    raise HTTPException(status_code=404, detail="Brand not found")
```

No custom exception classes are defined. No global exception handler middleware is registered in `app/main.py`.

Database retries are handled at engine creation time via `tenacity` in `app/base/db/engine.py`:

```python
@retry(wait=wait_exponential(min=1, max=20), stop=stop_after_attempt(6))
def create_engine_with_retry(**kwargs: Any) -> Engine:
    ...
```

### Dependency Injection

FastAPI's `Depends` is used for session injection. Dependencies live in `app/{module}/api/dependencies.py`. Route signatures use `Annotated` for clarity:

```python
def create_brand(
    brand: BrandPostRequest, session: Annotated[Session, Depends(get_session)]
) -> BrandPostResponse:
```

### Schema Design

Request/response schemas are **pure Pydantic `BaseModel`** classes, kept separate from SQLModel table classes. Response schemas use inheritance to reduce duplication:

```python
class BrandResponse(BaseModel):
    id: UUID
    url: HttpUrl | None
    docs: list[str] | None

class BrandPostResponse(BrandResponse):
    pass

class BrandGetResponse(BrandResponse):
    pass
```

### Configuration

Settings are loaded from environment variables using `pydantic-settings` (`BaseSettings`). The singleton `settings` object is imported wherever config is needed (`from app.base.config import settings`). `.env` file loading can be disabled via `DISABLE_DOTENV=1` env var, which is used during tests.

### Prettier (non-Python)

`noxfile.py` includes a `prettier` session for non-Python files, pointing to a `prettier.config.js` in the parent directory (`../prettier.config.js`). This config file is not present in this repo, suggesting Prettier is used across a monorepo context.

## Notes

- The `[tool.ruff]` `target-version` is set to `py311` even though the runtime and poetry dependency require Python `3.13.5`. This is a minor inconsistency.
- `app/brand/db/repository.py` and `app/base/api/schemas.py` and `app/brand/api/dependencies.py` are empty (1-line files), indicating scaffolding stubs that have not been implemented.
- The `prettier` nox session references `../prettier.config.js` — a config outside this repo's root — implying this project is part of a larger monorepo that is not present here.
- No structured logging library is used; `app/main.py` relies on uvicorn's built-in logging.
