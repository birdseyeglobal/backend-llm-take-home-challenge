# Technology Stack
_Last updated: 2026-04-04_

## Summary

This is a Python 3.13.5 FastAPI backend service ("Brand Voice API") managed with Poetry. It uses SQLModel over SQLAlchemy for ORM, PostgreSQL for persistence, Alembic for schema migrations, and Uvicorn as the ASGI server. The project is a take-home coding challenge starter codebase intended to be extended with LLM integration.

## Details

### Languages

**Primary:**
- Python 3.13.5 — all application code, tests, and tooling scripts
  - `pyproject.toml` specifies `python = "3.13.5"`
  - Dockerfile uses `python:3.11-buster` / `python:3.11-slim-bookworm` (note: Docker image version lags behind declared Python version)
  - Nox sessions target `python = ["3.13.5"]` for ruff and `python = ["3.11.4"]` for mypy/test

### Runtime

**Environment:**
- CPython 3.13.5 (declared in `pyproject.toml`)
- ASGI server: Uvicorn with standard extras (`^0.24.0.post1`)
  - Production: 2 workers, port 80, JSON logging disabled via `uvicorn_disable_logging.json`
  - Development: single worker with `--reload`, port 3070 via `start_service_dev.sh`

**Package Manager:**
- Poetry (version 1.7.1 pinned in Dockerfile)
- Lockfile: `poetry.lock` present and committed

### Frameworks

**Core Web:**
- FastAPI — ASGI web framework; entry point at `app/main.py`
  - `CORSMiddleware` configured with `allow_origins=["*"]` (all origins allowed)
  - OpenAPI endpoint exposed at `/public/openapi.json` in dev mode only
  - Pagination support via `fastapi-pagination ^0.14.1`

**ORM / Data:**
- SQLModel `^0.0.27` — unified Pydantic + SQLAlchemy ORM layer; all models in `app/brand/db/models.py` and `app/base/db/models.py`
- SQLAlchemy (transitive via SQLModel) — used directly for `Engine`, `JSONB` dialect types
- Alembic `^1.13.0` — database migrations in `migrations/`
- `alembic-postgresql-enum ^1.7.0` — enum type support for Postgres in Alembic

**Validation / Settings:**
- Pydantic v2 `~2.11.9` (with email extras) — request/response schemas in `app/brand/api/schemas.py`
- `pydantic-settings ^2.1.0` — settings class in `app/base/config.py`
- `pydantic-extra-types ^2.9.0` — extended type support (e.g., `HttpUrl`)

**Resiliency:**
- tenacity `^9.1.2` — retry logic on database engine creation (`app/base/db/engine.py`), with exponential backoff (1–20s), 6 attempts

**Testing:**
- pytest `^7.4.3`
- pytest-asyncio `^0.21.1`
- pytest-cov `^4.1.0`
- pytest-timeout `^2.3.1`
- pytest-lazy-fixture `^0.6.3`
- testcontainers-postgres `^0.0.1rc1` — spins up `pgvector/pgvector:pg15` Docker container for integration tests
- FastAPI `TestClient` (via httpx) for endpoint testing

**Build / Dev Tools:**
- Nox `^2023.4.22` + nox-poetry `^1.0.3` — session runner for ruff, prettier, mypy, and pytest (`noxfile.py`)
- Ruff `^0.9.9` — linting and formatting (Black-compatible, line length 88, pyproject.toml config)
- mypy `^1.8.0` — strict type checking with pydantic plugin; targets `app` package
- debugpy `^1.8.17` — VS Code debugger attach support (`start_service_dev.sh --debug`)
- better-exceptions `^0.3.3` — enhanced tracebacks in dev
- rich `^14.2.0` — console output in dev
- time-machine `^2.19.0` — time mocking for tests

**HTTP Client:**
- httpx `^0.28.1` — async HTTP client (listed as a direct dependency; likely intended for outbound LLM calls)
- requests `^2.32.3` — sync HTTP client

**Other Utilities:**
- python-dotenv `^1.0.0` — `.env` file loading
- python-multipart `^0.0.20` — multipart form data support (FastAPI file uploads)
- sql-formatter `^0.6.2` — SQL pretty-printing (dev/tooling use)
- asyncpg `^0.30.0` — async PostgreSQL driver (installed but not yet wired to async engine in current code)
- psycopg2-binary `^2.9.9` — sync PostgreSQL driver used by the SQLAlchemy engine

### Build / Deployment

**Container:**
- Multi-stage Dockerfile:
  - Builder stage: `python:3.11-buster`, installs Poetry 1.7.1, resolves dependencies
  - Service stage: `python:3.11-slim-bookworm`, copies `.venv`, runs Uvicorn
- Production command: `uvicorn app.main:app --host 0.0.0.0 --port 80 --log-config uvicorn_disable_logging.json --workers 2`

**Database Migrations:**
- Alembic auto-applied on startup when `settings.MODE == "production"` (`app/main.py:run_migrations()`)
- Advisory lock (`pg_advisory_xact_lock(10000)`) prevents concurrent migration runs

**Configuration:**
- `pyproject.toml` — all tool config (ruff, mypy, pytest, poetry)
- `alembic.ini` — migration script location
- `.env` file loaded via python-dotenv (see INTEGRATIONS.md for env vars)

### Internal Package Source

A supplemental PyPI source is configured:
- Name: `internal`
- URL: `https://northamerica-northeast1-python.pkg.dev/birdseye-org-infra/python-internal/simple/`
- Priority: supplemental (falls back to PyPI)

This is a Google Artifact Registry endpoint suggesting Google Cloud Platform as the deployment environment.

## Notes

- `asyncpg` is installed but the current engine (`app/base/db/engine.py`) uses a synchronous `create_engine` with `psycopg2`. Async database access is not yet implemented.
- The Dockerfile builder stage does not `RUN poetry install` — it only copies `pyproject.toml` and `poetry.lock`. The `.venv` is not built in the builder. This appears to be an incomplete or intentional minimal Dockerfile (the service stage copies `${VIRTUAL_ENV}` from builder, but builder never populated it). This is likely a known stub.
- Python version mismatch: `pyproject.toml` declares `3.13.5`, Dockerfile pins `3.11`, and nox mypy/test sessions target `3.11.4`. The candidate is expected to reconcile this when extending the project.
- No LLM libraries are yet installed; the challenge instructs candidates to add LangChain, Pydantic AI, or Instructor as needed.
- `prettier` nox session references a `../prettier.config.js` (parent directory), suggesting this repo may be a subdirectory of a monorepo.
