"""
Repository layer for database operations
"""
from sqlmodel import Session, select
from app.models import TestEntry, UserContent, ContentAnalysis
from typing import Optional
from datetime import datetime


class TestEntryRepository:
    """Repository for TestEntry database operations"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, message: str) -> TestEntry:
        """
        Create a new test entry in the database

        Args:
            message: The message to store

        Returns:
            The created TestEntry with id
        """
        db_entry = TestEntry(message=message)
        self.session.add(db_entry)
        self.session.commit()
        self.session.refresh(db_entry)
        return db_entry


class UserContentRepository:
    """Repository for UserContent database operations"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, content: str) -> UserContent:
        """
        Create a new user content entry in the database

        Args:
            content: The user content to store

        Returns:
            The created UserContent with id
        """
        db_content = UserContent(content=content)
        self.session.add(db_content)
        self.session.commit()
        self.session.refresh(db_content)
        return db_content

    def get_by_id(self, content_id: int) -> Optional[UserContent]:
        """
        Fetch user content by ID

        Args:
            content_id: The ID of the content to retrieve

        Returns:
            UserContent if found, None otherwise
        """
        statement = select(UserContent).where(UserContent.id == content_id)
        return self.session.exec(statement).first()


class ContentAnalysisRepository:
    """Repository for ContentAnalysis database operations"""

    def __init__(self, session: Session):
        self.session = session

    def get_by_content_id(
        self, user_content_id: int
    ) -> Optional[ContentAnalysis]:
        """
        Retrieve analysis by content ID

        Args:
            user_content_id: The user content ID

        Returns:
            ContentAnalysis if found, None otherwise
        """
        statement = select(ContentAnalysis).where(
            ContentAnalysis.user_content_id == user_content_id
        )
        return self.session.exec(statement).first()

    def create(
        self,
        user_content_id: int,
        warmth_score: float,
        target_demographic: str,
        status: str = "completed"
    ) -> ContentAnalysis:
        """
        Create a new content analysis

        Args:
            user_content_id: The ID of the content being analyzed
            warmth_score: The warmth score (0.0-1.0)
            target_demographic: Description of target demographic
            status: Analysis status (default: "completed")

        Returns:
            The created ContentAnalysis
        """
        analysis = ContentAnalysis(
            user_content_id=user_content_id,
            warmth_score=warmth_score,
            target_demographic=target_demographic,
            status=status
        )
        self.session.add(analysis)
        self.session.commit()
        self.session.refresh(analysis)
        return analysis

    def create_pending_analysis(
        self,
        user_content_id: int
    ) -> ContentAnalysis:
        """
        Create a pending content analysis record

        Args:
            user_content_id: The ID of the content being analyzed

        Returns:
            The created ContentAnalysis with status="pending"
        """
        analysis = ContentAnalysis(
            user_content_id=user_content_id,
            status="pending"
        )
        self.session.add(analysis)
        self.session.commit()
        self.session.refresh(analysis)
        return analysis

    def get_analysis_by_content_id(
        self,
        user_content_id: int
    ) -> ContentAnalysis | None:
        """
        Get analysis by content ID (alias for get_by_content_id)

        Args:
            user_content_id: The content ID

        Returns:
            ContentAnalysis if found, None otherwise
        """
        return self.get_by_content_id(user_content_id)

    def update(
        self,
        analysis: ContentAnalysis,
        warmth_score: float,
        target_demographic: str,
        status: str = "completed",
        error_message: str | None = None
    ) -> ContentAnalysis:
        """
        Update an existing content analysis

        Args:
            analysis: The analysis to update
            warmth_score: The new warmth score
            target_demographic: The new demographic description
            status: Analysis status (default: "completed")
            error_message: Error message if failed

        Returns:
            The updated ContentAnalysis
        """
        analysis.warmth_score = warmth_score
        analysis.target_demographic = target_demographic
        analysis.status = status
        analysis.error_message = error_message
        analysis.updated_at = datetime.now()
        self.session.add(analysis)
        self.session.commit()
        self.session.refresh(analysis)
        return analysis

    def update_to_failed(
        self,
        analysis: ContentAnalysis,
        error_message: str
    ) -> ContentAnalysis:
        """
        Mark an analysis as failed

        Args:
            analysis: The analysis to update
            error_message: The error message

        Returns:
            The updated ContentAnalysis
        """
        analysis.status = "failed"
        analysis.error_message = error_message
        analysis.updated_at = datetime.now()
        self.session.add(analysis)
        self.session.commit()
        self.session.refresh(analysis)
        return analysis

    def upsert(
        self,
        user_content_id: int,
        warmth_score: float,
        target_demographic: str
    ) -> ContentAnalysis:
        """
        Create or update analysis (upsert operation)

        Args:
            user_content_id: The ID of the content
            warmth_score: The warmth score
            target_demographic: The demographic description

        Returns:
            The created or updated ContentAnalysis
        """
        existing = self.get_by_content_id(user_content_id)
        if existing:
            return self.update(existing, warmth_score, target_demographic)
        else:
            return self.create(
                user_content_id, warmth_score, target_demographic
            )
