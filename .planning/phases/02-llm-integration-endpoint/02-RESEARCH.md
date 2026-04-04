# Phase 2: LLM Integration & Endpoint - Research

**Researched:** 2026-04-04
**Domain:** Pydantic AI gateway, FastAPI routing, SQLModel aggregates, mypy strict
**Confidence:** HIGH (core APIs), MEDIUM (mypy edge cases)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Use **Pydantic AI** (`pydantic-ai`) for LLM integration. Add via `poetry add pydantic-ai`.
- **D-02:** Use the **Pydantic AI gateway** (`https://ai.pydantic.dev/gateway/`) as the API backend — not direct OpenAI/Anthropic/Gemini APIs.
- **D-03:** Gateway API key stored in new env var `PYDANTIC_AI_GATEWAY_API_KEY`. Add this field to `Settings` in `app/base/config.py` as `pydantic_ai_gateway_api_key: str`.
- **D-04:** Route by model name prefix: `"gpt-*"` → OpenAI provider, `"claude-*"` → Anthropic provider, `"gemini-*"` → Gemini provider. The Pydantic AI gateway handles the actual routing — the servicer sets the model string accordingly.
- **D-05:** The `llm_model` field from the request (e.g., `"gpt-4"`) is passed directly to the Pydantic AI agent as the model identifier and also stored in the `VoiceProfile.llm_model` field.
- **D-06:** Define a separate `VoiceProfileLLMResult` Pydantic BaseModel (in `app/brand/api/schemas.py`) containing only the LLM-generated fields: `warmth`, `seriousness`, `technicality`, `formality`, `playfulness` (all `float` with `ge=0.0, le=1.0`), `target_demographic: str`, `style_guide: list[str]`, `writing_example: str`. This is the Pydantic AI result type.
- **D-07:** After the LLM call, the servicer constructs a `VoiceProfile` model from the `VoiceProfileLLMResult` fields plus `brand_id`, `version`, `llm_model`, and timestamps.
- **D-08:** Each `generate` call creates a **new** `VoiceProfile` record — never updates existing ones. Profiles are immutable history.
- **D-09:** Version is computed as `MAX(version) + 1` for the given brand. Returns `1` if no profiles exist yet.
- **D-10:** Use SQLModel `select()` + `func.max()` for the version query, consistent with existing SQLModel session usage.
- **D-11:** New method `generate_voice_profile(request: VoiceGenerateRequest, brand_id: UUID, session: Session) -> VoiceProfileResponse` on `BrandServicer`.
- **D-12:** Endpoint path: `POST /brands/{brand_id}/voices:generate` — added to `app/brand/api/routes.py`. Servicer instantiated inline: `servicer = BrandServicer()`.
- **D-13:** 404 if brand not found: `session.get(Brand, brand_id)` → `HTTPException(status_code=404, detail="Brand not found")` if None.
- **D-14:** Wrap LLM call in `try/except Exception as e:` → `raise HTTPException(status_code=500, detail=str(e))`.

### Claude's Discretion

- Exact prompt text (simple, clear prompt per README recommendation)
- Pydantic AI agent initialization and configuration details
- Whether to use `asyncio.run()` or sync agent call (prefer sync to match existing sync route handlers)

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LLM-01 | LLM framework dependency added to pyproject.toml | pydantic-ai 1.77.0 via `poetry add pydantic-ai` |
| LLM-02 | LLM called with writing samples, returns structured voice profile data | Agent(model, output_type=VoiceProfileLLMResult).run_sync(prompt) |
| LLM-03 | Float metrics (warmth, seriousness, technicality, formality, playfulness) constrained 0–1 | Pydantic Field(ge=0.0, le=1.0) on VoiceProfileLLMResult enforces this |
| LLM-04 | style_guide returned as list of 3–5 bullet strings | Prompt instruction; `style_guide: list[str]` in VoiceProfileLLMResult |
| LLM-05 | writing_example returned as 3–6 sentences | Prompt instruction; `writing_example: str` in VoiceProfileLLMResult |
| API-03 | POST endpoint registered and reachable | `@router.post("/{brand_id}/voices:generate")` — colon in path valid in Starlette 0.49.3 |
| API-04 | Returns 404 if brand_id does not exist | `session.get(Brand, brand_id)` → HTTPException(404) — matches existing pattern |
| API-05 | Returns 422 for invalid/missing request body fields | FastAPI auto-validates VoiceGenerateRequest via Pydantic |
| API-06 | version auto-increments per brand (first = 1, second = 2, etc.) | `func.max(VoiceProfile.version)` query + `or 0` + `+ 1` |
</phase_requirements>

---

## Summary

Phase 2 installs `pydantic-ai`, wires a new `generate_voice_profile()` method on `BrandServicer`, and registers `POST /brands/{brand_id}/voices:generate`. All five research areas have been verified against official documentation.

**Pydantic AI gateway** is the correct integration point. The model string must be prefixed with `gateway/<provider>:` when calling the Agent — so the servicer must transform the raw `llm_model` from the request (e.g., `"gpt-4"`) into the gateway format (e.g., `"gateway/openai:gpt-4"`) before passing it to the Agent. The `PYDANTIC_AI_GATEWAY_API_KEY` environment variable is automatically picked up; no explicit key-passing code is required unless runtime override is needed.

**FastAPI colon paths** are fully supported. The literal colon in `/{brand_id}/voices:generate` was a Starlette bug fixed in 0.20.2. The project's locked Starlette is 0.49.3, so this is a non-issue.

**SQLModel `func.max`** works with `session.exec()` but returns `int | None` (None when no rows exist). The correct pattern is `.first()` (not `.one()`) to avoid `NoResultFound` on empty tables. For mypy strict mode, `session.exec()` on aggregate queries requires a `# type: ignore[arg-type]` comment due to a known SQLModel/mypy limitation with `func.*` column expressions.

**Primary recommendation:** Use `Agent(model_string, output_type=VoiceProfileLLMResult)` with `run_sync(prompt)` for the synchronous LLM call. Transform `llm_model` → gateway model string in the servicer via a simple prefix map. Use `session.exec(...).first() or 0` for version computation.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pydantic-ai | 1.77.0 (latest) | LLM agent framework with structured output | Locked in D-01; official Pydantic project; native gateway support |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pydantic-ai.providers.gateway | (bundled) | Gateway provider for explicit key injection | Only if key cannot be set in env at startup |
| sqlalchemy.func | (via sqlmodel) | Aggregate queries (func.max) | Version computation query |

**Installation:**
```bash
poetry add pydantic-ai
```

**Version verification (done):**
`pydantic-ai` latest on PyPI as of 2026-04-04: **1.77.0** (Python >=3.10)

---

## Architecture Patterns

### Pattern 1: Pydantic AI Gateway Agent — Simple Form

**What:** Create an Agent with a gateway model string and a structured output type. The `PYDANTIC_AI_GATEWAY_API_KEY` env var is auto-detected.

**When to use:** Any sync servicer method calling the gateway.

**Model string transformation (critical):** The request carries a bare model name (e.g., `"gpt-4"`). The gateway expects `"gateway/openai:gpt-4"`. The servicer must prefix-map before calling the Agent.

```python
# Source: https://ai.pydantic.dev/gateway/
from pydantic_ai import Agent
from app.brand.api.schemas import VoiceProfileLLMResult

def _to_gateway_model(llm_model: str) -> str:
    if llm_model.startswith("gpt-"):
        return f"gateway/openai:{llm_model}"
    elif llm_model.startswith("claude-"):
        return f"gateway/anthropic:{llm_model}"
    elif llm_model.startswith("gemini-"):
        return f"gateway/google-vertex:{llm_model}"
    else:
        return llm_model  # pass through unknown prefixes

agent = Agent(
    _to_gateway_model(request.llm_model),
    output_type=VoiceProfileLLMResult,
)
result = agent.run_sync(prompt)
llm_result = result.output  # type: VoiceProfileLLMResult
```

### Pattern 2: Pydantic AI Gateway Agent — Explicit Key

**What:** Pass the API key programmatically instead of via environment variable.

**When to use:** When `settings.pydantic_ai_gateway_api_key` is loaded from the database or injected at request time (D-03 uses env var, so this is the fallback if runtime injection is needed).

```python
# Source: https://ai.pydantic.dev/api/providers/
from pydantic_ai.providers.gateway import gateway_provider
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai import Agent

provider = gateway_provider("openai", api_key=settings.pydantic_ai_gateway_api_key)
model = OpenAIChatModel("gpt-4", provider=provider)
agent = Agent(model, output_type=VoiceProfileLLMResult)
```

**Note:** The simple form (Pattern 1) is preferred for this phase since D-03 specifies env var storage. The env var `PYDANTIC_AI_GATEWAY_API_KEY` is automatically read by the gateway when you use the `gateway/...` model string prefix.

### Pattern 3: VoiceProfileLLMResult Structured Output Type

**What:** Pydantic BaseModel as the Agent output type. Pydantic AI uses tool-calling / structured output to coerce the LLM response into this model.

```python
# Source: https://ai.pydantic.dev/output/
from pydantic import BaseModel, Field

class VoiceProfileLLMResult(BaseModel):
    warmth: float = Field(ge=0.0, le=1.0)
    seriousness: float = Field(ge=0.0, le=1.0)
    technicality: float = Field(ge=0.0, le=1.0)
    formality: float = Field(ge=0.0, le=1.0)
    playfulness: float = Field(ge=0.0, le=1.0)
    target_demographic: str
    style_guide: list[str]
    writing_example: str
```

The `result.output` attribute is typed as `VoiceProfileLLMResult` — no casting needed.

### Pattern 4: SQLModel func.max Version Query

**What:** Compute the next version number with MAX aggregate.

**When to use:** At the start of `generate_voice_profile()` before creating the new record.

```python
# Source: https://github.com/fastapi/sqlmodel/discussions/1465
from sqlmodel import select, func, col
from app.brand.db.models import VoiceProfile

max_version = session.exec(  # type: ignore[arg-type]
    select(func.max(col(VoiceProfile.version))).where(
        VoiceProfile.brand_id == brand_id
    )
).first()
next_version = (max_version or 0) + 1
```

**Critical:** Use `.first()` not `.one()`. When no profiles exist, `.one()` raises `sqlalchemy.exc.NoResultFound`. `.first()` returns `None`, which `or 0` handles. The `# type: ignore[arg-type]` is required because mypy strict cannot infer the type of `func.max(col(...))` expressions (known SQLModel limitation).

### Pattern 5: Route with Colon in Path

**What:** FastAPI/Starlette path with literal colon, per Google AIP-136 custom method convention.

```python
# Source: https://github.com/Kludex/starlette/issues/1674 (fixed in 0.20.2)
@router.post("/{brand_id}/voices:generate")
def generate_voice_profile(
    brand_id: UUID,
    request: VoiceGenerateRequest,
    session: Annotated[Session, Depends(get_session)],
) -> VoiceProfileResponse:
    servicer = BrandServicer()
    return servicer.generate_voice_profile(request, brand_id, session)
```

**Starlette 0.49.3** (locked in poetry.lock) is far above the 0.20.2 fix threshold — colon paths work without any workaround.

### Pattern 6: Complete generate_voice_profile() Method Skeleton

Combining all patterns:

```python
def generate_voice_profile(
    self,
    request: VoiceGenerateRequest,
    brand_id: UUID,
    session: Session,
) -> VoiceProfileResponse:
    # 1. Brand existence check (D-13)
    brand = session.get(Brand, brand_id)
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")

    # 2. Compute next version (D-09, D-10)
    max_version = session.exec(  # type: ignore[arg-type]
        select(func.max(col(VoiceProfile.version))).where(
            VoiceProfile.brand_id == brand_id
        )
    ).first()
    next_version = (max_version or 0) + 1

    # 3. Build prompt
    samples_text = "\n".join(
        f"- {s}" for s in request.writing_samples
    )
    prompt = (
        f"Analyze these writing samples and determine the brand voice profile:\n"
        f"{samples_text}\n\n"
        f"Return metrics on a 0-1 scale: warmth, seriousness, technicality, "
        f"formality, playfulness. Also provide: target_demographic (short paragraph), "
        f"style_guide (list of 3-5 bullet strings), writing_example (3-6 sentences)."
    )

    # 4. Call LLM (D-02, D-04, D-05, D-14)
    gateway_model = _to_gateway_model(request.llm_model)
    agent: Agent[None, VoiceProfileLLMResult] = Agent(
        gateway_model, output_type=VoiceProfileLLMResult
    )
    try:
        result = agent.run_sync(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    llm_result = result.output

    # 5. Persist (D-07, D-08)
    profile = VoiceProfile(
        brand_id=brand_id,
        version=next_version,
        llm_model=request.llm_model,
        warmth=llm_result.warmth,
        seriousness=llm_result.seriousness,
        technicality=llm_result.technicality,
        formality=llm_result.formality,
        playfulness=llm_result.playfulness,
        target_demographic=llm_result.target_demographic,
        style_guide=llm_result.style_guide,
        writing_example=llm_result.writing_example,
    )
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return VoiceProfileResponse.model_validate(profile)
```

### Anti-Patterns to Avoid

- **Passing bare `"gpt-4"` to Agent:** The Agent will not know to use the gateway. Always transform via `_to_gateway_model()` first.
- **Using `.one()` on the version query:** Raises `NoResultFound` on a brand with no existing profiles. Use `.first()`.
- **Calling `asyncio.run(agent.run())` in a sync context:** Use `agent.run_sync()` directly to avoid nested event loop issues with FastAPI's sync handlers.
- **Constructing Agent once at module level with a fixed model:** The model varies per request (`request.llm_model`). Construct the Agent inside the servicer method.
- **Storing `pydantic_ai_gateway_api_key` as the key name in UPPER_CASE:** The existing `Settings` class uses both `UPPER_CASE` (env vars) and lowercase field names. Follow the existing pattern for the new field — check whether it should be `PYDANTIC_AI_GATEWAY_API_KEY: str` (UPPER_CASE consistent with LLM keys) or `pydantic_ai_gateway_api_key: str` (D-03 specifies lowercase). D-03 says lowercase, but `pydantic_settings` maps env vars case-insensitively when `case_sensitive=True` is set — this means the env var `PYDANTIC_AI_GATEWAY_API_KEY` WILL map to the field only if the field is named `PYDANTIC_AI_GATEWAY_API_KEY`. See pitfall below.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| LLM structured output | Manual JSON parsing + validation | `Agent(output_type=VoiceProfileLLMResult)` | Pydantic AI handles retries, schema injection, validation |
| Provider routing | Custom HTTP client per provider | Gateway model string prefix | Gateway proxies all providers, zero translation |
| LLM retries | Custom retry loop | Pydantic AI internal retry | Agent retries on malformed output automatically |
| Response validation | Manual `0.0 <= x <= 1.0` checks | `Field(ge=0.0, le=1.0)` on VoiceProfileLLMResult | Pydantic validates at parse time |

---

## Common Pitfalls

### Pitfall 1: Settings Field Name vs. Env Var Name (pydantic_settings case_sensitive)

**What goes wrong:** The Settings class has `case_sensitive=True`. The field `pydantic_ai_gateway_api_key` (lowercase, D-03) will NOT match the env var `PYDANTIC_AI_GATEWAY_API_KEY` because case sensitivity is enabled. The existing LLM keys (`GEMINI_API_KEY`, `OPENAI_API_KEY`) are all UPPER_CASE fields. If D-03's lowercase field name is used literally, the env var must also be lowercase.

**Why it happens:** `pydantic_settings` with `case_sensitive=True` requires exact name matching between field name and env var name.

**How to avoid:** Define the Settings field as `PYDANTIC_AI_GATEWAY_API_KEY: str = ""` (UPPER_CASE, consistent with all other LLM keys in the class). The env var `PYDANTIC_AI_GATEWAY_API_KEY` will then resolve correctly. Reference it as `settings.PYDANTIC_AI_GATEWAY_API_KEY`. If D-03 lowercase naming must be honoured, the `.env` file and environment must use `pydantic_ai_gateway_api_key` (all lowercase).

**Warning signs:** `pydantic_settings.ValidationError` on startup with a missing field, or `settings.pydantic_ai_gateway_api_key` always being empty string despite env var being set.

### Pitfall 2: `.one()` on Empty Version Query

**What goes wrong:** `session.exec(select(func.max(...))).one()` raises `sqlalchemy.exc.NoResultFound` when the brand has no existing profiles.

**Why it happens:** `func.max()` on an empty result set returns a single row with value `NULL`, but SQLModel's `.one()` still expects exactly one non-null row in some versions.

**How to avoid:** Always use `.first()` — returns `None` for empty result. Then `(result or 0) + 1`.

**Warning signs:** `NoResultFound` exception on first `generate` call for a brand.

### Pitfall 3: Agent Constructed at Module Level with Fixed Model

**What goes wrong:** If `agent = Agent("gateway/openai:gpt-4", output_type=VoiceProfileLLMResult)` is a module-level singleton, it cannot accommodate `request.llm_model` varying per call.

**Why it happens:** Developers familiar with LangChain chains may apply the same pattern.

**How to avoid:** Construct the Agent inside `generate_voice_profile()` using the transformed model string for each call. Agent instantiation is lightweight.

### Pitfall 4: Missing `# type: ignore[arg-type]` on func.max Query

**What goes wrong:** `mypy app` fails with a type error on `session.exec(select(func.max(...)))` because SQLModel's type stubs do not recognize `func.max()` column expressions as a valid `select()` argument under strict mode.

**Why it happens:** Known SQLModel/mypy limitation — aggregate function columns have dynamic types that mypy strict cannot infer from the overloads. This is tracked in sqlalchemy/sqlalchemy#9189.

**How to avoid:** Add `# type: ignore[arg-type]` on the `session.exec(` line specifically. This is the accepted workaround; it does not suppress unrelated errors.

### Pitfall 5: mypy and Union output_type

**What goes wrong:** If `output_type` is passed a union type (e.g., `output_type=VoiceProfileLLMResult | str`), mypy raises a type error. This is documented in Pydantic AI docs.

**Why it happens:** PEP-747 is not yet in Python. Union types are not valid `OutputSpec` values in mypy's view.

**How to avoid:** Use a single concrete type for `output_type=VoiceProfileLLMResult`. No union needed for this phase.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| pydantic-ai | LLM calls | Not yet installed | — (PyPI: 1.77.0) | None — must install |
| PYDANTIC_AI_GATEWAY_API_KEY | LLM calls | Not in env (must be configured) | — | Tests can mock agent |
| Starlette colon path support | API-03 | ✓ | 0.49.3 (in poetry.lock) | N/A — already fixed |
| PostgreSQL | VoiceProfile persistence | Must be running per project setup | — | testcontainers for tests |

**Missing dependencies with no fallback:**
- `pydantic-ai` package: must run `poetry add pydantic-ai` before implementation
- `PYDANTIC_AI_GATEWAY_API_KEY`: must be set in `.env` or environment for real LLM calls; tests should mock the agent

**Missing dependencies with fallback:**
- Real LLM API key for manual testing: can defer to Phase 3 test with mocked agent

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `result_type=` parameter | `output_type=` parameter | pydantic-ai ~0.0.20+ | Use `output_type`, not `result_type` — old name causes TypeError |
| `agent.run_sync(prompt).data` | `agent.run_sync(prompt).output` | pydantic-ai 0.0.36+ | Access structured result via `.output`, not `.data` |
| Gateway URL `gateway.pydantic.dev` | `gateway-us.pydantic.dev` / `gateway-eu.pydantic.dev` | 2025 | New regional URLs; env var `PYDANTIC_AI_GATEWAY_BASE_URL` if override needed |
| `session.query(Model).filter(...)` | `session.exec(select(Model).where(...))` | SQLModel 0.0.x | Use SQLModel 2.0-style select; legacy query API deprecated |

**Deprecated/outdated:**
- `result_type` kwarg on Agent: renamed to `output_type`. Using old name raises TypeError.
- `result.data`: renamed to `result.output`. Old attribute no longer exists.

---

## Open Questions

1. **Case sensitivity of `PYDANTIC_AI_GATEWAY_API_KEY` settings field**
   - What we know: `Settings` has `case_sensitive=True`. D-03 says field name is `pydantic_ai_gateway_api_key` (lowercase). All existing LLM key fields are UPPER_CASE.
   - What's unclear: Whether D-03's lowercase naming is intentional or an oversight. With `case_sensitive=True`, the env var must exactly match the field name.
   - Recommendation: Define the field as `PYDANTIC_AI_GATEWAY_API_KEY: str = ""` (UPPER_CASE) for consistency with existing LLM keys and to ensure env var resolution works without friction.

2. **`_to_gateway_model` placement**
   - What we know: The model string transformation (D-04/D-05) is servicer logic.
   - What's unclear: Whether this should be a standalone module-level function or a private staticmethod on `BrandServicer`.
   - Recommendation: Module-level function in `servicer.py` is simplest; no need for a class method since it has no dependency on `self`.

---

## Sources

### Primary (HIGH confidence)
- `https://ai.pydantic.dev/gateway/` — gateway model string format, env var name, regional URLs
- `https://ai.pydantic.dev/api/providers/` — `gateway_provider()` function signature, env var auto-detection
- `https://ai.pydantic.dev/output/` — `output_type` parameter, `AgentRunResult.output` attribute
- `https://ai.pydantic.dev/agents/` — `Agent.__init__` and `run_sync()` signatures
- `https://github.com/Kludex/starlette/issues/1674` — colon in path bug, fixed in Starlette 0.20.2

### Secondary (MEDIUM confidence)
- `https://github.com/fastapi/sqlmodel/discussions/1465` — `func.max` with `session.exec` pattern + `.first()` recommendation
- `https://github.com/fastapi/sqlmodel/issues/450` — mypy aggregate function type inference limitation
- PyPI `https://pypi.org/project/pydantic-ai/` — version 1.77.0 current, Python >=3.10

### Tertiary (LOW confidence — flag for validation)
- WebSearch result re: `result.data` → `result.output` rename: verify against installed version's changelog if needed

---

## Metadata

**Confidence breakdown:**
- Pydantic AI gateway integration: HIGH — verified against official ai.pydantic.dev/gateway and api/providers docs
- Agent output_type API: HIGH — verified against official ai.pydantic.dev/output docs
- FastAPI colon path: HIGH — verified against Starlette issue tracker; 0.49.3 is well past fix
- SQLModel func.max pattern: MEDIUM — verified via SQLModel GitHub discussions; mypy workaround confirmed but exact ignore code may vary
- mypy type: ignore placement: MEDIUM — known issue with multiple sources but specific error code needs confirmation at implementation time

**Research date:** 2026-04-04
**Valid until:** 2026-05-04 (pydantic-ai moves fast; re-verify API names if >30 days elapse)
