from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "giga-news-service"
    environment: str = "development"
    gigachat_api_key: str = ""
    gigachat_base_url: str = "https://gigachat.devices.sberbank.ru/api/v1"
    kafka_bootstrap_servers: str = "localhost:9092"

settings = Settings()