"""
Integration tests for the complete content creation and analysis flow
"""
import httpx
import time


def poll_for_analysis_completion(
    api_base_url: str,
    content_id: int,
    max_attempts: int = 30,
    delay: float = 1.0
):
    """
    Poll the analysis status endpoint until completion or failure

    Args:
        api_base_url: Base URL of the API
        content_id: The content ID to check
        max_attempts: Maximum number of polling attempts
        delay: Delay between attempts in seconds

    Returns:
        The final AnalysisResponse data

    Raises:
        TimeoutError: If analysis doesn't complete within max_attempts
    """
    for attempt in range(max_attempts):
        response = httpx.get(
            f"{api_base_url}/analyze_content/{content_id}/status"
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] in ["completed", "failed"]:
                return data
        
        time.sleep(delay)
    
    raise TimeoutError(
        f"Analysis did not complete within {max_attempts * delay} seconds"
    )


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_endpoint(self, api_base_url):
        """Verify health endpoint returns 200 and correct structure"""
        response = httpx.get(f"{api_base_url}/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "message" in data


class TestUserContentCreation:
    """Test user content creation endpoints"""

    def test_create_user_content_success(self, api_base_url):
        """Test successful content creation"""
        content_data = {
            "content": (
                "This is a test content that meets the minimum "
                "character requirement of 50 characters for "
                "validation purposes."
            )
        }

        response = httpx.post(
            f"{api_base_url}/user_content", json=content_data
        )
        assert response.status_code == 200

        data = response.json()
        assert "id" in data
        assert data["content"] == content_data["content"]
        assert "created_at" in data
        assert data["status"] == "success"
        assert data["id"] > 0

    def test_create_content_too_short(self, api_base_url):
        """Test content validation - too short"""
        content_data = {"content": "Too short!"}

        response = httpx.post(
            f"{api_base_url}/user_content", json=content_data
        )
        assert response.status_code == 422

        error_data = response.json()
        assert "detail" in error_data

    def test_create_content_too_long(self, api_base_url, sample_content):
        """Test content validation - too long"""
        content_data = {"content": sample_content["exactly_1000"] + "x"}

        response = httpx.post(
            f"{api_base_url}/user_content", json=content_data
        )
        assert response.status_code == 422

        error_data = response.json()
        assert "detail" in error_data

    def test_create_content_exactly_50_chars(
        self, api_base_url, sample_content
    ):
        """Test content with exactly 50 characters (minimum)"""
        content_data = {"content": sample_content["exactly_50"]}

        response = httpx.post(
            f"{api_base_url}/user_content", json=content_data
        )
        assert response.status_code == 200

        data = response.json()
        assert data["content"] == sample_content["exactly_50"]

    def test_create_content_exactly_1000_chars(
        self, api_base_url, sample_content
    ):
        """Test content with exactly 1000 characters (maximum)"""
        content_data = {"content": sample_content["exactly_1000"]}

        response = httpx.post(
            f"{api_base_url}/user_content", json=content_data
        )
        assert response.status_code == 200

        data = response.json()
        assert data["content"] == sample_content["exactly_1000"]


class TestContentAnalysis:
    """Test content analysis endpoints"""

    def test_analyze_content_success(self, api_base_url):
        """Test successful content analysis with background task"""
        # First create content
        content_data = {
            "content": (
                "Hey there! Welcome to our friendly community where "
                "everyone is valued and supported. We believe in "
                "creating warm, inclusive spaces where people can "
                "connect, share ideas, and grow together."
            )
        }

        create_response = httpx.post(
            f"{api_base_url}/user_content", json=content_data
        )
        assert create_response.status_code == 200
        content_id = create_response.json()["id"]

        # Start analysis (returns immediately with pending status)
        analysis_data = {"content_id": content_id}
        response = httpx.post(
            f"{api_base_url}/analyze_content", json=analysis_data
        )

        assert response.status_code == 200
        start_data = response.json()
        assert start_data["content_id"] == content_id
        assert start_data["status"] in ["pending", "completed"]
        assert "message" in start_data

        # Poll for completion
        data = poll_for_analysis_completion(api_base_url, content_id)

        assert data["content_id"] == content_id
        assert data["status"] == "completed"
        assert "warmth_score" in data
        assert "target_demographic" in data
        assert "created_at" in data
        assert "updated_at" in data

        # Verify warmth_score is in expected range
        assert 0.0 <= data["warmth_score"] <= 1.0
        assert data["warmth_score"] is not None
        assert data["target_demographic"] is not None

    def test_analyze_nonexistent_content(self, api_base_url):
        """Test analyzing content that doesn't exist"""
        analysis_data = {"content_id": 99999}
        response = httpx.post(
            f"{api_base_url}/analyze_content", json=analysis_data
        )

        assert response.status_code == 404

        error_data = response.json()
        assert "Content with id 99999 not found" in error_data["detail"]

    def test_analyze_invalid_content_id(self, api_base_url):
        """Test analyzing with invalid content_id"""
        analysis_data = {"content_id": -1}
        response = httpx.post(
            f"{api_base_url}/analyze_content", json=analysis_data
        )

        assert response.status_code == 422  # Validation error


class TestCompleteFlow:
    """Test the complete user journey"""

    def test_complete_flow_create_and_analyze(self, api_base_url):
        """Test the complete flow: create content -> analyze"""
        # Step 1: Create content
        content_data = {
            "content": (
                "Hey friends! So excited to share this amazing "
                "journey with you all. Your support means the world "
                "to me and I cannot wait to create more incredible "
                "memories together. Sending all the love and positive "
                "vibes your way!"
            )
        }

        create_response = httpx.post(
            f"{api_base_url}/user_content", json=content_data
        )
        assert create_response.status_code == 200
        content_id = create_response.json()["id"]

        # Step 2: Start analysis
        analysis_data = {"content_id": content_id}
        analysis_response = httpx.post(
            f"{api_base_url}/analyze_content", json=analysis_data
        )
        assert analysis_response.status_code == 200

        # Step 3: Wait for completion and get results
        final_data = poll_for_analysis_completion(api_base_url, content_id)
        assert final_data["content_id"] == content_id
        assert final_data["status"] == "completed"
        assert 0.0 <= final_data["warmth_score"] <= 1.0
        assert len(final_data["target_demographic"]) > 0

    def test_reanalysis_returns_existing(self, api_base_url):
        """Test that re-analyzing returns existing analysis status"""
        # Create content
        content_data = {
            "content": (
                "This is a test content for re-analysis. It meets "
                "the minimum character requirement and will be "
                "analyzed multiple times to test the behavior."
            )
        }

        create_response = httpx.post(
            f"{api_base_url}/user_content", json=content_data
        )
        content_id = create_response.json()["id"]

        # First analysis
        analysis_data = {"content_id": content_id}
        first_response = httpx.post(
            f"{api_base_url}/analyze_content", json=analysis_data
        )
        assert first_response.status_code == 200

        # Wait for completion
        first_analysis = poll_for_analysis_completion(
            api_base_url, content_id
        )
        first_created_at = first_analysis["created_at"]

        # Second analysis request (should return existing)
        second_response = httpx.post(
            f"{api_base_url}/analyze_content", json=analysis_data
        )
        assert second_response.status_code == 200
        
        # Check status - should show completed from first analysis
        second_analysis = httpx.get(
            f"{api_base_url}/analyze_content/{content_id}/status"
        ).json()

        # Verify it's the same analysis (same created_at)
        assert second_analysis["created_at"] == first_created_at
        assert second_analysis["status"] == "completed"

    def test_multiple_contents_separate_analyses(self, api_base_url):
        """Test analyzing multiple different contents"""
        # Create first content
        content1_data = {
            "content": (
                "This is the first test content that meets the "
                "minimum character requirement for validation "
                "purposes and will be analyzed separately."
            )
        }

        create1_response = httpx.post(
            f"{api_base_url}/user_content", json=content1_data
        )
        content1_id = create1_response.json()["id"]

        # Create second content
        content2_data = {
            "content": (
                "This is the second test content that also meets "
                "the minimum character requirement for validation "
                "purposes and will be analyzed separately from the "
                "first one."
            )
        }

        create2_response = httpx.post(
            f"{api_base_url}/user_content", json=content2_data
        )
        content2_id = create2_response.json()["id"]

        # Start analysis for both
        analysis1_response = httpx.post(
            f"{api_base_url}/analyze_content",
            json={"content_id": content1_id}
        )
        analysis2_response = httpx.post(
            f"{api_base_url}/analyze_content",
            json={"content_id": content2_id}
        )

        assert analysis1_response.status_code == 200
        assert analysis2_response.status_code == 200

        # Wait for both to complete
        analysis1 = poll_for_analysis_completion(api_base_url, content1_id)
        analysis2 = poll_for_analysis_completion(api_base_url, content2_id)

        # Verify each has its own analysis
        assert analysis1["content_id"] == content1_id
        assert analysis2["content_id"] == content2_id
        assert analysis1["content_id"] != analysis2["content_id"]

        # Both should have valid warmth scores
        assert 0.0 <= analysis1["warmth_score"] <= 1.0
        assert 0.0 <= analysis2["warmth_score"] <= 1.0
        assert analysis1["status"] == "completed"
        assert analysis2["status"] == "completed"


class TestRootEndpoints:
    """Test root and basic endpoints"""

    def test_root_endpoint(self, api_base_url):
        """Test root endpoint"""
        response = httpx.get(f"{api_base_url}/")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "docs" in data
        assert "health" in data

    def test_test_endpoint(self, api_base_url):
        """Test the /test endpoint"""
        response = httpx.get(f"{api_base_url}/test")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "timestamp" in data
        assert "data" in data
        assert "framework" in data["data"]
