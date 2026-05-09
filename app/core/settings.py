from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Company Lens"
    VERSION: str = "0.1.0"
    DATABASE_URL: str = (
        "postgresql://companylens:companylens@localhost:5432/companylens"
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
