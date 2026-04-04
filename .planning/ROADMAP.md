# Roadmap: Brand Voice API
**Milestone:** v1 — VoiceProfile Generation
**Goal:** Working POST /public/api/brands/{brand_id}/voices:generate endpoint with LLM integration, versioned storage, and passing tests

---

## Phase 1: Data Foundation
**Goal:** VoiceProfile SQLModel, Alembic migration, and API schemas in place — all subsequent phases can build on this.

### Requirements
- DATA-01: VoiceProfile SQLModel with all fields
- DATA-02: Unique constraint on (brand_id, version)
- DATA-03: Alembic migration creates voice_profile table
- DATA-04: VoiceProfile imported in app/base/db/models.py
- API-01: VoiceGenerateRequest schema
- API-02: VoiceProfileResponse schema

### Deliverables
- `app/brand/db/models.py` — VoiceProfile model added
- `migrations/versions/XXXX_add_voice_profile.py` — new migration
- `app/brand/api/schemas.py` — request/response schemas added

**Plans:** 1 plan

Plans:
- [ ] 01-01-PLAN.md — VoiceProfile model, model registry update, API schemas, Alembic migration

### Success Criteria
- [ ] `alembic upgrade head` succeeds
- [ ] VoiceProfile table exists with all columns and unique constraint
- [ ] Schemas importable with no mypy errors

---

## Phase 2: LLM Integration & Endpoint
**Goal:** The generate endpoint is wired, calls the LLM, stores a versioned profile, and returns the correct response.

### Requirements
- LLM-01: LLM framework dependency added
- LLM-02: LLM called with writing samples, returns structured data
- LLM-03: Float metrics constrained 0–1
- LLM-04: style_guide returned as 3–5 bullet strings
- LLM-05: writing_example returned as 3–6 sentences
- API-03: POST endpoint registered
- API-04: 404 if brand not found
- API-05: 422 for invalid request body
- API-06: version auto-increments per brand

### Deliverables
- `pyproject.toml` + `poetry.lock` — LLM library added
- `app/base/config.py` — PYDANTIC_AI_GATEWAY_API_KEY setting
- `app/brand/api/schemas.py` — VoiceProfileLLMResult schema added
- `app/brand/api/servicer.py` — generate_voice_profile() method
- `app/brand/api/routes.py` — new route registered

**Plans:** 1 plan

Plans:
- [ ] 02-01-PLAN.md — Install pydantic-ai, add gateway key setting, VoiceProfileLLMResult schema, generate_voice_profile() servicer method, POST /{brand_id}/voices:generate route

### Success Criteria
- [ ] POST /public/api/brands/{brand_id}/voices:generate returns 200 with valid body
- [ ] Second call to same brand returns version 2
- [ ] Missing brand returns 404
- [ ] Missing writing_samples returns 422

---

## Phase 3: Tests & Quality
**Goal:** At least one passing integration test; mypy and ruff both clean.

### Requirements
- TEST-01: Integration test for happy path
- TEST-02: Test asserts version == 1 and correct field shapes
- QUAL-01: mypy app passes
- QUAL-02: ruff check passes

### Deliverables
- `tests/test_voice.py` — integration tests

### Success Criteria
- [ ] `pytest tests/test_voice.py` exits 0
- [ ] `mypy app` exits 0
- [ ] `ruff check .` exits 0

---

## Traceability

| Requirement | Phase |
|-------------|-------|
| DATA-01 | Phase 1 |
| DATA-02 | Phase 1 |
| DATA-03 | Phase 1 |
| DATA-04 | Phase 1 |
| API-01 | Phase 1 |
| API-02 | Phase 1 |
| LLM-01 | Phase 2 |
| LLM-02 | Phase 2 |
| LLM-03 | Phase 2 |
| LLM-04 | Phase 2 |
| LLM-05 | Phase 2 |
| API-03 | Phase 2 |
| API-04 | Phase 2 |
| API-05 | Phase 2 |
| API-06 | Phase 2 |
| TEST-01 | Phase 3 |
| TEST-02 | Phase 3 |
| QUAL-01 | Phase 3 |
| QUAL-02 | Phase 3 |

**Coverage:** 19/19 v1 requirements mapped ✓
