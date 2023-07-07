# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.enums import ChatType
from aiogram.types import Chat, TelegramObject, User
from babel import Locale, UnknownLocaleError

from gojira import i18n
from gojira.database import Chats, Users


class ACLMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user", None)
        chat: Chat | None = data.get("event_chat", None)

        if user and not user.is_bot:
            userdb = await Users.get_user(user=user)
            if not userdb:
                if user.language_code:
                    try:
                        locale = Locale.parse(user.language_code, sep="-")
                        if str(locale) not in i18n.available_locales:
                            locale = i18n.default_locale
                    except UnknownLocaleError:
                        locale = i18n.default_locale
                else:
                    locale = i18n.default_locale

                if chat and chat.type == ChatType.PRIVATE:
                    userdb = await Users.set_language(user=user, language_code=str(locale))

            data["user"] = userdb

        if chat:
            chatdb = await Chats.get_chat(chat=chat)
            if not chatdb and chat.type in (
                ChatType.GROUP,
                ChatType.SUPERGROUP,
            ):
                chatdb = await Chats.set_language(chat=chat, language_code=i18n.default_locale)

            data["chat"] = chatdb

        return await handler(event, data)
