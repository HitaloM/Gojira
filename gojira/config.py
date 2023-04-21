# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022-2023 Hitalo M. <https://github.com/HitaloM>

from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


config = Settings()  # type: ignore
