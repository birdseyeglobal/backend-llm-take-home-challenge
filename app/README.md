# Brand Voice API - Application Structure

## Architecture Overview

This application follows a clean layered architecture pattern with clear separation of concerns:

```
Routes → Services → Repositories → Database
```

## File Structure

- **`main.py`** - FastAPI application initialization, middleware, and startup/shutdown events
- **`routes.py`** - API endpoint definitions (routes layer)
- **`services.py`** - Business logic layer
- **`repositories.py`** - Database operations layer (data access)
- **`models.py`** - SQLModel database table definitions
- **`schemas.py`** - Pydantic request/response models
- **`database.py`** - Database engine and session management

## Layer Responsibilities

### Routes Layer (`routes.py`)
- Handles HTTP requests and responses
- Input validation via Pydantic schemas
- Dependency injection for database sessions
- Delegates business logic to services

### Service Layer (`services.py`)
- Contains business logic
- Orchestrates operations across repositories
- Returns response schemas
- Independent of HTTP concerns

### Repository Layer (`repositories.py`)
- Direct database operations (CRUD)
- Works with SQLModel database models
- Receives database sessions via dependency injection
- Returns database model instances

### Database Layer (`database.py`)
- Engine configuration
- Session management via `get_db()` dependency
- Table creation utilities

## Dependency Injection Flow

```python
# In routes.py
@router.post("/test/db")
async def test_database(
    entry: TestEntryCreate,
    session: Session = Depends(get_db)  # DB session injected
):
    repository = TestEntryRepository(session)  # Pass to repository
    service = TestEntryService(repository)     # Pass to service
    return service.create_entry(entry.message)
```

## Running the Application

Make sure your `.env` file contains:
```
DATABASE_URL=postgresql://your-neon-connection-string
```

Then start the application:
```bash
docker-compose up
```

## Testing the Database Endpoint

```bash
curl -X POST http://localhost:8000/test/db \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from Neon DB!"}'
```
