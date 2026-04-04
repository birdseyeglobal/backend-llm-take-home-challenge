from uuid import UUID

from fastapi import HTTPException
from pydantic import HttpUrl
from pydantic_ai import Agent
from sqlmodel import Session, func, select

from app.brand.api.schemas import (
    LLM_GATEWAY_LIST,
    BrandGetResponse,
    BrandPostRequest,
    BrandPostResponse,
    VoiceGenerateRequest,
    VoiceProfileLLMResult,
    VoiceProfileResponse,
)
from app.brand.db.models import Brand, VoiceProfile

LLM_DEFAULT_GATEWAY_MODEL = "openai:gpt-5.2"


def _to_gateway_model(llm_model: str) -> str:
    if llm_model in LLM_GATEWAY_LIST:
        return f"gateway/{llm_model}"
    else:
        print("Fallback to default gateway model: ", LLM_DEFAULT_GATEWAY_MODEL)
        return f"gateway/{LLM_DEFAULT_GATEWAY_MODEL}"


class BrandServicer:
    def create_brand(
        self, brand_post_request: BrandPostRequest, session: Session
    ) -> BrandPostResponse:
        brand = Brand(
            url=str(brand_post_request.url) if brand_post_request.url else None,
            docs=brand_post_request.docs,
        )
        session.add(brand)
        session.commit()
        session.refresh(brand)
        return BrandPostResponse(
            id=brand.id,
            url=HttpUrl(brand.url) if brand.url else None,
            docs=brand.docs,
        )

    def get_brand(self, brand_id: UUID, session: Session) -> BrandGetResponse:
        brand = session.get(Brand, brand_id)
        if brand is None:
            raise HTTPException(status_code=404, detail="Brand not found")
        return BrandGetResponse(
            url=HttpUrl(brand.url) if brand.url else None,
            docs=brand.docs,
            id=brand.id,
        )

    def generate_voice_profile(
        self,
        brand_id: UUID,
        request: VoiceGenerateRequest,
        session: Session,
    ) -> VoiceProfileResponse:
        # 1. Check brand exists
        brand = session.get(Brand, brand_id)
        if brand is None:
            raise HTTPException(status_code=404, detail="Brand not found")

        # 2. Compute next version
        max_version = session.exec(
            select(func.max(VoiceProfile.version)).where(
                VoiceProfile.brand_id == brand_id
            )
        ).first()
        next_version = (max_version or 0) + 1

        # 3. Build prompt
        samples_text = "\n\n".join(request.writing_samples)
        prompt = (
            f"Analyze these writing samples and generate a brand voice profile.\n\n"
            f"Writing samples:\n{samples_text}\n\n"
            f"Return metrics on a 0.0-1.0 scale:\n"
            f"- warmth: how warm and friendly the tone is\n"
            f"- seriousness: how serious vs casual the tone is\n"
            f"- technicality: how technical the language is\n"
            f"- formality: how formal vs informal the writing is\n"
            f"- playfulness: how playful and creative the tone is\n\n"
            f"Also provide:\n"
            f"- target_demographic: a short paragraph describing the target audience\n"
            f"- style_guide: 3-5 bullet points as a list of strings\n"
            f"- writing_example: an example sentence or two (3-6 sentences) in this brand's voice"
        )

        # 4. Call LLM via Pydantic AI gateway
        try:
            gateway_model = _to_gateway_model(LLM_DEFAULT_GATEWAY_MODEL)
            agent: Agent[None, VoiceProfileLLMResult] = Agent(
                model=gateway_model,
                output_type=VoiceProfileLLMResult,
            )
            result = agent.run_sync(prompt)
            llm_output = result.output
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

        # 5. Persist
        voice_profile = VoiceProfile(
            brand_id=brand_id,
            version=next_version,
            warmth=llm_output.warmth,
            seriousness=llm_output.seriousness,
            technicality=llm_output.technicality,
            formality=llm_output.formality,
            playfulness=llm_output.playfulness,
            target_demographic=llm_output.target_demographic,
            style_guide=llm_output.style_guide,
            writing_example=llm_output.writing_example,
            llm_model=request.llm_model,
        )
        session.add(voice_profile)
        session.commit()
        session.refresh(voice_profile)

        # 6. Return response
        return VoiceProfileResponse(
            id=voice_profile.id,
            brand_id=voice_profile.brand_id,
            version=voice_profile.version,
            warmth=voice_profile.warmth,
            seriousness=voice_profile.seriousness,
            technicality=voice_profile.technicality,
            formality=voice_profile.formality,
            playfulness=voice_profile.playfulness,
            target_demographic=voice_profile.target_demographic,
            style_guide=voice_profile.style_guide or [],
            writing_example=voice_profile.writing_example,
            llm_model=voice_profile.llm_model,
            created_at=voice_profile.created_at,
        )
