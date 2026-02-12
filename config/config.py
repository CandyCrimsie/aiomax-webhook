from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    BOT_TOKEN: str
    WEBHOOK_HOST: str
    WEBHOOK_PORT: int
    WEBHOOK_URL: str
    WEBHOOK_SECRET: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra='allow')


config = Config()