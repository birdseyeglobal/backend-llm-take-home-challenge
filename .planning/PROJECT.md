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

### Active

- [ ] `VoiceProfile` SQLModel with all specified fields (id, brand_id FK, version, warmth, seriousness, technicality, formality, playfulness, target_demographic, style_guide, writing_example, llm_model, created_at, updated_at)
- [ ] Unique constraint on `(brand_id, version)` in VoiceProfile
- [ ] Alembic migration for voice_profile table
- [ ] `VoiceGenerateRequest` and `VoiceProfileResponse` Pydantic schemas
- [ ] LLM integration (LangChain / Pydantic AI / Instructor) for structured output
- [ ] `POST /public/api/brands/{brand_id}/voices:generate` endpoint
- [ ] Auto-versioning: each call increments version per brand
- [ ] 404 if brand not found
- [ ] At least one integration test for the endpoint
- [ ] mypy and ruff pass

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

## Constraints

- **Tech stack:** Python 3.13.5, FastAPI, Pydantic v2, SQLModel, Alembic, Postgres — must follow existing patterns
- **LLM library:** Must use LangChain, Pydantic AI, or Instructor (not raw HTTP) — add via `poetry add`
- **Code quality:** mypy (strict) and ruff must pass
- **Versioning:** VoiceProfile is immutable; each generate call creates a new version

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use Pydantic AI for LLM integration | Tightest Pydantic v2 integration, minimal boilerplate for structured output | — Pending |
| Store style_guide as JSON list | README specifies `list[str]` stored as JSONB, matches docs pattern | — Pending |
| Implement voice endpoint on brand router | README spec: `POST /brands/{id}/voices:generate` — subresource of brand | — Pending |

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
*Last updated: 2026-04-04 after initialization*
