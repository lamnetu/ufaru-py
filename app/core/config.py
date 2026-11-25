from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "giga-news-service"
    environment: str = "development"

    # GigaChat — РАЗДЕЛЯЕМ OAuth и API
    gigachat_api_key: str = ""
    gigachat_scope: str = "GIGACHAT_API_PERS"
    gigachat_oauth_url: str = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    gigachat_api_url: str = "https://gigachat.devices.sberbank.ru/api/v1"

    # Для отладки: отключить проверку SSL (в проде = false)
    gigachat_verify_ssl: bool = True

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"


settings = Settings()