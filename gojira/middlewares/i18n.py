# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from typing import Any, Dict, Optional, cast

from aiogram.enums import ChatType
from aiogram.types import Chat, TelegramObject, User
from aiogram.utils.i18n import I18nMiddleware
from babel import Locale, UnknownLocaleError

from gojira.database.models import Chats, Users


class MyI18nMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        user: Optional[User] = data.get("event_from_user")
        chat: Optional[Chat] = data.get("event_chat")

        if chat is not None and chat.type == ChatType.PRIVATE:
            obj = user
            objdb = Users
        else:
            obj = chat
            objdb = Chats

        if obj is None:
            return self.i18n.default_locale

        obj = await objdb.get_or_none(id=obj.id)
        if obj is None:
            return self.i18n.default_locale

        if obj.language_code not in self.i18n.available_locales:
            return self.i18n.default_locale

        return cast(str, obj.language_code)
