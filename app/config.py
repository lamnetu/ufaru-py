# app/config.py
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- GigaChat ---
    gigachat_credentials: SecretStr = Field(..., description="Authorization key")
    gigachat_scope: str = Field(default="GIGACHAT_API_PERS")  # PERS / B2B / CORP
    gigachat_model: str = Field(default="GigaChat-Plus")
    gigachat_base_url: str = Field(default="https://gigachat.devices.sberbank.ru/api/v1")
    gigachat_verify_ssl_certs: bool = Field(default=False)    # для тестового контура Сбера
    gigachat_timeout: float = Field(default=60.0)

    # --- Сервис ---
    service_name: str = "giga-news-service"
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")   # json | console

    # --- API ---
    api_key: SecretStr = Field(default=SecretStr("change-me"))
    rate_limit_per_minute: int = Field(default=60)
    max_request_text_chars: int = Field(default=20_000)
    default_max_tokens: int = Field(default=2048)
    default_temperature: float = Field(default=0.6)

    # --- Кэш ---
    cache_enabled: bool = Field(default=True)
    cache_ttl_seconds: int = Field(default=3600)
    cache_max_size: int = Field(default=1024)
    redis_url: str | None = Field(default=None)  # redis://localhost:6379/0

    # --- Kafka (заготовка) ---
    kafka_bootstrap_servers: str = Field(default="localhost:9092")
    kafka_topic_out: str = Field(default="news.rewritten")
    kafka_enabled: bool = Field(default=False)

    @field_validator("log_level")
    @classmethod
    def _upper(cls, v: str) -> str:
        return v.upper()


settings = Settings()
