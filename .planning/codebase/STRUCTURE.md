# Codebase Structure

_Last updated: 2026-04-04_

## Summary

The project is a single-repo Python FastAPI service. Application code lives in `app/`, tests in `tests/`, and database migrations in `migrations/`. Feature code is organized into domain modules (`brand/`) under `app/`, each with its own `api/` and `db/` subdirectories. Configuration and shared infrastructure live in `app/base/`.

## Details

### Directory Layout

```
backend-llm-take-home-challenge/
├── app/                          # Application source code
│   ├── __init__.py
│   ├── main.py                   # FastAPI app factory, lifespan, router mounting
│   ├── base/                     # Shared infrastructure (config, DB engine, base routes)
│   │   ├── __init__.py
│   │   ├── config.py             # pydantic-settings Settings class (singleton: settings)
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py   # Shared FastAPI dependencies (get_session)
│   │   │   ├── routes.py         # Top-level APIRouter; aggregates feature routers
│   │   │   └── schemas.py        # Empty — base schema registry (currently unused)
│   │   └── db/
│   │       ├── engine.py         # SQLAlchemy engine creation with retry logic
│   │       └── models.py         # SQLModel metadata registry; imports all table models
│   └── brand/                    # "Brand" feature module
│       ├── __init__.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── dependencies.py   # Empty stub
│       │   ├── routes.py         # Brand endpoints (POST /, GET /{id})
│       │   ├── schemas.py        # Pydantic request/response schemas
│       │   └── servicer.py       # BrandServicer — business logic
│       └── db/
│           ├── __init__.py
│           ├── models.py         # Brand SQLModel table definition
│           └── repository.py     # Empty stub — intended for DB query logic
├── migrations/                   # Alembic database migration files
│   ├── README
│   ├── env.py                    # Alembic environment; uses SQLModel.metadata
│   ├── script.py.mako            # Migration script template
│   └── versions/
│       └── 8d2126d21d1f_init.py  # Initial migration: creates brand table
├── tests/                        # Pytest test suite
│   ├── __init__.py
│   ├── init.py                   # Pre-test env setup (port, DISABLE_DOTENV)
│   ├── conftest.py               # Session-scoped fixtures: postgres container, engine, client
│   ├── test_api.py               # Tests for generic FastAPI routes (openapi, docs)
│   └── test_brand.py             # Integration tests for brand endpoints
├── .planning/                    # GSD planning documents
│   └── codebase/
├── .env.example                  # Template for required environment variables
├── .gitignore
├── alembic.ini                   # Alembic configuration
├── Dockerfile                    # Multi-stage Docker build (builder + service)
├── noxfile.py                    # Nox automation: ruff, mypy, test sessions
├── pyproject.toml                # Poetry deps, ruff/mypy configuration
├── poetry.lock                   # Locked dependency versions
├── README.md                     # Challenge spec and codebase walkthrough
├── start_service_dev.sh          # Dev runner: uvicorn with optional --debug/port args
└── uvicorn_disable_logging.json  # Uvicorn log config (suppresses default logs in prod)
```

### Key File Roles

**`app/main.py`**
- Single application factory. Creates `FastAPI` instance, registers CORS middleware, mounts `/public` router, enables pagination. Runs Alembic migrations at startup in production mode.

**`app/base/config.py`**
- Defines `Settings` (pydantic-settings). Imported as the singleton `settings` throughout the app. Holds DB connection params, LLM API keys, rate limits, and environment flags.

**`app/base/api/routes.py`**
- Top-level `APIRouter` with prefix `/api`. Imports and includes feature routers. This is the single file to add a new feature's router to.

**`app/base/api/dependencies.py`**
- Defines `get_session()` — the shared `Depends` injection for SQLModel sessions. All route handlers that need DB access import from here.

**`app/base/db/engine.py`**
- Creates the shared `engine` singleton with retry and connection tuning. All DB sessions derive from this engine.

**`app/base/db/models.py`**
- SQLModel/Pydantic model registry. Must import every table model so Alembic can see them via `SQLModel.metadata`. **Add imports of new models here** when creating new DB tables.

**`app/brand/api/routes.py`**
- Defines brand-specific endpoints. **Add new brand sub-endpoints here** (e.g., `POST /{brand_id}/voices:generate`).

**`app/brand/api/schemas.py`**
- Pydantic request/response types for brand endpoints. **Add new request/response models here** for any new brand endpoints.

**`app/brand/api/servicer.py`**
- `BrandServicer` class containing business logic. **Add new service methods here** following the same pattern (`method(request_schema, session) -> response_schema`).

**`app/brand/db/models.py`**
- SQLModel table definitions for brand domain. **Add new table models here** (e.g., `VoiceProfile`).

**`app/brand/db/repository.py`**
- Currently an empty stub. Intended for DB query methods (complex queries, bulk operations). Simple CRUD in the servicer is acceptable for now.

**`migrations/env.py`**
- Alembic entrypoint. Uses `SQLModel.metadata` from `app/base/db/models.py`. Uses advisory lock to prevent concurrent migrations.

**`tests/conftest.py`**
- All session-scoped fixtures: spins up a `testcontainers` PostgreSQL Docker container, creates an engine, runs migrations, provides `TestClient` with session override.

**`tests/init.py`**
- Executed before any pytest import. Sets `DISABLE_DOTENV=1` and configures the test Postgres port to `5439`.

### Configuration Files

| File | Purpose |
|---|---|
| `pyproject.toml` | Poetry dependencies, ruff lint/format rules, mypy strict settings |
| `alembic.ini` | Alembic configuration (migration script location, DB URL placeholder) |
| `noxfile.py` | Nox sessions: `ruff` (lint+format), `mypy` (type check), `test` (pytest+coverage) |
| `.env.example` | Documents required environment variables (never committed with real values) |
| `uvicorn_disable_logging.json` | Overrides uvicorn log config in production to suppress default access logs |
| `Dockerfile` | Multi-stage: `builder` installs deps with Poetry; `service` copies venv and app source |

### Naming Conventions

**Files:**
- Feature modules: `snake_case` directory names matching the domain noun (`brand/`)
- Within feature: fixed sub-structure `api/` and `db/` directories always present
- Servicer file always named `servicer.py`; repository always `repository.py`

**Classes:**
- SQLModel tables: `PascalCase` noun (e.g., `Brand`)
- Servicers: `{Feature}Servicer` (e.g., `BrandServicer`)
- Pydantic schemas: `{Resource}{Verb}Request` / `{Resource}{Verb}Response` (e.g., `BrandPostRequest`, `BrandGetResponse`)

### Where to Add New Code

**New endpoint on an existing feature (e.g., brand):**
1. Add request/response schemas to `app/brand/api/schemas.py`
2. Add business logic method to `app/brand/api/servicer.py`
3. Add route handler to `app/brand/api/routes.py`

**New database model (table):**
1. Define `class MyModel(SQLModel, table=True)` in `app/brand/db/models.py` (or the relevant feature's `db/models.py`)
2. Import it in `app/base/db/models.py` so Alembic sees it
3. Run `alembic revision --autogenerate -m "description"` to generate migration
4. Run `alembic upgrade head` to apply

**New feature module (beyond brand):**
1. Create `app/{feature}/` with sub-dirs `api/` and `db/`
2. Add `__init__.py` files throughout
3. Create `api/routes.py`, `api/schemas.py`, `api/servicer.py`, `api/dependencies.py`
4. Create `db/models.py`, `db/repository.py`
5. Import the new feature router in `app/base/api/routes.py`
6. Import new models in `app/base/db/models.py`

**New test:**
- Integration tests go in `tests/test_{feature}.py`
- Use `client: TestClient` and `session: Session` fixtures from `conftest.py`
- No unit test infrastructure is present; existing tests are all integration-style

### Special Directories

**`yolando-test/`**
- A Python virtualenv directory committed to the repo (contains `bin/`, `lib/python3.13/site-packages/`). This is a local venv artifact and should not be referenced directly. Generated, should not be committed.

**`.planning/codebase/`**
- GSD planning documents. Not generated by build tooling; committed as part of the development workflow.

**`migrations/versions/`**
- Alembic migration scripts. Generated by `alembic revision --autogenerate`. Committed to version control.

## Notes

- `yolando-test/` appears to be a virtual environment directory that was committed to the repo accidentally. It contains installed packages under `lib/python3.13/site-packages/` and should be in `.gitignore`.
- `app/brand/db/repository.py` and `app/brand/api/dependencies.py` are both empty stubs (1-line files). The README references the repository pattern, but the existing servicer code skips it and talks to the session directly.
- `app/base/api/schemas.py` is also empty — it exists as a placeholder but defines nothing.
- Python version inconsistency: `Dockerfile` uses `python:3.11`, `pyproject.toml` specifies `python = "3.13.5"`, and `noxfile.py` uses both `"3.13.5"` (ruff) and `"3.11.4"` (mypy, test).
