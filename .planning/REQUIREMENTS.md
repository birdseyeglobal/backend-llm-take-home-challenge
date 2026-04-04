# Requirements: Brand Voice API

**Defined:** 2026-04-04
**Core Value:** A working `POST /public/api/brands/{brand_id}/voices:generate` endpoint that calls an LLM, stores a versioned VoiceProfile, and returns structured results.

## v1 Requirements

### Data Model

- [ ] **DATA-01**: `VoiceProfile` SQLModel table exists with fields: `id (UUID)`, `brand_id (UUID FK → brand.id)`, `version (int)`, `warmth (float)`, `seriousness (float)`, `technicality (float)`, `formality (float)`, `playfulness (float)`, `target_demographic (str)`, `style_guide (list[str] stored as JSON)`, `writing_example (str)`, `llm_model (str)`, `created_at`, `updated_at`
- [ ] **DATA-02**: Unique constraint on `(brand_id, version)` in `voice_profile` table
- [ ] **DATA-03**: Alembic migration creates the `voice_profile` table and all constraints
- [ ] **DATA-04**: `VoiceProfile` model imported in `app/base/db/models.py` (Alembic discovery)

### API

- [ ] **API-01**: `VoiceGenerateRequest` schema with `writing_samples: list[str]` and `llm_model: str`
- [ ] **API-02**: `VoiceProfileResponse` schema with all VoiceProfile fields
- [ ] **API-03**: `POST /public/api/brands/{brand_id}/voices:generate` endpoint registered and reachable
- [ ] **API-04**: Returns 404 if `brand_id` does not exist
- [ ] **API-05**: Returns 422 for invalid/missing request body fields
- [ ] **API-06**: `version` auto-increments per brand (first profile = 1, second = 2, etc.)

### LLM Integration

- [ ] **LLM-01**: LLM framework dependency added to `pyproject.toml` (LangChain, Pydantic AI, or Instructor)
- [ ] **LLM-02**: LLM is called with writing samples and returns structured voice profile data
- [ ] **LLM-03**: All float metrics (warmth, seriousness, technicality, formality, playfulness) are constrained to 0–1 range
- [ ] **LLM-04**: `style_guide` returned as a list of 3–5 bullet strings
- [ ] **LLM-05**: `writing_example` returned as 3–6 sentences

### Tests & Quality

- [ ] **TEST-01**: At least one integration test for the happy path of `POST /brands/{id}/voices:generate`
- [ ] **TEST-02**: Integration test asserts `version == 1` for first profile and correct field shapes
- [ ] **QUAL-01**: `mypy app` passes with no errors
- [ ] **QUAL-02**: `ruff check .` passes with no errors

## v2 Requirements

### Enhancements

- **ENH-01**: Retrieve existing voice profiles (`GET /brands/{id}/voices`)
- **ENH-02**: Get specific version (`GET /brands/{id}/voices/{version}`)
- **ENH-03**: Rate limiting on the generate endpoint (config already exists in settings)
- **ENH-04**: Auth middleware (SKIP_AUTH flag suggests planned but not implemented)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Async engine (asyncpg) | Sync session is fine for challenge scope |
| Auth / SKIP_AUTH wiring | Out of challenge scope |
| CORS restriction | Out of challenge scope |
| Voice profile retrieval endpoints | Not in README spec for v1 |
| Custom prompt engineering | Simple prompt is sufficient |
| Full error handling coverage | "At least one test" is the bar |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATA-01 | Phase 1 | Pending |
| DATA-02 | Phase 1 | Pending |
| DATA-03 | Phase 1 | Pending |
| DATA-04 | Phase 1 | Pending |
| API-01 | Phase 1 | Pending |
| API-02 | Phase 1 | Pending |
| LLM-01 | Phase 2 | Pending |
| LLM-02 | Phase 2 | Pending |
| LLM-03 | Phase 2 | Pending |
| LLM-04 | Phase 2 | Pending |
| LLM-05 | Phase 2 | Pending |
| API-03 | Phase 2 | Pending |
| API-04 | Phase 2 | Pending |
| API-05 | Phase 2 | Pending |
| API-06 | Phase 2 | Pending |
| TEST-01 | Phase 3 | Pending |
| TEST-02 | Phase 3 | Pending |
| QUAL-01 | Phase 3 | Pending |
| QUAL-02 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 19 total
- Mapped to phases: 19
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-04*
*Last updated: 2026-04-04 after initial definition*
