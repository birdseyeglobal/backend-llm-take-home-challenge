# Project State: Brand Voice API

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-04)

**Core value:** Working POST /public/api/brands/{brand_id}/voices:generate endpoint with LLM integration, versioned storage, and passing tests
**Current focus:** Phase 1 — Data Foundation

## Current Status

**Phase:** Pre-execution (planning complete)
**Milestone:** v1 — VoiceProfile Generation

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-04 | Follow existing servicer pattern (no repository) | Repository is an empty stub; existing code puts DB logic in servicer |
| 2026-04-04 | Use Pydantic AI for LLM | Tightest Pydantic v2 integration, minimal boilerplate |
| 2026-04-04 | 3-phase coarse roadmap | Small focused scope; 1 hour session |

## Notes

- This is a brownfield codebase — existing Brand CRUD must not be broken
- LLM API keys are pre-wired in Settings (OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY)
- Tests use testcontainers (Docker required)
- mypy is strict — all new code must be fully typed

---
*Initialized: 2026-04-04*
