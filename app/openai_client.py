"""
OpenAI client for content analysis
"""
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

OPEN_AI_KEY = (
    "sk-proj-BRcmDryU60R3KguvnDlE6zuvFG-Gq1poJmFbgr29fpMsrIB45kFZe-mxXf"
    "28x6rJ8rs4JjfRdbT3BlbkFJhxgtL_cZkovg5uZ9qU6oMXe01BO3PrNSB1kmG1"
    "esmmFFXqv_aC1szZcsk1yrtOMbr6j2sVd0kA"
)
if not OPEN_AI_KEY:
    raise ValueError("OPEN_AI_KEY environment variable is not set")

client = OpenAI(api_key=OPEN_AI_KEY)


class ContentAnalysis(BaseModel):
    """Pydantic model for content analysis response"""
    warmth_score: float = Field(
        description="Warmth score between 0.0 and 1.0",
        ge=0.0,
        le=1.0
    )
    target_demographic: str = Field(
        description="Description of target demographic (2-3 sentences)"
    )


def analyze_content_with_gpt(content: str) -> dict:
    """
    Analyze content using GPT-4 to extract warmth score and
    target demographic

    Args:
        content: The user content to analyze

    Returns:
        Dictionary with 'warmth_score' (float 0.0-1.0) and
        'target_demographic' (string)

    Raises:
        Exception: If OpenAI API call fails
    """
    prompt = f"""Analyze the following content and provide:
1. A warmth score (0.0 to 1.0) measuring how warm, friendly, and \
approachable the content feels
   - 0.0 = Very cold, impersonal, clinical
   - 0.5 = Neutral, balanced tone
   - 1.0 = Extremely warm, friendly, personable

2. A description of the target demographic (2-3 sentences) including \
likely age range, interests, values, and characteristics of the intended \
audience

Content to analyze:
{content}"""

    try:
        print("DEBUG: Making OpenAI API call...")
        print(f"DEBUG: API Key present: {bool(OPEN_AI_KEY)}")
        print(f"DEBUG: Content length: {len(content)}")

        response = client.responses.parse(
            model="gpt-4o-2024-08-06",
            input=[
                {
                    "role": "system",
                    "content": "Extract the content analysis information."
                },
                {"role": "user", "content": prompt}
            ],
            text_format=ContentAnalysis,
        )

        print("DEBUG: OpenAI API call completed successfully")

        analysis = response.output_parsed
        print("DEBUG: Parsed analysis successfully")
        print(f"DEBUG: Warmth score: {analysis.warmth_score}")
        demo_preview = analysis.target_demographic[:50]
        print(f"DEBUG: Target demographic: {demo_preview}...")

        return {
            "warmth_score": analysis.warmth_score,
            "target_demographic": analysis.target_demographic
        }

    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}") from e
