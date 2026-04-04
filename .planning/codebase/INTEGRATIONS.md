# External Integrations
_Last updated: 2026-04-04_

## Summary

The service integrates with a PostgreSQL database (production target: likely Google Cloud AlloyDB based on engine comments) and is pre-wired for multiple LLM provider APIs. No LLM library is installed yet — the challenge scaffold defines API key settings and rate limits for four providers (OpenAI, Anthropic, Gemini, Perplexity) and instructs the implementer to add the appropriate client library. Authentication between services is present as a stub (`SKIP_AUTH` flag).

## Details

### Databases and Data Stores

**PostgreSQL:**
- Primary and only data store
- Driver: `psycopg2-binary ^2.9.9` (sync) for application; `asyncpg ^0.30.0` installed but not yet used
- ORM: SQLModel / SQLAlchemy via `app/base/db/engine.py`
- Connection string assembled in `app/base/config.py`:
  ```
  postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}
  ```
- Default development values: `localhost:5432`, user `postgres`, password `birdseye`, db `seo_service`
- Engine configured with:
  - `pool_size=4`, `max_overflow=4`
  - `pool_pre_ping=True`, `pool_use_lifo=True`
  - TCP keepalives enabled (comment: "AlloyDB is using its own managed pooling")
- Test database: `pgvector/pgvector:pg15` Docker image via testcontainers, bound to port `5439`

**No caching layer** — not detected.

**No file storage** — not detected (docs stored as JSON array of URL strings in the `brand.docs` JSONB column).

### LLM Provider APIs (Pre-wired, Not Yet Implemented)

Four LLM providers have API keys and rate limits defined in `app/base/config.py`. No SDK or client library for any of these is currently installed.

**OpenAI:**
- Env var: `OPENAI_API_KEY`
- Rate limit setting: `OPENAI_RATE_LIMIT` (default: 5000)
- Recommended client: `openai` or `langchain-openai` (per README)

**Anthropic:**
- Env var: `ANTHROPIC_API_KEY`
- Rate limit setting: `ANTHROPIC_RATE_LIMIT` (default: 4000)
- Recommended client: `anthropic` or `langchain-anthropic` (per README)

**Google Gemini:**
- Env var: `GEMINI_API_KEY`
- Rate limit setting: `GEMINI_RATE_LIMIT` (default: 7000)
- Recommended client: `google-generativeai` or `langchain-google-genai`

**Perplexity:**
- Env var: `PPLX_API_KEY`
- Rate limit setting: `PERPLEXITY_RATE_LIMIT` (default: 1000)
- Recommended client: OpenAI-compatible HTTP client

Candidate chooses which provider to use when implementing the `POST /public/api/brands/{brand_id}/voices:generate` endpoint.

### Authentication and Authorization

**Current state: stub only.**
- `SKIP_AUTH: bool = False` setting exists in `app/base/config.py`
- When `True`, auth is bypassed on routes
- No auth middleware, guards, or JWT/session validation is implemented in the codebase
- No external auth provider (e.g., Auth0, Cognito) is integrated yet

### Deployment Platform

**Likely: Google Cloud Platform (AlloyDB)**
- The engine docstring references "AlloyDB is using its own managed pooling" and "PSC/NAT idles"
- Google Artifact Registry is configured as a supplemental Python package source:
  - `https://northamerica-northeast1-python.pkg.dev/birdseye-org-infra/python-internal/simple/`
  - Region: `northamerica-northeast1` (Montreal)
- This is the only cloud-specific integration signal in the codebase

### CI/CD

No CI/CD pipeline configuration detected (no `.github/`, `.gitlab-ci.yml`, `cloudbuild.yaml`, etc. present in the repository root).

### Webhooks and Callbacks

None detected — no incoming webhook endpoints or outgoing webhook calls.

### Environment Variables

All settings are defined in `app/base/config.py` as a Pydantic `BaseSettings` class. The `.env` file is loaded at startup via `python-dotenv` (and optionally disabled with `DISABLE_DOTENV=1` for test isolation).

| Variable | Default | Purpose |
|---|---|---|
| `ENV` | `"dev"` | Environment label; enables OpenAPI JSON endpoint when `"dev"` |
| `MODE` | `"development"` | `"production"` triggers auto-migration on startup |
| `SKIP_AUTH` | `False` | Bypass route authentication (stub) |
| `POSTGRES_HOST` | `"localhost"` | PostgreSQL hostname |
| `POSTGRES_PORT` | `"5432"` | PostgreSQL port |
| `POSTGRES_USER` | `"postgres"` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `"birdseye"` | PostgreSQL password |
| `POSTGRES_DB` | `"seo_service"` | PostgreSQL database name |
| `SQLALCHEMY_DATABASE_URI` | (computed) | Assembled from above Postgres vars; not set directly |
| `GEMINI_API_KEY` | `""` | Google Gemini API key |
| `OPENAI_API_KEY` | `""` | OpenAI API key |
| `ANTHROPIC_API_KEY` | `""` | Anthropic API key |
| `PPLX_API_KEY` | `""` | Perplexity API key |
| `OPENAI_RATE_LIMIT` | `5000` | Token/request rate limit for OpenAI |
| `GEMINI_RATE_LIMIT` | `7000` | Token/request rate limit for Gemini |
| `PERPLEXITY_RATE_LIMIT` | `1000` | Token/request rate limit for Perplexity |
| `ANTHROPIC_RATE_LIMIT` | `4000` | Token/request rate limit for Anthropic |
| `DISABLE_DOTENV` | (unset) | Set to `"1"` to skip `.env` loading (used in tests) |
| `LOG_JSON_FORMAT` | `"0"` (dev) / `"1"` (prod) | JSON vs. plain log format |
| `LOG_LEVEL` | `"DEBUG"` (dev) / `"INFO"` (prod) | Logging verbosity |
| `BETTER_EXCEPTIONS` | `1` (dev script) | Enable pretty exception formatting |

**Secrets location:**
- `.env` file at project root (copied into Docker image in Dockerfile — flagged as a potential concern)
- No secrets manager integration detected

## Notes

- The Dockerfile `COPY .env ./.env` bakes the `.env` file into the container image, which is a security concern for production deployments. Secrets should be injected at runtime via environment variables or a secrets manager (e.g., Google Secret Manager).
- `SQLALCHEMY_DATABASE_URI` is a derived field (computed by `@model_validator`) and should never be set directly in `.env`.
- Rate limit settings (`OPENAI_RATE_LIMIT`, etc.) are defined but no rate limiting middleware or token-counting logic is implemented yet. These are placeholders for the LLM integration the candidate will build.
- The `asyncpg` driver is installed, suggesting the codebase may evolve toward async database operations. The current synchronous SQLModel session pattern in `app/base/api/dependencies.py` would need to be replaced with an async session if that path is taken.
- No monitoring, error tracking (e.g., Sentry), or observability tooling (e.g., OpenTelemetry) is integrated, though `OTEL_SDK_DISABLED=true` is set in the test init, suggesting OpenTelemetry may be planned or used in other services in the organization.
