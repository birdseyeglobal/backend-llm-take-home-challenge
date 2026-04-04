# Phase 1: Data Foundation - Context

**Gathered:** 2026-04-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver the VoiceProfile SQLModel, Alembic migration, and Pydantic request/response schemas. No LLM call, no endpoint wiring — pure data layer and schema definitions. All subsequent phases build on this.

</domain>

<decisions>
## Implementation Decisions

### Float Metric Validation
- **D-01:** Add `ge=0.0, le=1.0` constraints to all 5 float fields (warmth, seriousness, technicality, formality, playfulness) in the Pydantic `VoiceProfileResponse` schema. Ensures clean 422 validation errors if LLM returns out-of-range values.
- **D-02:** Apply the same constraints in `VoiceGenerateRequest` if any float fields are user-supplied (not applicable here — floats come from LLM, not request body).

### Brand Model
- **D-03:** Leave the existing `Brand` model untouched. Do NOT add timestamps to Brand or generate a second migration. Focus Phase 1 scope on VoiceProfile only.

### VoiceProfile Delete Behavior
- **D-04:** `brand_id` FK uses `ON DELETE CASCADE`. Deleting a Brand removes all its VoiceProfiles. No orphaned records.

### Response Schema Fields
- **D-05:** `VoiceProfileResponse` includes exactly: `id`, `brand_id`, `version`, `warmth`, `seriousness`, `technicality`, `formality`, `playfulness`, `target_demographic`, `style_guide`, `writing_example`, `llm_model`, `created_at`. No `updated_at` (profiles are immutable, matching README spec).

### Implementation Patterns (from codebase scout)
- **D-06:** `style_guide: list[str]` stored via `Field(sa_type=JSONB)` — same pattern as `Brand.docs`.
- **D-07:** `VoiceProfile` model goes in `app/brand/db/models.py`. Import it in `app/base/db/models.py` for Alembic discovery (follow Brand import pattern).
- **D-08:** Schemas go in `app/brand/api/schemas.py` using `pydantic.BaseModel` (not SQLModel) — matching existing brand schema approach.
- **D-09:** UUID primary key with `default_factory=uuid4`, timestamps with `default_factory=datetime.utcnow` and `sa_column_kwargs={"onupdate": datetime.utcnow}`.

### Claude's Discretion
- Exact Alembic migration naming convention (use `--autogenerate` with descriptive message)
- Whether to use `datetime` or `datetime | None` for timestamps (use non-nullable with defaults)
- Table name: `"voice_profile"` (snake_case of class name)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Patterns to Follow
- `app/brand/db/models.py` — Brand SQLModel pattern: UUID PK, JSONB fields, Field() usage
- `app/brand/api/schemas.py` — Pydantic BaseModel schema pattern (not SQLModel)
- `app/base/db/models.py` — Model registry pattern (import + __all__ + model_rebuild loop)
- `migrations/versions/8d2126d21d1f_init.py` — Existing migration as reference

### Spec
- `README.md` §5 (Data Model) — VoiceProfile field spec
- `README.md` §6 (API Endpoint) — Response body shape (canonical for VoiceProfileResponse)
- `.planning/REQUIREMENTS.md` — DATA-01 through API-02 requirements

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Brand(SQLModel, table=True)` in `app/brand/db/models.py` — direct template for VoiceProfile structure
- `JSONB` import from `sqlalchemy.dialects.postgresql` already in models.py — reuse for style_guide

### Established Patterns
- Schemas use `pydantic.BaseModel` (NOT SQLModel) — all request/response types
- `Field(sa_type=JSONB, nullable=True)` for list fields stored in Postgres
- `UUID = Field(default_factory=uuid4, primary_key=True)`
- Alembic discovers models via `SQLModel.metadata` when models are imported in `app/base/db/models.py`

### Integration Points
- `app/base/db/models.py` — add `from app.brand.db.models import VoiceProfile` and add to `__all__`
- `app/brand/api/schemas.py` — add `VoiceGenerateRequest` and `VoiceProfileResponse`

</code_context>

<specifics>
## Specific Ideas

- VoiceProfile fields must exactly match README §5: `id (UUID)`, `brand_id (UUID FK)`, `version (int)`, `warmth/seriousness/technicality/formality/playfulness (float 0-1)`, `target_demographic (str)`, `style_guide (list[str] JSON)`, `writing_example (str)`, `llm_model (str)`, `created_at`, `updated_at`
- Unique constraint: `UniqueConstraint("brand_id", "version")` on the VoiceProfile table
- `VoiceGenerateRequest` body: `writing_samples: list[str]`, `llm_model: str`

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-data-foundation*
*Context gathered: 2026-04-04*
