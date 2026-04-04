# Phase 2: LLM Integration & Endpoint - Context

**Gathered:** 2026-04-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Install Pydantic AI, implement `BrandServicer.generate_voice_profile()` using the Pydantic AI gateway, wire `POST /public/api/brands/{brand_id}/voices:generate`, and implement auto-versioning with immutable profile history. No retrieval endpoints — generation only.

</domain>

<decisions>
## Implementation Decisions

### LLM Library
- **D-01:** Use **Pydantic AI** (`pydantic-ai`) for LLM integration. Add via `poetry add pydantic-ai`.
- **D-02:** Use the **Pydantic AI gateway** (`https://ai.pydantic.dev/gateway/`) as the API backend — not direct OpenAI/Anthropic/Gemini APIs.
- **D-03:** Gateway API key stored in new env var `PYDANTIC_AI_GATEWAY_API_KEY`. Add this field to `Settings` in `app/base/config.py` as `PYDANTIC_AI_GATEWAY_API_KEY: str = ""` (UPPER_CASE to match all other LLM key fields and the env var name — Settings has `case_sensitive=True` so casing must match).

### LLM Provider Routing
- **D-04:** Route by model name prefix: `"gpt-*"` → OpenAI provider, `"claude-*"` → Anthropic provider, `"gemini-*"` → Gemini provider. The Pydantic AI gateway handles the actual routing — the servicer sets the model string accordingly.
- **D-05:** The `llm_model` field from the request (e.g., `"gpt-4"`) is passed directly to the Pydantic AI agent as the model identifier and also stored in the `VoiceProfile.llm_model` field.

### Structured Output Model
- **D-06:** Define a separate `VoiceProfileLLMResult` Pydantic BaseModel (in `app/brand/api/schemas.py`) containing only the LLM-generated fields: `warmth`, `seriousness`, `technicality`, `formality`, `playfulness` (all `float` with `ge=0.0, le=1.0`), `target_demographic: str`, `style_guide: list[str]`, `writing_example: str`. This is the Pydantic AI result type.
- **D-07:** After the LLM call, the servicer constructs a `VoiceProfile` model from the `VoiceProfileLLMResult` fields plus `brand_id`, `version`, `llm_model`, and timestamps.

### Versioning (Immutable History)
- **D-08:** Each `generate` call creates a **new** `VoiceProfile` record — never updates existing ones. Profiles are immutable history.
- **D-09:** Version is computed as `MAX(version) + 1` for the given brand: `SELECT MAX(VoiceProfile.version) FROM voice_profile WHERE brand_id = ?`. Returns `1` if no profiles exist yet.
- **D-10:** Use SQLModel `select()` + `func.max()` for the version query, consistent with existing SQLModel session usage.

### Endpoint & Servicer
- **D-11:** New method `generate_voice_profile(self, brand_id: UUID, request: VoiceGenerateRequest, session: Session) -> VoiceProfileResponse` on `BrandServicer` (keep single servicer; `brand_id` first because it comes from the path param, `request` second from the body — route calls it as `servicer.generate_voice_profile(brand_id, request, session)`).
- **D-12:** Endpoint path: `POST /brands/{brand_id}/voices:generate` — added to `app/brand/api/routes.py`. Servicer instantiated inline: `servicer = BrandServicer()` (matching existing pattern).
- **D-13:** 404 if brand not found: `session.get(Brand, brand_id)` → `HTTPException(status_code=404, detail="Brand not found")` if None.

### Error Handling
- **D-14:** Wrap LLM call in `try/except Exception as e:` → `raise HTTPException(status_code=500, detail=str(e))`. Pydantic AI handles internal retries; the servicer catches what bubbles up.

### Claude's Discretion
- Exact prompt text (simple, clear prompt per README recommendation)
- Pydantic AI agent initialization and configuration details
- Whether to use `asyncio.run()` or sync agent call (prefer sync to match existing sync route handlers)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Patterns to Follow
- `app/brand/api/servicer.py` — BrandServicer method signature pattern: `(self, request, session) → response`
- `app/brand/api/routes.py` — Route handler pattern: `Annotated[Session, Depends(get_session)]`, inline servicer instantiation
- `app/brand/api/schemas.py` — Pydantic BaseModel schema pattern (Phase 1 adds VoiceGenerateRequest, VoiceProfileResponse — read after Phase 1 is executed)
- `app/brand/db/models.py` — VoiceProfile SQLModel (created in Phase 1)
- `app/base/config.py` — Settings class — add `pydantic_ai_gateway_api_key: str` field

### Spec
- `README.md` §6 (API Endpoint) — Request/response body spec, error codes (404, 422)
- `README.md` §7 (LLM Integration) — Recommended approach, prompt idea
- `.planning/REQUIREMENTS.md` — LLM-01 through API-06 requirements

### External
- Pydantic AI gateway: `https://ai.pydantic.dev/gateway/` — gateway configuration reference

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `BrandServicer.get_brand()` — template for 404 pattern: `session.get(Model, id)` → `HTTPException(404)` if None
- `Depends(get_session)` — shared session dependency, already imported in routes.py
- `settings` singleton from `app/base/config.py` — source for `PYDANTIC_AI_GATEWAY_API_KEY`

### Established Patterns
- Servicer methods are sync, take `(self, request_schema, session: Session) → response_schema`
- Routes instantiate servicer inline: `servicer = BrandServicer()`
- No dependency injection for servicer — keep consistent
- `session.add()` / `session.commit()` / `session.refresh()` for persistence (see `create_brand`)

### Integration Points
- `app/brand/api/routes.py` — add `@router.post("/{brand_id}/voices:generate")` handler
- `app/brand/api/schemas.py` — add `VoiceProfileLLMResult` (LLM output type)
- `app/base/config.py` — add `pydantic_ai_gateway_api_key: str` to Settings

</code_context>

<specifics>
## Specific Ideas

- Use `pydantic-ai` library with the Pydantic AI gateway backend (not direct OpenAI/Anthropic SDKs)
- Gateway API key: `PYDANTIC_AI_GATEWAY_API_KEY` env var → `settings.pydantic_ai_gateway_api_key`
- Version query: `session.exec(select(func.max(VoiceProfile.version)).where(VoiceProfile.brand_id == brand_id)).first() or 0` → `+ 1`
- Endpoint URL pattern: `POST /public/api/brands/{brand_id}/voices:generate` (colon in path per REST action convention)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-llm-integration-endpoint*
*Context gathered: 2026-04-04*
