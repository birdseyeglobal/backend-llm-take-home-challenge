import os
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ########################################################################
    # generic settings
    ########################################################################
    API_V1_STR: str = "/api/v1"

    # For local development set to True to skip auth on routes
    SKIP_AUTH: bool = False

    model_config = SettingsConfigDict(
        env_file=None if os.getenv("DISABLE_DOTENV") == "1" else ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    ENV: str = "dev"
    MODE: Literal["production", "development"] = Field(default="development")

    ########################################################################
    # database settings
    ########################################################################
    POSTGRES_HOST: str | None = "localhost"
    POSTGRES_PORT: str | None = "5432"
    POSTGRES_USER: str | None = "postgres"
    POSTGRES_PASSWORD: str | None = "birdseye"
    POSTGRES_DB: str | None = "seo_service"
    SQLALCHEMY_DATABASE_URI: str = ""

    ########################################################################
    # llm settings
    ########################################################################
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    PPLX_API_KEY: str = ""
    PYDANTIC_AI_GATEWAY_API_KEY: str = ""

    OPENAI_RATE_LIMIT: int = 5000
    GEMINI_RATE_LIMIT: int = 7000
    PERPLEXITY_RATE_LIMIT: int = 1000
    ANTHROPIC_RATE_LIMIT: int = 4000

    @model_validator(mode="after")
    def validator(self) -> "Settings":
        self.SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        return self


settings = Settings()
