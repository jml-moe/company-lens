from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Company Lens"
    VERSION: str = "0.1.0"
    DATABASE_URL: str = "postgresql://companylens:companylens@localhost:5432/companylens"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    LLM_MODEL_FAST: str = ""
    LLM_MODEL_STRONG: str = ""
    TAVILY_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
