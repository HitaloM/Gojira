# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.enums import ChatType
from aiogram.types import Chat, TelegramObject, User
from babel import Locale, UnknownLocaleError

from gojira import i18n
from gojira.database.models import Chats, Users


class ACLMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: Optional[User] = data.get("event_from_user")
        chat: Optional[Chat] = data.get("event_chat")

        if user:
            if (userdb := await Users.get_or_none(id=user.id)) is None:
                try:
                    locale = Locale.parse(user.language_code, sep="-")
                    if str(locale) not in i18n.available_locales:
                        locale = i18n.default_locale
                except UnknownLocaleError:
                    locale = i18n.default_locale

                if chat and chat.type == ChatType.PRIVATE:
                    userdb = await Users.create(
                        id=user.id,
                        language_code=str(locale),
                    )

            data["user"] = userdb

        if chat:
            if (chatdb := await Chats.get_or_none(id=chat.id)) is None:
                if chat and chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
                    chatdb = await Chats.create(id=chat.id, language_code=i18n.default_locale)

            data["chat"] = chatdb

        return await handler(event, data)
