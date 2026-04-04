# Brand Voice API

## What This Is

A FastAPI backend service that generates brand voice profiles using LLMs. Given a brand and a set of writing samples, it analyzes the samples and produces structured voice metrics (warmth, seriousness, technicality, formality, playfulness) plus qualitative outputs (target demographic, style guide, writing example). This is a live coding interview challenge requiring LLM integration on top of an existing brand CRUD starter codebase.

## Core Value

A working `POST /public/api/brands/{brand_id}/voices:generate` endpoint that calls an LLM, stores a versioned `VoiceProfile` in the database, and returns structured results — following the existing codebase patterns.

## Requirements

### Validated

- ✓ Brand creation endpoint (`POST /public/api/brands/`) — existing
- ✓ Brand retrieval endpoint (`GET /public/api/brands/{brand_id}`) — existing
- ✓ FastAPI + SQLModel + PostgreSQL + Alembic stack — existing
- ✓ Pytest test infrastructure with testcontainers — existing
- ✓ `VoiceProfile` SQLModel with all 14 specified fields — v1.0
- ✓ Unique constraint on `(brand_id, version)` — v1.0
- ✓ Alembic migration for voice_profile table — v1.0
- ✓ `VoiceGenerateRequest` and `VoiceProfileResponse` schemas — v1.0
- ✓ Pydantic AI integration for structured LLM output — v1.0
- ✓ `POST /public/api/brands/{brand_id}/voices:generate` endpoint — v1.0
- ✓ Auto-versioning per brand — v1.0
- ✓ 404 if brand not found — v1.0
- ✓ Integration tests (happy path, 404, 422) — v1.0
- ✓ mypy and ruff pass — v1.0

### Active

(None — v2.0 requirements to be defined)

### Deferred to v2.0

- [ ] Voice profile retrieval endpoints (`GET /brands/{id}/voices`, `GET /brands/{id}/voices/{version}`)
- [ ] Rate limiting on generate endpoint
- [ ] Auth middleware wiring
- [ ] `style_guide` length validator (3–5 items, currently prompt-only)
- [ ] `writing_example` sentence count validator (3–6, currently prompt-only)
- [ ] Test for version increment on second call (version == 2)

### Out of Scope

- Auth middleware — SKIP_AUTH exists, not wired; out of scope for this challenge
- Async engine — sync SQLModel sessions are fine for this scope
- Rate limiting — rate limit config exists but not wired; not required
- Full test coverage for all error paths — "at least one working test" is the bar
- Custom LLM prompt engineering — simple, clear prompt is sufficient

## Context

- Interview take-home challenge; implementation must be complete within 1 hour during live session
- Existing codebase: `app/brand/` feature module with `api/` (routes, schemas, servicer) and `db/` (models, repository) layers
- LLM API keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`) are pre-wired in Settings
- `app/brand/db/repository.py` is an empty stub — servicer can talk directly to session (existing pattern)
- The README explicitly says to follow existing patterns for consistency

**v1.0 shipped state:** ~200 LOC added across `app/brand/` (models, schemas, servicer, routes). Pydantic AI gateway integration via `pydantic-ai-slim`. Migration `a1b2c3d4e5f6`. 3 integration tests. mypy and ruff both clean.

## Constraints

- **Tech stack:** Python 3.13.5, FastAPI, Pydantic v2, SQLModel, Alembic, Postgres — must follow existing patterns
- **LLM library:** Must use LangChain, Pydantic AI, or Instructor (not raw HTTP) — add via `poetry add`
- **Code quality:** mypy (strict) and ruff must pass
- **Versioning:** VoiceProfile is immutable; each generate call creates a new version

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use Pydantic AI for LLM integration | Tightest Pydantic v2 integration, minimal boilerplate for structured output | ✓ Good |
| Store style_guide as JSON list | README specifies `list[str]` stored as JSONB, matches docs pattern | ✓ Good |
| Implement voice endpoint on brand router | README spec: `POST /brands/{id}/voices:generate` — subresource of brand | ✓ Good |
| `llm_model` in request is a record/label field | Model used for inference is internally configured; caller label is stored in DB and echoed in response — not used to route the LLM call | ✓ Good |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-04 after v1.0 milestone*
