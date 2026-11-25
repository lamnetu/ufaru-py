from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "giga-news-service"
    environment: str = "development"

    gigachat_api_key: str = ""
    gigachat_scope: str = "GIGACHAT_API_PERS"
    gigachat_oauth_url: str = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    gigachat_api_url: str = "https://gigachat.devices.sberbank.ru/api/v1"
    gigachat_verify_ssl: bool = True  # ← тип bool, но из .env придёт строка!

    kafka_bootstrap_servers: str = "localhost:9092"

    @field_validator("gigachat_verify_ssl", mode="before")
    @classmethod
    def parse_bool(cls, v):
        """Конвертируем строки из .env в настоящий bool."""
        if isinstance(v, str):
            return v.lower() not in ("false", "0", "no", "")
        return bool(v)


settings = Settings()
