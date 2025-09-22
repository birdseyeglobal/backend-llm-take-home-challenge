# Brand Voice API — Take-Home Assignment

**Time window:** ~1 week (we’re not tracking hours; please be thoughtful with scope).  

**Primary focus:** backend design & implementation, typed Python, web APIs, persistence, and an LLM integration with tool calling (MCP or custom).

**Guidlines:** Given the time constraint we expect you to use AI to help you co-develop your solution. Your solution should still contain elements that showcase your own skill as an engineer. If you submit a solution that doesn't showcase your abilities in accordance with the rubric, you will not be successful. We chose this problem because of the many ways that an engineer could run with the idea and produce a solution that showcases their skill in a domain that's core to our product offering. Outside of the core objective, everything is open to interpretation. This readme is here to guide your thinking but if you already have some strong ideas for designing a system that meets the core objective, go for it!

---

## 1) Objective

Build a small, well-architected web service that infers and manages a brand’s “voice” (e.g., warmth, seriousness, technicality) and evaluates sample text against that voice. We will evaluate your design, code quality, correctness, tests, and practical engineering judgment.

You’re free to use equivalent technologies, but we list our stack below to indicate our environment and expectations.

---

## 2) Our Stack (for context, not a hard requirement)

We build on:

- Python 3.11, FastAPI, Pydantic v2, SQLModel (+ SQLAlchemy)  
- Postgres (+ Alembic migrations)  
- Pytest, mypy, ruff, tenacity (retries)  
- LLMs via a Ports/Adapters pattern, Responses API or similar, and function/tool calling (or MCP)

You may use another web framework, schema library, or ORM if you prefer. Just document why, and maintain the same quality bar: types, tests, migrations, and clean layering.

---

## 3) What You Will Build

A REST API service that can:

- **Create & retrieve brands**
- **Generate a “Brand Voice Profile”** using an LLM, based on site content and/or writing samples  
  - **Metrics (floats 0–1):** warmth, seriousness, technicality, formality, playfulness  
  - **Qualitative:** `target_demographic` (short paragraph), `style_guide` (bulleted list), `writing_example` (3–6 sentences)  
  - **Versioned per brand** (`version: int`), immutable histories
- **Evaluate a text sample** against a brand voice (return metric deltas and suggestions)
- **Tool calling for content acquisition**
  - **Option A (preferred):** expose a tool (MCP or provider-native function calling) that fetches page text: `fetch_page_text(url) -> str`
  - **Option B:** implement a simple HTTP fetcher inside your service and wire it as a callable tool for the LLM
- **Store, version, and serve** all results in a relational DB with migrations
- **Run in a deterministic “stub” mode** (no network) for CI/tests

_No UI required—OpenAPI and examples are enough._

---

## 4) Minimum Data Model (extend if you like)

You may adapt names/types, but try to preserve semantics.

**Brand**
- `id: UUID`, `name: str`, `canonical_url: str | None`
- `timestamps`

**VoiceProfile**
- `id: UUID`, `brand_id: UUID (FK)`, `version: int (unique per brand)`
- `metrics: dict[str, float]` with keys above (0–1)
- `target_demographic: str`
- `style_guide: list[str]`
- `writing_example: str`
- `llm_model: str`, `source: str` (e.g., `"site"` | `"manual"` | `"mixed"`)
- `timestamps`

**VoiceEvaluation (recommended)**
- `id: UUID`, `brand_id: UUID`, `voice_profile_id: UUID | None`
- `input_text: str`
- `scores: dict[str, float]` (same keys as metrics)
- `suggestions: list[str]`
- `timestamps`

Include constraints where appropriate (e.g., `Unique(brand_id, version)`).

---

## 5) Required API Endpoints

**POST `/brands`**  
Create a brand.

**GET `/brands/{brand_id}`**  
Fetch brand details.

**POST `/brands/{brand_id}/voices:generate`**  
Request body (example):
```json
{
  "inputs": {
    "urls": ["https://acme.example.com/about"],
    "writing_samples": ["We build robots..."]
  },
  "llm_model": "gpt-5-mini"
}
```
Produces a new `VoiceProfile` with `version = previous + 1`.

**GET `/brands/{brand_id}/voices/latest`**

**GET `/brands/{brand_id}/voices/{version}`**

**POST `/brands/{brand_id}/voices/{version}/evaluate`**  
Request body:
```json
{ "text": "Introducing our modular arm with precision ..." }
```
Respond with aligned scores and suggestions.

Return well-formed error responses (e.g., 422 validation, 404 not found).

---

## 6) LLM Integration & Tooling

### 6.1 Port/Adapter Interface (example)

Design a small interface to keep your core logic independent of any vendor:

```python
class LLMPort(Protocol):
    def generate_voice_profile(
        self, *, brand: Brand, site_text: str | None, samples: list[str] | None
    ) -> VoiceProfileData: ...

    def evaluate_text(
        self, *, voice: VoiceProfileData, text: str
    ) -> VoiceEvaluationData: ...
```

Implement at least two adapters:

- **StubLLM (required):** deterministic, no network.  
  Must produce stable outputs for given inputs (e.g., seeded by content hash).  
  Tests and CI use this by default.

- **ProviderLLM (optional to run):** OpenAI/Anthropic/Gemini/etc.  
  Use environment variables for credentials.  
  Add timeouts and retries (e.g., tenacity).

### 6.2 Tool Calling

Expose a tool that the LLM can invoke to fetch page text:

- MCP tool server or provider-native function/tool calling.
- Validate inputs, sanitize HTML, cap payload sizes, and handle timeouts.

---

## 7) Non-Functional Requirements

- **Typing & Style:** Strong typing, mypy clean; ruff clean.  
- **Layering:** Separate domain use-cases from web/ORM/provider details.  
- **Persistence:** Use migrations (Alembic or equivalent).  
- **Resilience:** Timeouts, retries, and useful error handling around LLM & tools.  
- **Determinism:** Tests must pass offline in stub mode, consistently.  
- **Observability:** Clear structured logs; a minimal counter or two is a plus.  
- **Security:** Don’t log secrets; basic input validation; safe fetches.

---

## 8) How to Run & Test

**Local DB**  
Prefer Postgres (Docker Compose is great), but SQLite is acceptable for tests.

**Migrations**  
Provide commands (e.g., `alembic upgrade head`).

**App**  
Run the API server; expose `/docs` for OpenAPI.

**Tests**  
Use StubLLM (no network).  
Include both unit tests (core logic) and integration tests (API + DB).  
Tests should run quickly and deterministically.

**Example commands** (adapt to your project):
```bash
docker compose up -d db
alembic upgrade head
uvicorn app.main:app --reload
pytest -q
```

---

## 9) Deliverables

Source repo with:

- `/app` (or similar) service code  
- `/migrations` (Alembic or equivalent)  
- `/tests` (unit + integration, stub mode)  
- `Dockerfile` and `docker-compose.yml` (or clear local runbook)  
- `README.md` (quickstart + API usage)  
- `DESIGN.md` (1–2 pages; see §11)  
- `pyproject.toml` with linters/formatters/type checking

---

## 10) Evaluation Rubric (weights)

- **Architecture & Design (30%)**  
  Layering, interfaces, testability, versioning model, tool/LLM integration.

- **Correctness & API (20%)**  
  Endpoints behave as specified; OpenAPI is accurate.

- **Data Modeling & Persistence (15%)**  
  Sensible schema, constraints, migrations.

- **Resilience & Reliability (10%)**  
  Timeouts/retries, graceful failures, safe scraping/tool calls.

- **Code Quality (10%)**  
  Readable, typed, maintainable, minimal complexity.

- **Tests (10%)**  
  Useful coverage; deterministic; API + unit tests.

- **DX & Docs (5%)**  
  Clear README and design notes; easy to run.

We’ll also credit strong trade-off discussions in your design doc.

---

## 11) Design Doc (what to include)

In 1–2 pages, please cover:

- Architecture diagram (optional but helpful)  
- Ports/Adapters: how your LLM and tools are abstracted  
- Data model: why the chosen fields & constraints  
- Versioning strategy for voices  
- Failure modes: timeouts, retries, bad inputs, scraping limits  
- Determinism: how tests are kept reproducible  
- If you deviated from our stack, explain why

---

## 12) How to Stand Out

- Thoughtful domain modeling: sensible constraints; defensive SQL; explicit enums for voice metrics  
- Great error ergonomics: structured validation errors, consistent problem responses  
- Idempotency & concurrency: e.g., generating the same voice twice should produce one version unless inputs change (document your choice)  
- Observability: request IDs, log context, minimal timing metrics  
- Security & safety: prompt‑injection‑aware scraping (sanitization), size/time limits, robust tool validation  
- MCP implementation: clean, minimal MCP tool server + client wiring  
- Performance considerations: pagination, stream‑safe reading, reasonable timeouts  
- Polished tests: realistic data builders/fixtures, clear naming, test the “unhappy paths”  
- Extensibility: make it obvious how to add another LLM vendor or tool

---

## 13) Time & Expectations

We don’t track hours. We expect a thoughtful, scope‑aware solution you’re proud to discuss. It’s fine to note deferred items in `DESIGN.md` or TODOs—show us your prioritization.

---

## 14) Submission

Share a GitHub repo (preferred) or a tar/zip.

Include a brief note with:

- How to run  
- Any known gaps  
- Anything you’d like us to focus on during review

---

## 15) FAQ

**Do I have to use FastAPI/Pydantic/SQLModel?**  
No. We prefer them because they’re our stack, but use equivalents if you can meet the same quality bar and document your choices.

**Do I need real LLM credentials?**  
No. StubLLM must be default and used in tests. If you add a live adapter, keep it opt‑in via env vars.

**How complex should the scraper/tool be?**  
Keep it simple: fetch text, sanitize, cap size, handle timeouts. We care more about the interface and resilience than scraping tricks.

**Can I include extra endpoints or features?**  
Sure—just don’t sacrifice quality elsewhere. Document anything nontrivial.

---

## Appendix A — Example Types (Illustrative Only)

```python
class VoiceProfileData(TypedDict):
    metrics: dict[str, float]  # warmth, seriousness, technicality, formality, playfulness
    target_demographic: str
    style_guide: list[str]
    writing_example: str
    llm_model: str
    source: str  # "site" | "manual" | "mixed"

class VoiceEvaluationData(TypedDict):
    scores: dict[str, float]
    suggestions: list[str]
```
