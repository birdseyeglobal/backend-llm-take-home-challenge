from unittest.mock import MagicMock, patch
from uuid import UUID

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.brand.api.schemas import VoiceProfileLLMResult
from app.brand.db.models import Brand, VoiceProfile


def _mock_llm_result() -> VoiceProfileLLMResult:
    return VoiceProfileLLMResult(
        warmth=0.7,
        seriousness=0.3,
        technicality=0.5,
        formality=0.4,
        playfulness=0.6,
        target_demographic="Tech-savvy professionals aged 25-40",
        style_guide=["Be concise", "Use active voice", "Avoid jargon"],
        writing_example="Our platform empowers you to build faster.",
    )


def _create_brand(client: TestClient) -> str:
    response = client.post(
        "public/api/brands",
        json={"url": "https://example.com", "docs": ["https://example.com/about"]},
    )
    assert response.status_code == 200
    return str(response.json()["id"])


def test_generate_voice_profile_happy_path(
    client: TestClient,
    session: Session,
) -> None:
    brand_id = _create_brand(client)

    mock_agent_result = MagicMock()
    mock_agent_result.output = _mock_llm_result()

    with patch("app.brand.api.servicer.Agent") as mock_agent_cls:
        mock_agent_instance = MagicMock()
        mock_agent_instance.run_sync.return_value = mock_agent_result
        mock_agent_cls.return_value = mock_agent_instance

        response = client.post(
            f"public/api/brands/{brand_id}/voices:generate",
            json={
                "writing_samples": [
                    "We build great software.",
                    "Our team is passionate.",
                ],
                "llm_model": "gpt-4o",
            },
        )

    assert response.status_code == 200
    data = response.json()

    # All required fields present
    for field in (
        "id",
        "brand_id",
        "version",
        "warmth",
        "seriousness",
        "technicality",
        "formality",
        "playfulness",
        "target_demographic",
        "style_guide",
        "writing_example",
        "llm_model",
        "created_at",
    ):
        assert field in data, f"Missing field: {field}"

    # TEST-02: version == 1 for first profile
    assert data["version"] == 1

    # brand_id and llm_model match
    assert data["brand_id"] == brand_id
    assert data["llm_model"] == "gpt-4o"

    # Float fields are valid 0.0-1.0
    for float_field in (
        "warmth",
        "seriousness",
        "technicality",
        "formality",
        "playfulness",
    ):
        value = data[float_field]
        assert isinstance(value, float), f"{float_field} should be float"
        assert 0.0 <= value <= 1.0, f"{float_field}={value} out of range"

    # style_guide is list[str]
    assert isinstance(data["style_guide"], list)
    for item in data["style_guide"]:
        assert isinstance(item, str)

    # String fields
    assert isinstance(data["target_demographic"], str)
    assert isinstance(data["writing_example"], str)

    # id is a valid UUID
    UUID(data["id"])

    # created_at is non-empty
    assert data["created_at"]

    # Cleanup
    voice_profile = session.get(VoiceProfile, data["id"])
    assert voice_profile is not None
    session.delete(voice_profile)
    brand = session.get(Brand, brand_id)
    assert brand is not None
    session.delete(brand)
    session.commit()


def test_generate_voice_404_unknown_brand(
    client: TestClient,
    session: Session,
) -> None:
    response = client.post(
        "public/api/brands/00000000-0000-0000-0000-000000000000/voices:generate",
        json={"writing_samples": ["sample"], "llm_model": "gpt-4o"},
    )
    assert response.status_code == 404


def test_generate_voice_422_missing_writing_samples(
    client: TestClient,
    session: Session,
) -> None:
    brand_id = _create_brand(client)

    response = client.post(
        f"public/api/brands/{brand_id}/voices:generate",
        json={"llm_model": "gpt-4o"},
    )
    assert response.status_code == 422

    # Cleanup
    brand = session.get(Brand, brand_id)
    assert brand is not None
    session.delete(brand)
    session.commit()
