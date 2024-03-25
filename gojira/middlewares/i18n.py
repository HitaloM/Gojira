# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from typing import Any, cast

from aiogram.enums import ChatType
from aiogram.types import Chat, TelegramObject, User
from aiogram.utils.i18n import I18nMiddleware

from gojira.database import Chats, Users


class MyI18nMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: dict[str, Any]) -> str:
        user: User | None = data.get("event_from_user")
        chat: Chat | None = data.get("event_chat")

        if not user or not chat:
            return self.i18n.default_locale

        if chat is not None and chat.type == ChatType.PRIVATE:
            obj = await Users.get_user(user=user)
            language_code = await Users.get_language(user=user)
        else:
            obj = await Chats.get_chat(chat=chat)
            language_code = await Chats.get_language(chat=chat)

        if not obj:
            return self.i18n.default_locale

        if language_code not in self.i18n.available_locales:
            return self.i18n.default_locale

        return cast(str, language_code)
