# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram.types import Chat

from .base import SqliteConnection


class Chats(SqliteConnection):
    @staticmethod
    async def get_chat(chat: Chat) -> list | str | None:
        sql = "SELECT * FROM chats WHERE id = ?"
        params = (chat.id,)
        r = await Chats._make_request(sql, params, fetch=True, mult=True)
        return r if r else None

    @staticmethod
    async def register_chat(chat: Chat) -> None:
        sql = "INSERT INTO chats (id) VALUES (?)"
        params = (chat.id,)
        await Chats._make_request(sql, params)

    @staticmethod
    async def get_language(chat: Chat) -> list | str | None:
        sql = "SELECT language_code FROM chats WHERE id = ?"
        params = (chat.id,)
        r = await Chats._make_request(sql, params, fetch=True)
        return r[0] if r and r[0] else None

    @staticmethod
    async def set_language(chat: Chat, language_code: str) -> None:
        if await Chats.get_chat(chat):
            sql = "UPDATE chats SET language_code = ? WHERE id = ?"
        else:
            sql = "INSERT INTO chats (id, language_code) VALUES (?, ?)"
        params = (language_code, chat.id)
        await Chats._make_request(sql, params)
