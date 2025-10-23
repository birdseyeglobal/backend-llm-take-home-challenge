"""
Test fixtures and configuration
"""
import pytest


@pytest.fixture
def api_base_url():
    """Base URL for the running Docker API service"""
    return "http://localhost:8000"


@pytest.fixture
def sample_content():
    """Sample content for testing"""
    return {
        "warm": (
            "Hey friends! So excited to share this amazing journey with "
            "you all. Your support means the world to me and I cannot "
            "wait to create more incredible memories together. Sending "
            "all the love and positive vibes your way!"
        ),
        "cold": (
            "This document outlines the technical specifications and "
            "requirements for implementation. All stakeholders must "
            "review section 4.2 regarding compliance standards. Failure "
            "to adhere to documented protocols will result in immediate "
            "escalation."
        ),
        "exactly_50": "This is exactly fifty characters long for testing.",
        "exactly_1000": "a" * 1000
    }
