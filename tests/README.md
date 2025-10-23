# Test Suite - Simplified Docker Setup

## Overview

The test suite has been simplified to work directly with your running Docker
services at `http://localhost:8000`. Tests make real HTTP requests and use
the real database.

## Changes Made

### 1. Simplified Dependencies
- **Removed**: FastAPI TestClient, SQLModel test database, mocked fixtures
- **Using**: Only `httpx` for making HTTP requests to the running service
- **Result**: Much simpler test setup with fewer dependencies to manage

### 2. Updated Test Files

#### `tests/conftest.py`
- Contains only 2 simple fixtures:
  - `api_base_url`: Returns `"http://localhost:8000"`
  - `sample_content`: Provides sample test data

#### `tests/test_content_flow.py`
- All tests now use `httpx.get()` and `httpx.post()` instead of TestClient
- Tests hit the real API at `http://localhost:8000`
- No more mocked OpenAI responses (uses real API)
- Tests create actual data in your database

## How to Run Tests

### Prerequisites
1. **Start your Docker services first:**
   ```bash
   docker-compose up -d
   ```

2. **Verify services are running:**
   ```bash
   curl http://localhost:8000/health
   ```

### Run Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_content_flow.py

# Run specific test class
pytest tests/test_content_flow.py::TestHealthEndpoint

# Run specific test
pytest tests/test_content_flow.py::TestHealthEndpoint::test_health_endpoint
```

## Important Notes

### Data Persistence
- ⚠️ **Tests create real data** in your database
- Data persists after tests complete
- Consider clearing test data periodically if needed

### OpenAI API Calls
- Tests now make **real OpenAI API calls** (no mocking)
- This will consume API credits
- Ensure your `.env` file has valid OpenAI API key

### Test Dependencies
- Tests require your Docker services to be running
- If services are down, tests will fail with connection errors
- Make sure `http://localhost:8000` is accessible

## What Each Test Does

### `TestHealthEndpoint`
- Verifies the `/health` endpoint is working

### `TestUserContentCreation`
- Tests content creation with various validations
- Minimum length (50 chars), maximum length (1000 chars)

### `TestContentAnalysis`
- Tests the GPT analysis flow
- Creates content then analyzes it
- Tests error cases (non-existent content, invalid IDs)

### `TestCompleteFlow`
- End-to-end tests of the full user journey
- Tests re-analysis (upsert functionality)
- Tests multiple content pieces

### `TestRootEndpoints`
- Tests root `/` and `/test` endpoints

## Troubleshooting

### Connection Refused
```
httpx.ConnectError: [Errno 61] Connection refused
```
**Solution**: Start Docker services with `docker-compose up -d`

### 404 Errors
**Solution**: Verify the API is running at `http://localhost:8000`

### Test Data Accumulation
**Solution**: Manually clear the database if needed, or connect to the
database and delete test records

