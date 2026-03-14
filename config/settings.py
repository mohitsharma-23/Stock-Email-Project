from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ── LLM ──────────────────────────────────────────
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")

    # ── Gmail ─────────────────────────────────────────
    gmail_sender: str = Field(..., env="GMAIL_SENDER")
    gmail_recipient: str = Field(..., env="GMAIL_RECIPIENT")

    # ── LangSmith (optional — enables tracing/observability) ──
    # langchain_api_key: str = Field(default="", env="LANGCHAIN_API_KEY")
    # langchain_tracing_v2: bool = Field(default=False, env="LANGCHAIN_TRACING_V2")
    # langchain_project: str = Field(default="stock-news-agent", env="LANGCHAIN_PROJECT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()