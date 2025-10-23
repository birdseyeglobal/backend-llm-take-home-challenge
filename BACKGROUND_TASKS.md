# Background Task Implementation for Content Analysis

## Overview

The `/analyze_content` endpoint has been converted to use FastAPI BackgroundTasks. Analysis now happens asynchronously in the background, providing immediate API responses while GPT processing occurs.

## What Changed

### 1. Database Model (`app/models.py`)
- Added `status` field: `"pending"`, `"completed"`, or `"failed"`
- Added `error_message` field for failure details
- Made `warmth_score` and `target_demographic` Optional (nullable during pending state)

### 2. Response Schemas (`app/schemas.py`)
- **New**: `AnalysisStatusResponse` - returned immediately when analysis starts
  - `content_id`: int
  - `status`: str
  - `message`: str
- **Updated**: `AnalysisResponse` - now includes status tracking
  - Added `status`: str
  - Added `error_message`: str | None
  - Made `warmth_score` and `target_demographic` nullable

### 3. Repository Layer (`app/repositories.py`)
- **New**: `create_pending_analysis()` - creates analysis record with status="pending"
- **New**: `get_analysis_by_content_id()` - alias for getting analysis
- **New**: `update_to_failed()` - marks analysis as failed with error message
- **Updated**: `create()` - accepts optional `status` parameter
- **Updated**: `update()` - accepts `status` and `error_message` parameters

### 4. Service Layer (`app/services.py`)
- **New**: `start_analysis_background()` - creates pending record and returns immediately
- **Updated**: `analyze_content()` - now updates existing pending record with results
  - Marks analysis as "failed" if any errors occur
  - Updates status to "completed" on success

### 5. Routes (`app/routes.py`)
- **Updated**: `POST /analyze_content` 
  - Returns `AnalysisStatusResponse` immediately
  - Accepts `BackgroundTasks` parameter
  - Adds background task to perform actual analysis
  - Returns status="pending" while processing
- **New**: `GET /analyze_content/{content_id}/status`
  - Check current status of analysis
  - Returns full `AnalysisResponse` with results if completed

### 6. Tests (`tests/test_content_flow.py`)
- **New**: `poll_for_analysis_completion()` helper function
  - Polls status endpoint until analysis completes
  - Configurable max attempts and delay
- **Updated**: All analysis tests now use polling pattern
- **Updated**: Tests check for "pending" status initially
- **Updated**: Tests wait for "completed" status before checking results

## API Usage

### Starting Analysis

```bash
POST /analyze_content
{
  "content_id": 123
}

# Response (immediate):
{
  "content_id": 123,
  "status": "pending",
  "message": "Analysis pending for content 123"
}
```

### Checking Status

```bash
GET /analyze_content/123/status

# Response (while pending):
{
  "content_id": 123,
  "warmth_score": null,
  "target_demographic": null,
  "status": "pending",
  "error_message": null,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}

# Response (when completed):
{
  "content_id": 123,
  "warmth_score": 0.85,
  "target_demographic": "Young professionals...",
  "status": "completed",
  "error_message": null,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:15"
}

# Response (if failed):
{
  "content_id": 123,
  "warmth_score": null,
  "target_demographic": null,
  "status": "failed",
  "error_message": "Content analysis failed: API error...",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:10"
}
```

## Benefits

✅ **Immediate Response**: API responds instantly, no waiting for GPT
✅ **No Timeouts**: Long-running analyses won't cause timeout errors
✅ **Better UX**: Users get feedback immediately
✅ **Graceful Failures**: Failed analyses are tracked with error messages
✅ **Scalability**: Can handle many concurrent analyses

## Migration Notes

### Database Migration Required

You'll need to add the new columns to your database:

```sql
ALTER TABLE content_analysis 
ADD COLUMN status VARCHAR(20) DEFAULT 'pending',
ADD COLUMN error_message TEXT;

ALTER TABLE content_analysis 
ALTER COLUMN warmth_score DROP NOT NULL,
ALTER COLUMN target_demographic DROP NOT NULL;
```

### Existing Data

Existing analyses will need status="completed" set:

```sql
UPDATE content_analysis 
SET status = 'completed' 
WHERE status IS NULL OR status = '';
```

### Frontend Changes Required

Frontend clients must now:
1. Call POST `/analyze_content` to start analysis
2. Poll GET `/analyze_content/{id}/status` to check completion
3. Handle "pending", "completed", and "failed" states

## Testing

Run tests with Docker services running:

```bash
# Start services
docker-compose up -d

# Run tests
pytest tests/test_content_flow.py -v

# Tests will automatically poll for completion
```

## Troubleshooting

### Background task not running
- Check Docker logs: `docker-compose logs -f api`
- Ensure database connection is working
- Look for DEBUG statements in logs

### Analysis stuck in "pending"
- Check if background task crashed
- Look for exceptions in Docker logs
- Analysis should auto-fail after exceptions

### Tests timing out
- Increase polling timeout in `poll_for_analysis_completion()`
- Check if OpenAI API is responding
- Verify API key is valid

