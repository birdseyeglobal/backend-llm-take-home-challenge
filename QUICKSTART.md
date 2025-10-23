# FastAPI Server Quick Start

## Installation

1. **Create a virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Running the Server

**Start the development server:**
```bash
uvicorn app.main:app --reload
```

The server will start on `http://localhost:8000`

## Testing the API

### Using curl:

**Root endpoint:**
```bash
curl http://localhost:8000/
```

**Health check:**
```bash
curl http://localhost:8000/health
```

**Test endpoint:**
```bash
curl http://localhost:8000/test
```

### Using your browser:

- **Interactive API docs (Swagger UI):** http://localhost:8000/docs
- **Alternative API docs (ReDoc):** http://localhost:8000/redoc

## Example Response

When you call the test endpoint:
```bash
curl http://localhost:8000/test
```

You should see:
```json
{
  "message": "Test endpoint is working!",
  "timestamp": "2025-10-23T...",
  "data": {
    "framework": "FastAPI",
    "python_version": "3.11+",
    "features": [
      "Fast",
      "Type-safe",
      "Auto-documented"
    ]
  }
}
```

## Next Steps

This skeleton is ready for you to add:
- Brand management endpoints
- Voice profile generation
- Text evaluation
- Database models and migrations
- LLM integration

