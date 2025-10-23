"""
Service layer for business logic
"""
from app.repositories import (
    TestEntryRepository,
    UserContentRepository,
    ContentAnalysisRepository
)
from app.schemas import (
    TestEntryResponse,
    UserContentResponse,
    AnalysisResponse
)
from app.openai_client import analyze_content_with_gpt


class TestEntryService:
    """Service for test entry business logic"""

    def __init__(self, repository: TestEntryRepository):
        self.repository = repository

    def create_entry(self, message: str) -> TestEntryResponse:
        """
        Create a new test entry

        Args:
            message: The message to store

        Returns:
            TestEntryResponse with created entry details
        """
        db_entry = self.repository.create(message)
        return TestEntryResponse(
            id=db_entry.id,
            message=db_entry.message,
            created_at=db_entry.created_at,
            status="success"
        )


class UserContentService:
    """Service for user content business logic"""

    def __init__(self, repository: UserContentRepository):
        self.repository = repository

    def create_content(self, content: str) -> UserContentResponse:
        """
        Create new user content

        Args:
            content: The user content to store

        Returns:
            UserContentResponse with created content details
        """
        db_content = self.repository.create(content)
        return UserContentResponse(
            id=db_content.id,
            content=db_content.content,
            created_at=db_content.created_at,
            status="success"
        )


class ContentAnalysisService:
    """Service for content analysis business logic"""

    def __init__(
        self,
        content_repository: UserContentRepository,
        analysis_repository: ContentAnalysisRepository
    ):
        self.content_repository = content_repository
        self.analysis_repository = analysis_repository

    def start_analysis_background(self, content_id: int) -> AnalysisResponse:
        """
        Start a background analysis by creating a pending record

        Args:
            content_id: The ID of content to analyze

        Returns:
            AnalysisResponse with status="pending"

        Raises:
            ValueError: If content not found or analysis already exists
        """
        # Verify content exists
        content = self.content_repository.get_by_id(content_id)
        if not content:
            raise ValueError(f"Content with id {content_id} not found")

        # Check if analysis already exists
        existing = self.analysis_repository.get_by_content_id(content_id)
        if existing:
            # If already pending or completed, return current status
            return AnalysisResponse(
                content_id=existing.user_content_id,
                warmth_score=existing.warmth_score,
                target_demographic=existing.target_demographic,
                status=existing.status,
                error_message=existing.error_message,
                created_at=existing.created_at,
                updated_at=existing.updated_at
            )

        # Create pending analysis record
        db_analysis = self.analysis_repository.create_pending_analysis(
            content_id
        )

        return AnalysisResponse(
            content_id=db_analysis.user_content_id,
            warmth_score=None,
            target_demographic=None,
            status="pending",
            error_message=None,
            created_at=db_analysis.created_at,
            updated_at=db_analysis.updated_at
        )

    def analyze_content(self, content_id: int) -> AnalysisResponse:
        """
        Analyze content using GPT and update pending record with results
        This method is designed to run as a background task

        Args:
            content_id: The ID of content to analyze

        Returns:
            AnalysisResponse with analysis results

        Raises:
            ValueError: If content not found
            Exception: If OpenAI API fails
        """
        print(f"DEBUG: Starting analyze_content for content_id: {content_id}")

        # Get existing analysis record (should be pending)
        existing_analysis = self.analysis_repository.get_by_content_id(
            content_id
        )
        if not existing_analysis:
            print(
                f"DEBUG: No pending analysis found for "
                f"content_id {content_id}"
            )
            raise ValueError(
                f"No analysis record found for content_id {content_id}"
            )

        # Fetch the content
        print("DEBUG: Fetching content from database...")
        content = self.content_repository.get_by_id(content_id)
        print(f"DEBUG: Content found: {content is not None}")

        if not content:
            print(f"DEBUG: Content not found for id {content_id}")
            # Mark analysis as failed
            self.analysis_repository.update_to_failed(
                existing_analysis,
                f"Content with id {content_id} not found"
            )
            raise ValueError(f"Content with id {content_id} not found")

        print(f"DEBUG: Content to analyze: {content.content[:100]}...")

        # Analyze with GPT
        print("DEBUG: Starting GPT analysis...")
        try:
            analysis_result = analyze_content_with_gpt(content.content)
            print("DEBUG: GPT analysis completed successfully")
            result_keys = list(analysis_result.keys())
            print(f"DEBUG: Analysis result keys: {result_keys}")
            warmth = analysis_result.get('warmth_score')
            print(f"DEBUG: Warmth score: {warmth}")
            demo = analysis_result.get('target_demographic', '')[:50]
            print(f"DEBUG: Target demographic: {demo}...")
        except Exception as e:
            print(f"DEBUG: GPT analysis failed with error: {str(e)}")
            print(f"DEBUG: Error type: {type(e).__name__}")
            # Mark analysis as failed
            self.analysis_repository.update_to_failed(
                existing_analysis,
                f"Content analysis failed: {str(e)}"
            )
            raise Exception(f"Content analysis failed: {str(e)}") from e

        # Update analysis with results
        print("DEBUG: Saving analysis to database...")
        try:
            db_analysis = self.analysis_repository.update(
                analysis=existing_analysis,
                warmth_score=analysis_result["warmth_score"],
                target_demographic=analysis_result["target_demographic"],
                status="completed"
            )
            print("DEBUG: Analysis saved to database successfully")
        except Exception as e:
            print(f"DEBUG: Database save failed with error: {str(e)}")
            print(f"DEBUG: Error type: {type(e).__name__}")
            # Mark analysis as failed
            self.analysis_repository.update_to_failed(
                existing_analysis,
                f"Failed to save analysis: {str(e)}"
            )
            raise Exception(
                f"Failed to save analysis to database: {str(e)}"
            ) from e

        return AnalysisResponse(
            content_id=db_analysis.user_content_id,
            warmth_score=db_analysis.warmth_score,
            target_demographic=db_analysis.target_demographic,
            status=db_analysis.status,
            error_message=db_analysis.error_message,
            created_at=db_analysis.created_at,
            updated_at=db_analysis.updated_at
        )
