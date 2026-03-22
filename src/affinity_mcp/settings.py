from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    affinity_api_key: str
    read_only: bool = False  # Set READ_ONLY=true to block all write/delete operations


settings = Settings()
