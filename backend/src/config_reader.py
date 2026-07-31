from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Config(BaseSettings):
    BOT_TOKEN: SecretStr
    DB_USER: SecretStr
    DB_PASSWORD: SecretStr
    HOST: str
    PORT: int
    DB_NAME: str
    WEBHOOK_URL: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    @property
    def database_url(self) -> str:
        return f'postgresql+asyncpg://{self.DB_USER.get_secret_value()}:{self.DB_PASSWORD.get_secret_value()}@{self.HOST}:{self.PORT}/{self.DB_NAME}'


config = Config()