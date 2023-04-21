from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    database_path: str = "./gojira.sqlite"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


config = Settings()  # type: ignore
