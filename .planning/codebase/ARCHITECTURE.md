# Architecture

_Last updated: 2026-04-04_

## Summary

This is a synchronous, single-process Python monolith built with FastAPI. It follows a layered, feature-module pattern: each domain feature (currently `brand`) owns its own API, DB models, and business logic layers. The application connects to a PostgreSQL database managed via Alembic migrations, and is designed to be extended with LLM integrations for brand voice profile generation.

## Details

### Overall Pattern

**Monolith with feature module layering.** There is one FastAPI application (`app/main.py`) that aggregates all feature routers under a shared `/public/api` prefix. Each feature module (`brand`) contains its own sub-layers: `api/` (routing + schemas + servicer) and `db/` (models + repository).

**Layering within each feature:**
```
Route Handler → Servicer (Business Logic) → Repository (DB) → SQLModel / PostgreSQL
```

### Entry Point

**`app/main.py`**
- Creates the `FastAPI` application instance with a lifespan context manager.
- On startup: loads `.env` via `python-dotenv`; in `production` MODE, automatically runs Alembic migrations to `head`.
- Mounts all routes under `/public` prefix via `app/base/api/routes.py`.
- Adds CORS middleware (wildcard origins, all methods, all headers).
- Exposes `/public/openapi.json` in `dev` ENV for schema introspection.
- Enables `fastapi-pagination` globally.

**Development server:** `./start_service_dev.sh` runs `uvicorn app.main:app --reload` on port 3070 (configurable). Supports `--debug` flag for `debugpy` attach.

**Production container:** `Dockerfile` runs uvicorn with 2 workers on port 80 (`CMD ["uvicorn", "app.main:app", ...]`).

### Configuration Layer

**`app/base/config.py`** — `Settings` (pydantic-settings `BaseSettings`)
- Single global `settings` instance imported throughout the codebase.
- Reads from `.env` file unless `DISABLE_DOTENV=1` is set (used during testing).
- Key settings groups:
  - **Generic:** `ENV` (dev/prod), `MODE` (development/production), `SKIP_AUTH`
  - **Database:** `POSTGRES_HOST/PORT/USER/PASSWORD/DB` — assembled into `SQLALCHEMY_DATABASE_URI` via `@model_validator`
  - **LLM keys & rate limits:** `GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `PPLX_API_KEY` plus per-provider rate limit integers

### Database Layer

**`app/base/db/engine.py`**
- Creates a SQLAlchemy `Engine` from `settings.SQLALCHEMY_DATABASE_URI`.
- Uses `tenacity` retry (exponential backoff, up to 6 attempts) to handle transient connection failures.
- Tuned for AlloyDB/managed pooling: `pool_pre_ping=True`, `pool_use_lifo=True`, `pool_size=4`, `max_overflow=4`, TCP keepalive settings.

**`app/base/api/dependencies.py`** — `get_session()`
- FastAPI dependency that yields a `sqlmodel.Session` from the shared engine.
- Injected via `Depends(get_session)` in route handlers.

**`app/base/db/models.py`**
- Acts as a registry: imports all `SQLModel` subclasses from feature modules so Alembic can discover them via `SQLModel.metadata`.
- Also triggers `model_rebuild()` on all Pydantic models to resolve forward references.

### Migrations

**`migrations/`** (Alembic)
- `migrations/env.py` drives Alembic using `SQLModel.metadata` as the target.
- Uses a PostgreSQL advisory lock (`pg_advisory_xact_lock(10000)`) in online mode to prevent concurrent migration runs.
- `migrations/versions/8d2126d21d1f_init.py` creates the initial `brand` table.
- In production: `run_migrations()` in `app/main.py` lifespan calls `alembic upgrade head` at startup.

### Feature Module: `brand`

**`app/brand/api/routes.py`**
- Defines two endpoints on `APIRouter(prefix="/brands")`:
  - `POST /` → `BrandServicer.create_brand()`
  - `GET /{brand_id}` → `BrandServicer.get_brand()`
- Full URL paths: `POST /public/api/brands/`, `GET /public/api/brands/{brand_id}`

**`app/brand/api/schemas.py`**
- `BrandPostRequest`: `url: HttpUrl | None`, `docs: list[str] | None`
- `BrandResponse` (base): `id: UUID`, `url: HttpUrl | None`, `docs: list[str] | None`
- `BrandPostResponse`, `BrandGetResponse`: both inherit from `BrandResponse` (no additional fields)

**`app/brand/api/servicer.py`** — `BrandServicer`
- `create_brand()`: instantiates a `Brand` model, persists via session, returns response schema.
- `get_brand()`: fetches by PK; raises `HTTPException(404)` if not found.
- Servicer is instantiated per-request inside route handlers (no DI, no singleton).

**`app/brand/db/models.py`** — `Brand(SQLModel, table=True)`
- `id: UUID` (default `uuid4`, primary key)
- `url: str | None` (nullable)
- `docs: list[str] | None` (JSONB, nullable)
- Table name: `"brand"`

**`app/brand/db/repository.py`** — empty stub (1 line). Database logic currently lives directly in the servicer.

### Request Lifecycle

```
HTTP Request
  → FastAPI routing (/public/api/brands/...)
  → Route handler (app/brand/api/routes.py)
    → Depends(get_session) injects SQLModel Session
    → BrandServicer instantiated inline
    → Servicer calls session.get() / session.add() / session.commit()
  → Pydantic response schema serialized
HTTP Response (JSON)
```

### Error Handling

- Business-level 404s raised as `HTTPException` in the servicer layer.
- Validation errors handled automatically by FastAPI/Pydantic (422 responses).
- No global exception handlers registered.
- DB engine retries connection failures at startup via `tenacity`.

### Cross-Cutting Concerns

- **Auth:** `SKIP_AUTH` setting exists; no auth middleware is currently wired up.
- **CORS:** Wildcard (`*`) allow-all, registered globally in `app/main.py`.
- **Pagination:** `fastapi-pagination` added globally; not yet applied to any route.
- **Logging:** No structured logging framework is wired in the app code. Uvicorn logging is suppressed in production via `uvicorn_disable_logging.json`.

## Notes

- `app/brand/db/repository.py` is an empty stub — the servicer directly accesses the session. The README instructs implementing new features using the servicer/repository pattern, but the existing code does not yet use the repository.
- `app/brand/api/dependencies.py` is also empty — the brand module has no feature-specific dependencies beyond the shared `get_session`.
- `app/base/api/schemas.py` is empty — the file exists but has no schemas defined.
- The `Dockerfile` uses Python 3.11 in the builder/runtime stages, but `pyproject.toml` specifies Python `3.13.5` and `noxfile.py` references both `3.13.5` (ruff) and `3.11.4` (mypy/test). This is a version inconsistency.
- LLM API keys and rate limits are pre-wired in `Settings` but no LLM integration code exists yet — the `VoiceProfile` endpoint is the candidate's task.
