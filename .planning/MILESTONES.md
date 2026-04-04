# Milestones

## v1.0 VoiceProfile Generation (Shipped: 2026-04-04)

**Phases completed:** 3 phases, 3 plans

**Key accomplishments:**

1. VoiceProfile SQLModel with 14 fields, unique constraint on (brand_id, version), and CASCADE FK to brand
2. Alembic migration creates voice_profile table with all columns and constraints
3. Pydantic AI integration via pydantic-ai-slim with structured VoiceProfileLLMResult output schema
4. POST /public/api/brands/{brand_id}/voices:generate endpoint with auto-versioning, 404/422 guards
5. Integration tests covering happy path, 404 (unknown brand), and 422 (missing writing_samples)
6. mypy strict-mode pass on 19 source files; ruff clean

---
