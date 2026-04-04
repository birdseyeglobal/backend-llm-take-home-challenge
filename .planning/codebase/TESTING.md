# Testing Patterns

_Last updated: 2026-04-04_

## Summary

Tests use pytest with a real PostgreSQL database spun up via `testcontainers`. There is no mocking of the database layer — integration tests run against a fully migrated Postgres instance using Alembic. There are two test files covering basic API routing and brand CRUD operations.

## Details

### Test Framework

**Runner:** pytest `^7.4.3`

**Key plugins installed (from `pyproject.toml` dev dependencies):**
- `pytest-cov ^4.1.0` — coverage reporting
- `pytest-asyncio ^0.21.1` — async test support
- `pytest-timeout ^2.3.1` — per-test timeouts
- `pytest-lazy-fixture ^0.6.3` — use fixtures inside `@pytest.mark.parametrize`

**No `[tool.pytest.ini_options]` section** is present in `pyproject.toml`. Pytest is invoked with explicit CLI flags from `noxfile.py`.

### How to Run Tests

Via nox (recommended):
```bash
nox -s test
```

This runs:
```bash
py.test -vvv --tb=native --timeout=300 --cov=app --cov-report=term --cov-report=html tests/
```

To run a specific test file directly (requires Poetry environment active):
```bash
poetry run py.test -vvv --tb=native tests/test_brand.py
```

**Coverage target:** No minimum threshold is configured. Coverage is measured over the `app` package and reported to terminal and HTML (`--cov-report=term --cov-report=html`).

**Timeout:** 300 seconds per test (`--timeout=300`).

### Test File Organization

```
tests/
├── __init__.py         # Package marker
├── init.py             # Pre-setup: sets env vars before any imports run
├── conftest.py         # Session-scoped fixtures: containers, engine, client
├── test_api.py         # Route-level smoke tests
└── test_brand.py       # Brand CRUD integration tests
```

All test files live in a flat `tests/` directory at the project root. There is no subdirectory structure (e.g., no `tests/unit/` or `tests/integration/` split). Tests are **not co-located** with application code.

### Pre-Test Initialization (`tests/init.py`)

`tests/init.py` is a special module that must be imported first. It sets environment variables before any application code loads:

```python
POSTGRES_CONTAINER_PORT = 5439
os.environ.setdefault("POSTGRES_PORT", str(POSTGRES_CONTAINER_PORT))
os.environ["DISABLE_DOTENV"] = "1"          # Prevents .env file loading during tests
os.environ.setdefault("OTEL_SDK_DISABLED", "true")
os.environ.setdefault("SKIP_PORT_CHECK", "1")
```

`conftest.py` enforces this via its first line:
```python
from .init import POSTGRES_CONTAINER_PORT  # noqa: I001
```

The `# noqa: I001` suppresses the isort warning since this import must appear before stdlib/third-party imports.

### Fixtures (`tests/conftest.py`)

All core fixtures are **session-scoped** to avoid re-creating the database container per test.

**`ensure_ports_free` (session, autouse=True):**
Checks that required ports (5439 for Postgres) are not already in use before starting the container. Can be bypassed with `SKIP_PORT_CHECK=1`.

**`postgres_container` (session):**
Starts a `pgvector/pgvector:pg15` Docker container bound to port 5439. Waits for the Postgres ready-log before yielding.

```python
postgres = PostgresContainer(
    image="pgvector/pgvector:pg15",
    user="postgres",
    password="birdseye",
    dbname="seo_service",
    port=5432,
)
```

**`engine` (session):**
Creates a SQLAlchemy engine pointing at the test container and runs Alembic migrations to `head`. This ensures tests run against a fully migrated schema.

```python
alembic_config = Config("alembic.ini")
alembic_config.attributes["configure_logger"] = False
command.upgrade(alembic_config, "head")
command.check(alembic_config)
```

Note: A `TODO` comment marks the intent to load mock data here (`# TODO: load mock data into db`), which is not yet implemented.

**`session` (function-scoped, name="session"):**
Yields a SQLModel `Session` and rolls back any open transaction on teardown:

```python
@pytest.fixture(name="session")
def session_fixture(engine: Engine) -> Generator[Session, None, None]:
    with database_session(engine) as session:
        try:
            yield session
        finally:
            if session.in_transaction():
                session.rollback()
            session.close()
```

**`client` (function-scoped, name="client"):**
Creates a FastAPI `TestClient` with the production `get_session` dependency overridden to use the test database session. Clears overrides on teardown:

```python
@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    def get_session_override() -> Session:
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
```

### Test Types

**Integration tests only.** All tests exercise the full HTTP → FastAPI → SQLModel → PostgreSQL stack. There are no unit tests, no mocking of service or repository layers, and no isolated function-level tests.

**`tests/test_api.py` — Route smoke tests:**
Uses `@pytest.mark.parametrize` to verify that OpenAPI and docs routes return HTTP 200:

```python
@pytest.mark.parametrize(
    "route,expected_status_code",
    [
        ("openapi.json", 200),
        ("docs", 200),
    ],
    ids=["openapi", "docs"],
)
def test_routes(client: TestClient, route: str, expected_status_code: int) -> None:
    """Test basic fast api routes"""
    response = client.get(f"/{route}")
    assert response.status_code == expected_status_code
```

**`tests/test_brand.py` — Brand CRUD integration test:**
Single test function that exercises POST and GET for the brand resource end-to-end, then cleans up by deleting the created record via the session directly:

```python
def test_api(client: TestClient, session: Session) -> None:
    post_response = client.post("public/api/brands", json={...})
    assert post_response.status_code == 200
    # ... assertions on JSON response ...

    brand = session.get(Brand, post_response_json.get("id"))
    assert brand is not None
    # ... assertions on DB state ...

    get_response = client.get(f"public/api/brands/{post_response_json.get('id')}")
    # ... assertions ...

    session.delete(brand)
    session.commit()
```

### Mocking Patterns

**Database:** Not mocked. Tests use a real PostgreSQL instance via testcontainers. The only substitution is the FastAPI dependency override (`app.dependency_overrides`) to inject the test session into the application.

**External services (LLMs, etc.):** Not mocked. No mock library usage (e.g., `unittest.mock`, `pytest-mock`) appears in any test file. This means tests that exercise any LLM API calls would make real network requests (or fail if keys are absent).

**No use of `monkeypatch`, `MagicMock`, `patch`, or `responses` library** is present in the current test suite.

### Coverage

Coverage is collected over the `app` package. Reports are written to:
- **Terminal:** `--cov-report=term`
- **HTML:** `--cov-report=html` (output directory defaults to `htmlcov/`)

No minimum coverage threshold is enforced (no `--cov-fail-under` flag).

## Notes

- The `postgres_container` fixture does not run within the `with postgres:` context manager pattern used by testcontainers — it uses `with postgres.with_bind_ports(5432, 5439):` instead, which is the correct pattern for fixed-port binding.
- The `session` fixture is function-scoped but `engine` is session-scoped. This means one DB engine/schema is shared across all tests, but each test gets a fresh session. Tests must manually clean up data they create (as `test_brand.py` does with `session.delete(brand); session.commit()`).
- `pytest-asyncio` is installed but no `async def test_*` functions appear in the current test suite, suggesting async tests are anticipated but not yet written.
- `pytest-lazy-fixture` is installed but not used in current tests.
- The `yolando-test/` directory at the project root is a Python virtual environment directory (not a test directory) and contains no test files.
