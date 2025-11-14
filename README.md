# Brand Voice API — Live Coding Challenge

**Time window:** 1 hour (live coding session)  
**Pre-interview prep:** You'll receive this repository ~2 days before your interview to familiarize yourself with the codebase, setup, and requirements.

**Primary focus:** backend implementation, typed Python, LLM integration, and code quality.

**Guidelines:** This is a live coding session where you'll implement a brand voice generation endpoint. We've provided a working starter codebase with brands already implemented. Use AI assistance if you'd like—we want to see how you work in a realistic environment. We'll evaluate your problem-solving approach, code quality, testing mindset, and ability to integrate with existing patterns.

---

## 1) Objective

Implement an endpoint that generates a "brand voice profile" for an existing brand using an LLM. The profile should analyze provided writing samples and generate metrics like warmth, seriousness, technicality, formality, and playfulness.

**What's already built:**
- Brand creation and retrieval endpoints (`POST /public/api/brands`, `GET /public/api/brands/{id}`)
- Database models and migrations for brands
- FastAPI application structure with proper layering
- Test infrastructure with pytest

**What you'll build:**
- `POST /public/api/brands/{brand_id}/voices:generate` endpoint
- `VoiceProfile` data model with versioning
- LLM integration to analyze writing samples and generate voice profiles
- Tests for your implementation

---

## 2) Tech Stack

This project uses:

- **Python 3.11** with FastAPI, Pydantic v2, SQLModel
- **Postgres** with Alembic migrations (testcontainers for tests)
- **Pytest** for testing, mypy for type checking, ruff for linting
- **Poetry** for dependency management

You should follow the existing patterns in the codebase for consistency.

---

## 3) Getting Started

### Prerequisites
- Python 3.11
- Poetry (`pip install poetry`)
- Docker (for running tests with Postgres)

### Installation

1. **Install dependencies:**
```bash
poetry install
```

2. **Activate the virtual environment:**
```bash
poetry shell
```

3. **Run the application:**
```bash
./start_service_dev.sh
```

The API will be available at `http://localhost:3070`. View API docs at `http://localhost:3070/docs`.

You can specify a custom port: `./start_service_dev.sh 8000`

### Running Tests

Run all tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app --cov-report=term
```

Run specific test file:
```bash
pytest tests/test_brand.py -v
```

### Static Analysis

**Linting with ruff:**
```bash
ruff check .
ruff format .
```

**Type checking with mypy:**
```bash
mypy app
```

**Run all checks with nox:**
```bash
nox -s ruff    # Linting and formatting
nox -s mypy    # Type checking
nox -s test    # Tests with coverage
```

---

## 4) What You'll Implement

You need to build a voice profile generation system:

- **Generate a "Brand Voice Profile"** using an LLM based on writing samples  
  - **Metrics (floats 0–1):** warmth, seriousness, technicality, formality, playfulness  
  - **Qualitative:** `target_demographic` (short paragraph), `style_guide` (bulleted list), `writing_example` (3–6 sentences)  
  - **Versioned per brand** (`version: int`), immutable histories
- **Store results** in the database with proper migrations
- **Write tests** to verify your implementation

---

## 5) Data Model to Implement

**Brand** (already implemented)
- `id: UUID`, `url: str`, `docs: list[str]`
- `created_at`, `updated_at`

**VoiceProfile** (you need to implement this)
- `id: UUID`, `brand_id: UUID (FK)`, `version: int`
- `warmth: float` (0–1)
- `seriousness: float` (0–1)
- `technicality: float` (0–1)
- `formality: float` (0–1)
- `playfulness: float` (0–1)
- `target_demographic: str`
- `style_guide: list[str]` (stored as JSON)
- `writing_example: str`
- `llm_model: str`
- `created_at`, `updated_at`
- `Unique constraint on (brand_id, version)`

---

## 6) API Endpoint to Implement

**POST `/public/api/brands/{brand_id}/voices:generate`**  

Request body:
```json
{
  "writing_samples": [
    "We believe in building technology that empowers everyone...",
    "Our mission is simple: make complex things accessible..."
  ],
  "llm_model": "gpt-4"
}
```

Response (200):
```json
{
  "id": "uuid",
  "brand_id": "uuid",
  "version": 1,
  "warmth": 0.8,
  "seriousness": 0.6,
  "technicality": 0.4,
  "formality": 0.5,
  "playfulness": 0.7,
  "target_demographic": "Young professionals seeking user-friendly tech solutions...",
  "style_guide": [
    "Use conversational, inclusive language",
    "Emphasize accessibility and empowerment",
    "Balance technical accuracy with approachability"
  ],
  "writing_example": "We're building tools that anyone can use. No technical expertise required—just bring your ideas and we'll help bring them to life.",
  "llm_model": "gpt-4",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error responses:**
- 404: Brand not found
- 422: Validation errors (missing writing_samples, invalid data)

---

## 7) LLM Integration

You'll need to integrate with an LLM to analyze writing samples and generate voice profiles.

**Recommended Approach:**
- Use **LangChain**, **Pydantic AI**, or **Instructor** for LLM integration (or any other framework you prefer)
- These libraries handle structured output, error handling, and retries for you
- Focus on crafting a good prompt and parsing the response into your data model

**Adding dependencies:**
You can add LLM frameworks as needed:
```bash
poetry add langchain langchain-openai
# or
poetry add pydantic-ai
# or
poetry add instructor
```

**Example prompt idea:**
```
Analyze these writing samples and determine the brand's voice profile:
[writing samples]

Return metrics (0-1 scale): warmth, seriousness, technicality, formality, playfulness
Also provide: target demographic, style guide (3-5 bullets), and an example sentence
```

**Testing approach:**
- Mock the LLM calls in tests (most frameworks support this)
- Or use a simple deterministic stub that returns fixed values
- Focus on testing the endpoint logic, validation, and database operations

---

## 8) Implementation Checklist

- [ ] Add LLM framework dependency (`poetry add langchain`/`pydantic-ai`/`instructor`)
- [ ] Create `VoiceProfile` SQLModel in `app/brand/db/models.py`
- [ ] Create Alembic migration for the new table
- [ ] Create Pydantic schemas for request/response in `app/brand/api/schemas.py`
- [ ] Implement voice generation logic using LLM framework (servicer/repository pattern)
- [ ] Add the endpoint to `app/brand/api/routes.py`
- [ ] Write tests for the new endpoint
- [ ] Ensure mypy and ruff pass
- [ ] Handle edge cases (brand not found, validation errors)

---

## 9) Codebase Structure

Understanding the existing patterns will help you implement your solution:

```
app/
├── base/              # Base configuration and shared utilities
│   ├── api/
│   │   ├── routes.py       # Main API router (includes brand router)
│   │   └── dependencies.py # Dependency injection (e.g., get_session)
│   ├── config.py          # Settings and configuration
│   └── db/
│       ├── engine.py      # Database engine setup
│       └── models.py      # Base SQLModel classes
└── brand/             # Brand feature module
    ├── api/
    │   ├── routes.py       # Brand endpoints (you'll add voice endpoint here)
    │   ├── schemas.py      # Pydantic request/response schemas
    │   └── servicer.py     # Business logic layer
    └── db/
        ├── models.py       # Brand SQLModel (add VoiceProfile here)
        └── repository.py   # Database operations
```

---

## 10) Evaluation Criteria

During the live session, we'll assess:

- **Problem-solving approach (35%):** How you break down the problem, what questions you ask, your debugging process
- **Code quality (25%):** Type safety, following existing patterns, clean code practices
- **Implementation (20%):** Getting a working solution with proper validation and error handling
- **Testing mindset (10%):** Writing meaningful tests, thinking about edge cases
- **LLM integration (10%):** Sensible use of LLM frameworks and structured output

**What we're NOT expecting in 1 hour:**
- Perfect, production-ready code
- Custom LLM integration or prompt engineering magic
- Comprehensive test coverage
- Full error handling for every edge case
- Design documents or architectural diagrams

**What we ARE looking for:**
- Clean, well-typed code that follows the existing patterns
- At least one working test
- Thoughtful questions and trade-off discussions
- Ability to debug and iterate
- Practical use of LLM libraries (LangChain, Pydantic AI, etc.)

---

## 11) Tips for Success

**Before the interview:**
1. Clone the repo and get it running locally
2. Run the tests to ensure your environment is set up correctly
3. Explore the existing Brand implementation as a reference
4. Familiarize yourself with SQLModel, FastAPI, and Alembic basics
5. Review LangChain or Pydantic AI documentation for structured output
6. Have an LLM API key ready (OpenAI, Anthropic, etc.) or plan to use mocked responses

**During the session:**
1. Ask clarifying questions—we want to see your thought process
2. Start with the data model and migrations
3. Get a basic endpoint working first, then iterate
4. Use the existing brand code as a reference for patterns
5. Use LangChain/Pydantic AI for LLM calls—don't reinvent the wheel
6. Don't overthink the prompt—a simple, clear prompt is fine
7. Write at least one test to show your testing approach

---

## 12) Example Test Case

Here's an example of what a test might look like (for reference):

```python
def test_generate_voice_profile(
    client: TestClient,
    session: Session,
) -> None:
    # Create a brand first
    brand_response = client.post(
        "/public/api/brands/",
        json={
            "url": "https://example.com",
            "docs": ["https://example.com/docs"],
        },
    )
    brand_id = brand_response.json()["id"]
    
    # Generate voice profile
    voice_response = client.post(
        f"/public/api/brands/{brand_id}/voices:generate",
        json={
            "writing_samples": [
                "We build amazing products for everyone.",
                "Our mission is to empower people through technology."
            ],
            "llm_model": "gpt-4"
        },
    )
    
    assert voice_response.status_code == 200
    voice_data = voice_response.json()
    
    assert voice_data["brand_id"] == brand_id
    assert voice_data["version"] == 1
    assert 0 <= voice_data["warmth"] <= 1
    assert voice_data["target_demographic"]
    assert len(voice_data["style_guide"]) > 0
```

---

## 13) Questions?

If you have any questions about the setup or requirements before your interview, please reach out to your recruiting contact. Good luck!
