# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram.types import User

from .base import SqliteConnection


class Users(SqliteConnection):
    @staticmethod
    async def get_user(user: User) -> list | str | None:
        sql = "SELECT * FROM users WHERE id = ?"
        params = (user.id,)
        return await Users._make_request(sql, params, fetch=True, mult=True) or None

    @staticmethod
    async def register_user(user: User) -> None:
        sql = "INSERT INTO users (id) VALUES (?)"
        params = (user.id,)
        await Users._make_request(sql, params)

    @staticmethod
    async def get_language(user: User) -> list | str | None:
        sql = "SELECT language_code FROM users WHERE id = ?"
        params = (user.id,)
        return (await Users._make_request(sql, params, fetch=True) or [None])[0]

    @staticmethod
    async def set_language(user: User, language_code: str) -> None:
        sql = "UPDATE users SET language_code = ? WHERE id = ?"
        params = (language_code, user.id)
        if not await Users.get_user(user=user):
            sql = "INSERT INTO users (language_code, id) VALUES (?, ?)"
        await Users._make_request(sql, params)
