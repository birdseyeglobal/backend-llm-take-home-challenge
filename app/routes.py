"""
API route definitions
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session
from datetime import datetime

from app.database import get_db
from app.schemas import (
    HealthResponse,
    TestResponse,
    TestEntryCreate,
    TestEntryResponse,
    UserContentCreate,
    UserContentResponse,
    AnalyzeContentRequest,
    AnalysisResponse,
    AnalysisStatusResponse
)
from app.services import (
    TestEntryService,
    UserContentService,
    ContentAnalysisService
)
from app.repositories import (
    TestEntryRepository,
    UserContentRepository,
    ContentAnalysisRepository
)

router = APIRouter()


@router.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Brand Voice API",
        "docs": "/docs",
        "health": "/health",
    }


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint

    Returns the current status of the API service.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        message="Service is running",
    )


@router.get("/test", response_model=TestResponse, tags=["Test"])
async def test_endpoint():
    """
    Test endpoint for development

    Returns a simple JSON response that can be used to verify
    the API is working correctly.
    """
    return TestResponse(
        message="Test endpoint is working!",
        timestamp=datetime.now(),
        data={
            "framework": "FastAPI",
            "python_version": "3.11+",
            "features": [
                "Fast",
                "Type-safe",
                "Auto-documented",
            ],
        },
    )


@router.post("/test/db", response_model=TestEntryResponse, tags=["Test"])
async def test_database(
    entry: TestEntryCreate,
    session: Session = Depends(get_db)
):
    """
    Test database connectivity

    Creates a test entry in the database to verify the connection
    is working.
    """
    try:
        repository = TestEntryRepository(session)
        service = TestEntryService(repository)
        return service.create_entry(entry.message)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        ) from e


@router.post(
    "/user_content",
    response_model=UserContentResponse,
    tags=["User Content"]
)
async def create_user_content(
    content: UserContentCreate,
    session: Session = Depends(get_db)
):
    """
    Create user content

    Accepts user-provided content string with validation:
    - Minimum 50 characters
    - Maximum 1000 characters

    Returns the created content with metadata.
    """
    try:
        repository = UserContentRepository(session)
        service = UserContentService(repository)
        return service.create_content(content.content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        ) from e


def _run_analysis_background(content_id: int, db_url: str):
    """
    Helper function to run analysis in background
    Creates a new database session for the background task
    """
    from sqlmodel import create_engine, Session as DBSession
    from app.repositories import (
        UserContentRepository as UCRepository,
        ContentAnalysisRepository as CARepository
    )

    # Create new engine and session for this background task
    engine = create_engine(db_url)
    with DBSession(engine) as session:
        content_repository = UCRepository(session)
        analysis_repository = CARepository(session)
        service = ContentAnalysisService(
            content_repository, analysis_repository
        )
        try:
            service.analyze_content(content_id)
        except Exception as e:
            print(f"Background analysis failed: {str(e)}")


@router.post(
    "/analyze_content",
    response_model=AnalysisStatusResponse,
    tags=["Content Analysis"]
)
async def analyze_content(
    request: AnalyzeContentRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_db)
):
    """
    Start content analysis with GPT (runs in background)

    Immediately returns with status="pending" while analysis happens
    in the background. Use the GET /analyze_content/{content_id}/status
    endpoint to check the status and retrieve results.

    Returns:
    - content_id: The ID of the content being analyzed
    - status: "pending" (analysis is running in background)
    - message: Status message
    """
    try:
        print(f"DEBUG /analyze_content: Starting request for content_id={request.content_id}")
        
        content_repository = UserContentRepository(session)
        print("DEBUG /analyze_content: Created UserContentRepository")
        
        analysis_repository = ContentAnalysisRepository(session)
        print("DEBUG /analyze_content: Created ContentAnalysisRepository")
        
        service = ContentAnalysisService(
            content_repository, analysis_repository
        )
        print("DEBUG /analyze_content: Created ContentAnalysisService")

        # Start analysis (creates pending record)
        print("DEBUG /analyze_content: Calling start_analysis_background()")
        result = service.start_analysis_background(request.content_id)
        print(f"DEBUG /analyze_content: Result status: {result.status}")

        # Only add background task if status is pending
        if result.status == "pending":
            print("DEBUG /analyze_content: Adding background task")
            # Get database URL for background task
            from app.database import engine
            db_url = "postgresql://neondb_owner:npg_2icn8xvqtDOj@ep-soft-wind-a4tl63ev-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
            print(f"DEBUG /analyze_content: DB URL: {db_url}")

            # Add background task
            background_tasks.add_task(
                _run_analysis_background,
                request.content_id,
                db_url
            )
            print("DEBUG /analyze_content: Background task added")

        print("DEBUG /analyze_content: Returning response")
        return AnalysisStatusResponse(
            content_id=result.content_id,
            status=result.status,
            message=f"Analysis {result.status} for content {result.content_id}"
        )
    except ValueError as e:
        # Handle content not found
        print(f"DEBUG /analyze_content: ValueError - {str(e)}")
        print(f"DEBUG /analyze_content: Error type: {type(e).__name__}")
        import traceback
        print(f"DEBUG /analyze_content: Traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        print(f"DEBUG /analyze_content: Exception - {str(e)}")
        print(f"DEBUG /analyze_content: Error type: {type(e).__name__}")
        import traceback
        print(f"DEBUG /analyze_content: Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        ) from e


@router.get(
    "/analyze_content/{content_id}/status",
    response_model=AnalysisResponse,
    tags=["Content Analysis"]
)
async def get_analysis_status(
    content_id: int,
    session: Session = Depends(get_db)
):
    """
    Get the status of a content analysis

    Returns the current status of the analysis along with results
    if completed.

    Status values:
    - "pending": Analysis is still running
    - "completed": Analysis finished successfully
    - "failed": Analysis encountered an error
    """
    try:
        analysis_repository = ContentAnalysisRepository(session)
        analysis = analysis_repository.get_by_content_id(content_id)

        if not analysis:
            raise HTTPException(
                status_code=404,
                detail=f"No analysis found for content {content_id}"
            )

        return AnalysisResponse(
            content_id=analysis.user_content_id,
            warmth_score=analysis.warmth_score,
            target_demographic=analysis.target_demographic,
            status=analysis.status,
            error_message=analysis.error_message,
            created_at=analysis.created_at,
            updated_at=analysis.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        ) from e
